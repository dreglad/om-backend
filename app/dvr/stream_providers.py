from datetime import timedelta
from functools import partial
from itertools import groupby
import json
import logging
from operator import itemgetter, methodcaller
from posixpath import join
import random
import time
from urllib.parse import urljoin

from cacheback.base import Job as CacheJob
from cacheback.decorators import cacheback
from django.core.cache import caches
from django.utils.functional import cached_property
from django.utils.text import slugify
import requests

logger = logging.getLogger('default')


class StreamProvider(object):

    def __init__(self, obj, metadata, *args, **kwargs):
        #logger.debug('StreamProvider __init__ for obj: {}'.format(obj))
        self.obj = obj
        self.metadata = metadata
        self.cache = caches['stream_providers']

    def _get_cache_key(self, key):
        return '{}-{}-{}'.format(self.__class__.__name__, self.obj.__class__.__name__, key)

    def get_or_set_cache(self, key, value, timeout=None):
        # logger.debug('get_or_set_cache with key: {}'.format(key))
        return self.cache.get_or_set(self._get_cache_key(key), value, timeout)

    def delete_cache(self, key):
        return self.cache.delete(self._get_cache_key(key))


class WowzaStreamingEngineStreamProvider(StreamProvider):

    def __init__(self, obj, metadata):
        super(WowzaStreamingEngineStreamProvider, self).__init__(obj, metadata)
        self.wowza_api_url = urljoin(
            metadata['wseApiUrl'], join(
                '/v2/servers/_defaultServer_/vhosts/_defaultVHost_/applications',
                metadata['wseApplication'],
                'instances/_definst_'
            )
        )

    def get_data(self):
        stream_stores = self.get_or_set_cache('stores', self.retrieve_stores, 10)
        stores = [v for k, v in stream_stores.items() if k.find('1080p') != -1][0]
        # stores2 = next(iter(stream_stores.values()))
        current_store = stores[0]

        current_details = StoreDetailsCacheJob().get(current_store, is_current=True)
        if current_details:
            current_details = json.loads(current_details)
            current_details = {
                prop: current_details['DvrConverterStore'][prop]
                for prop in ('dvrStoreName', 'utcStart', 'utcEnd')
            }            

        details = [current_details]
        for store in stores[1:]:
            try:
                store_details = StoreDetailsCacheJob().get(store, is_current=False)
                print('son', store_details)
                if store_details:
                    store_details = json.loads(store_details)['DvrConverterStore']
                    if store_details['utcStart'] and store_details['utcEnd']:
                        logger.info('Appending details data: {}'.format(store_details))
                        details.append({
                            prop: store_details[prop]
                            for prop in ('dvrStoreName', 'utcStart', 'utcEnd')
                    })
            except:
                logger.error('Error while parsing store details')
            if len(details) > 10:
                break

        return {
            'stores': stream_stores,
            'current_store_details': current_details,
            'store_details': details,
        }


    def request_conversion(self, conv):
        logger.info('Requesting new conversion')

        # filename = '{}-{}-{}.mp4'.format(self.obj.slug, slugify(start), slugify(duration))
        filename = '{}.mp4'.format(conv.pk)
        params = {
            'dvrConverterStartTime': int(conv.start.timestamp() * 1000),
            'dvrConverterDuration': int(conv.duration.total_seconds() * 1000),
            'dvrConverterOutputFilename': filename,
            'dvrConverterStoreList': conv.dvr_store.replace('240p', '1080p')
        }
        try:
            r = requests.put(join(self.wowza_api_url, 'dvrstores/actions/expire'))
            r = requests.put(join(self.wowza_api_url, 'dvrstores/actions/convert'),
                             params=params, headers={'Accept': 'application/json'})
            result = json.loads(r.text)
            logger.info('Received request conversion to {} with response: {}'.format(r.url, result))

            if not result.get('success'):
                logger.warning('Provider rejected conversion: {}'.format(result))
                return {'success': False, 'message': result.get('message')}
        except:
            logger.error('Error while requesting a conversion')
            return {'success': False, 'message': 'Error while requesting conversion'}

        return {'success': result.get('success'), 'message': result.get('message')}

    def retreive_groupconversions(self):
        try:
            r = requests.get(join(self.wowza_api_url, 'dvrstores'), headers={'Accept': 'application/json'})
            return json.loads(r.text)['groupConversionStatusList']
        except:
            logger.error('Error while requesting dvrstore list while retrieving groupconversions')
            return []

    def query_conversion(self, ref, conv):
        if ref: id = ref.split('ID:')[-1]
        group_conversions = self.get_or_set_cache('groupconversions', self.retreive_groupconversions, 5)
        try:
            status = next(item['conversionStatusList'][0] for item in group_conversions if item["id"] == int(id))
        except:
            return False

        if status.get('state') == 'SUCCESSFUL':
            return {'status': 'SUCCESS', 'progress': 1}
        if status.get('state') == 'FAILURE':
            return {'status': 'FAILURE'}
        if status.get('state') == 'RUNNING':
            progress = timedelta(milliseconds=status['fileDuration']).total_seconds() / float(conv.duration.total_seconds())
            return {'status': 'STARTED', 'progress': progress}

        # retrieve_store_details(['groupConversionStatusList'])
        # partial(retrieve_store_details, current_store),
        # try:
        #     r = requests.get(
        #         join(self.wowza_api_url, 'dvrstores/actions/convert'),
        #         headers={'Accept': 'application/json'})
        #     result = json.loads(r.text)
        # except Exception as e:
        #     raise


    def retrieve_stores(self):
        logger.info('Retrieving stores from provider for obj: {}'.format(self.obj))
        stores = {}
        try:
            r = requests.get(join(self.wowza_api_url, 'dvrstores'),
                            headers={'Accept': 'application/json'})
            data = json.loads(r.text)
            stores = sorted([
                {'name': s['name'], 'url': urljoin(self.wowza_api_url, s['location'])}
                for s in data['dvrconverterstoresummary']
                if s['name'].startswith(self.metadata['wseStream'])
            ], key=lambda s: int(s['name'].rsplit('.').pop()), reverse=True)

            sort_key = lambda s: int(s['name'].rsplit('.', 1)[0].replace(self.metadata['wseStream'], '').strip('_p'))
            stores = sorted(stores, key=sort_key, reverse=True)
            group_key = lambda s: s['name'].rsplit('.', 1)[0]
            stores = {k: list(v)[:30] for k, v in groupby(stores, key=group_key)}
        except:
            logger.error("Error while retrieving data from provider: {}")
        return stores


class StoreDetailsCacheJob(CacheJob):

    def fetch(self, store, is_current=False):
        logger.info('Retrieving store details for store: {}'.format(store))
        data = {}
        try:
            r = requests.get(store['url'], headers={'Accept': 'application/json'})
            r.raise_for_status()
            logger.debug('Data retrieved: {}'.format(r.text))
        except:
            logger.error("Error while retrieving store details from provider: {}".format(e))
            return
        return r.text

    def expiry(self, store_url, is_current=False):
        now = time.time()
        if is_current:
            return now + 60
        else:
            return now + 120 + random.randint(0, 120)

    def should_missing_item_be_fetched_synchronously(self, *args, **kwargs):
        return True # kwargs.get('is_current')

    def should_stale_item_be_fetched_synchronously(self, *args, **kwargs):
        return True # kwargs.get('is_current')


# def soft_retrieve_store_details(store):
#     logger.info('Retrieving store details for store: {}'.format(store))
#     data = {}
#     try:
#         r = requests.get(store['url'], headers={'Accept': 'application/json'})
#         r.raise_for_status()
#         # data = json.loads(r.text)
#     except:
#         logger.error("Error while retrieving store details from provider: {}".format(e))
#     print(r.text)
#     return r.text
# @cacheback(fetch_on_miss=True, lifetime=30)
# def retrieve_store_details(store):
#     logger.info('Retrieving store details for store: {}'.format(store))
#     data = {}
#     try:
#         r = requests.get(store['url'], headers={'Accept': 'application/json'})
#         r.raise_for_status()
#         # data = json.loads(r.text)
#     except:
#         logger.Error("Error while retrieving store details from provider: {}".format(e))
#     return r.text
