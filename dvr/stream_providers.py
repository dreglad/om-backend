from django.core.cache import caches
from django.utils.functional import cached_property
from django.utils.text import slugify
import requests

from functools import partial
from itertools import groupby
import json
import logging
from operator import itemgetter, methodcaller
from posixpath import join
from urllib.parse import urljoin

logger = logging.getLogger('default')


class StreamProvider(object):

    def __init__(self, obj, metadata, *args, **kwargs):
        logger.debug('StreamProvider __init__ for obj: {}'.format(obj))
        self.obj = obj
        self.metadata = metadata
        self.cache = caches['stream_providers']

    def _get_cache_key(self, key):
        return '{}-{}-{}'.format(self.__class__.__name__, self.obj.__class__.__name__, key)

    def get_or_set_cache(self, key, value, timeout=None):
        logger.debug('get_or_set_cache with key: {}'.format(key))
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
        stores = self.get_or_set_cache('stores', self.retrieve_stores, 10)
        current_store = next(iter(stores.values()))[0]
        details = self.get_or_set_cache(
            current_store['name'] + '-details',
            partial(self.retrieve_store_details, current_store),
            15)

        return {
            'stores': stores,
            'current_store_details': {
                prop: details['DvrConverterStore'][prop] for prop in ('dvrStoreName', 'utcStart', 'utcEnd')
            },
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

        return {'success': result.get('success') is True}

    def retreive_groupconversions(self):
        try:
            r = requests.get(join(self.wowza_api_url, 'dvrstores'), headers={'Accept': 'application/json'})
            return json.loads(r.text)['groupConversionStatusList']
        except:
            logger.error('Error while requesting dvrstore list while retrieving groupconversions')
            return []

    def query_conversion(self, id):
        group_conversions = self.get_or_set_cache('groupconversions', self.retreive_groupconversions, 5)
        try:
            status = next(item['conversionStatusList'][0] for item in group_conversions if item["id"] == int(id))
        except:
            return {'success': False, 'message': "Error while querying conversion status"}

        if not status or status.get('state') == 'FAILURE':
            return {'success': False, 'message': ''}
        return {
            'success': True,
            'progress': 0,
            'state': status.get('state'),
        }

        # self.retrieve_store_details(['groupConversionStatusList'])
        # partial(self.retrieve_store_details, current_store),
        # try:
        #     r = requests.get(
        #         join(self.wowza_api_url, 'dvrstores/actions/convert'),
        #         headers={'Accept': 'application/json'})
        #     result = json.loads(r.text)
        # except Exception as e:
        #     raise


    def retrieve_store_details(self, store):
        logger.info('Retrieving store details for store: {}'.format(store))
        data = {}
        try:
            r = requests.get(store['url'], headers={'Accept': 'application/json'})
            r.raise_for_status()
            data = json.loads(r.text)
        except:
            logger.eror("Error while retrieving store details from provider: {}".format(e))
        return data


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
            stores = {k: list(v) for k, v in groupby(stores, key=group_key)}
        except:
            logger.eror("Error while retrieving data from provider: {}")
        return stores
