from posixpath import join
from urllib.parse import urljoin

from django.http import HttpResponse

from dvr.models import Stream
from dvr.tasks.video_utils import download_live_video_sample, get_video_info


def check_streams(request):
    for stream in Stream.objects.all():
        m = stream.metadata
        filename = '/tmp/temp.mp4'
        test_url = urljoin(m['wseStreamingUrl'],
                           '{wseApplication}/{wseStream}/playlist.m3u8').format(**m)
        download_live_video_sample(test_url, time=6, filename=filename)
        info = get_video_info(filename)
        if info.get('duration') > '5000':
            print('Streaming OK')
        else:
            print('Streaming not OK, reseting')
            reset_url = urljoin(m['wseApiUrl'], (
                '/v2/servers/_defaultServer_/vhosts/_defaultVHost_'
                '/applications/{wseApplication}/instances/_definst_'
                '/incomingstreams/{wseStream}/actions/resetStream'
                ).format(**m)
            )
    return HttpResponse('Ok')
