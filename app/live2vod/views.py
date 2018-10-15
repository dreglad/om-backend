from datetime import timedelta, datetime
from posixpath import join
from urllib.parse import urljoin
import pytz
from time import sleep

from django.http import HttpResponse
from django.utils import timezone
import requests

from dvr.models import Stream
from dvr.tasks.video_utils import download_live_video_sample, get_video_duration


def check_streams(request):
    errors = []
    for stream in Stream.objects.all():
        try:
            # Test stream metadata for a recent recording time
            end = datetime.fromtimestamp(stream.get_provider().get_data()['current_store_details']['utcEnd']/1000.0)
            dvr_time, threshold_time = (pytz.utc.localize(end), timezone.now() - timedelta(minutes=3))
            assert dvr_time > threshold_time, '{} is greater than {}'.format()
            # Download and test a sample video
            assert _test_live(stream), 'Did not get live video sample with expected length'
        except Exception as err:
            print('Streaming not OK: %s' % err)
            reset_url = urljoin(stream.metadata['wseApiUrl'], (
                '/v2/servers/_defaultServer_/vhosts/_defaultVHost_'
                '/applications/{wseApplication}'
                '/actions/restart'
                ).format(**stream.metadata)
            )
            print('Resetting stream: {}'.format(reset_url))
            r = requests.put(reset_url)
            print(r.text)
            errors.append(stream.metadata['wseStream'])
            errors.append(err)
            continue  # Only restart once
    status = 500 if len(errors) else 200
    return HttpResponse(', '.join(errors), status=status)


def _test_live(stream):
    """Tests live HLS stream"""
    filename = '/tmp/temp.mp4'
    test_url = urljoin(stream.metadata['wseStreamingUrl'],
                       '{wseApplication}/{wseStream}/playlist.m3u8').format(**stream.metadata)
    download_live_video_sample(test_url, time=6, filename=filename)
    print(get_video_duration(filename))
    return get_video_duration(filename) > timedelta(seconds=4)
