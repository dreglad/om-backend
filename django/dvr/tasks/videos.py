from datetime import datetime, timedelta
import logging
import os
from posixpath import join
from subprocess import Popen, PIPE, call, check_output

from django.utils import timezone
from celery import shared_task, group
from celery.result import allow_join_result
import pexpect
import youtube_dl

from dvr.models import Video

from .video_utils import get_video_stream_info

logger = logging.getLogger()


@shared_task
def process_video(video_pk):
    video = Video.objects.get(pk=video_pk)
    video.set_status('STARTED', progress=0, result={'downloaded': '0'})

    # determine if conversion or download.

    conv = Conversion.objects.create(
        start=start, duration=duration, stream=stream, status='STARTED'
        )

    try:
        convert(conv.pk)
    except Exception as e:
        pass

    # start and wait for download job(s)
    group(
        download_video_youtubedl.s(url, video.get_source_filename(index, absolute=True), video_pk)
        for index, url in enumerate(video.sources, start=1)
    ).apply()

    for index in range(1, len(video.sources) + 1):
        part = video.get_source_filename(index, absolute=True)
        pexpect.spawn(
            'ffmpeg -y -i {0} -c copy -bsf:v h264_mp4toannexb -f mpegts {0}.ts'.format(part)
            ).expect(pexpect.EOF, timeout=None)

    source_filename = video.get_source_filename(absolute=True)
    video.set_status('STARTED', progress=0.99)

    print('About to join: ', source_filename)
    cmd = 'ffmpeg -y -i "concat:{}" -c copy -f mp4 -bsf:a aac_adtstoasc {}'.format(
        '|'.join(map(lambda p: '{}.ts'.format(p), parts)), source_filename)
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


@shared_task
def download_video_youtubedl(url, filename, video_pk=None):
    if video_pk: video = Video.objects.get(pk=video_pk)

    def youtubedl_progress(d):
        if video_pk:
            if d['status'] == 'downloading':
                progress = d.get('fragment_index', 0)/float(d.get('fragment_count', 0))
                video.set_status('STARTED', progress=progress)
            elif d['status'] == 'finished':
                video.set_status('STARTED', progress=1.0)
            elif d['status'] == 'error':
                video.set_status('ERROR', result=d)

    ydl_opts = {
        'format': 'bestaudio/best',
        'logger': logger,
        'hls_use_mpegts': settings.HLS_USE_MPEGTS,
        'hls_prefer_native': True,
        'outtmpl': filename,
        'progress_hooks': [youtubedl_progress],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            print('About to download: ', url)
            ydl.download([url])
            return True
        except youtube_dl.utils.DownloadError:
            video.set_status('FAILURE', result={ 'failed_download': url })
            return False


@shared_task
def download_video_ffmpeg(url, filename, video_pk=None):
    if video_pk: video = Video.objects.get(pk=video_pk)

    if not os.path.isdir(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    cmd = 'ffmpeg -y -i "{}" -c copy {}'.format(url, filename)
    thread = pexpect.spawn(cmd)
    cpl = thread.compile_pattern_list([
        pexpect.EOF,
        'Duration: (\d\d:\d\d:\d\d\.?\d*)',
        'time=(\d\d:\d\d:\d\d\.?\d*)'
        ])
    prev_progress, duration, progress = None, 0, 0
    while True:
        i = thread.expect_list(cpl, timeout=None)
        if i == 0: # EOF
            print('subprocess finished')
            return
        elif i == 1:
            duration = thread.match.group(1)
            print('duration', duration)
        elif i == 2:
            progress_time = thread.match.group(1)
            print(progress_time)
        if video_pk and duration and (progress != prev_progress):
            pass
    thread.close()
