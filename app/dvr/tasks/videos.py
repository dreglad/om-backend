from datetime import datetime, timedelta
import logging
import os
from posixpath import join
from subprocess import Popen, PIPE, call, check_output

from django.utils import timezone
from celery import shared_task, group
from celery.result import allow_join_result
import pexpect

from dvr.models import Video

from .video_utils import get_video_stream_info


@shared_task
def process_video(video_pk):
    video = Video.objects.get(pk=video_pk)

    video.set_status('STARTED', progress=0, result={'downloaded': '0'})

    # start and wait for download job(s)
    jobs = []
    for index, url in enumerate(video.sources, start=1):
        print('trying with ', url)
        jobs.append(download_video_youtubedl.s(url, video.get_source_filename(index, absolute=True), video_pk))

    with allow_join_result():
        group(jobs).apply_async().join()

    parts = [video.get_source_filename(index, absolute=True)
             for index in range(1, len(video.sources) + 1)]

    video.set_status('STARTED', progress=0.98)

    print('Parts are: ', parts)
    for part in parts:
        print('Demuxing to mpegts')
        pexpect.spawn(
            # 'ffmpeg -y -i {0} -c copy -f mpegts {0}.ts'.format(part)
            'ffmpeg -y -i {0} -c copy -bsf:v h264_mp4toannexb -f mpegts {0}.ts'.format(part)
            ).expect(pexpect.EOF, timeout=None)

    source_filename = video.get_source_filename(absolute=True)

    video.set_status('STARTED', progress=0.99)

    print('About to join: ', source_filename)
    cmd = 'ffmpeg -y -i "concat:{}" -c copy -f mp4 -bsf:a aac_adtstoasc {}'.format(
        '|'.join(map(lambda p: '{}.ts'.format(p), parts)), source_filename)
    print('Concat to mp4 command: ', cmd)
    pexpect.spawn(cmd).expect(pexpect.EOF, timeout=None)

    # Finished
    vinfo = get_video_stream_info(source_filename)
    if vinfo and vinfo.get('duration'):
        video.set_status(
            'SUCCESS', progress=1,
            file=video.get_source_filename(),
            duration=timedelta(seconds=float(vinfo['duration'])),
            width=vinfo['width'], height=vinfo['height'],
            result={'finished': timezone.now().isoformat()}
            )
    else:
        video.set_status('FAILURE', result=vinfo or None)

