from datetime import datetime, timedelta
import logging
import os
from posixpath import join
from subprocess import Popen, PIPE, call, check_output
import re
import tempfile
from time import sleep
from urllib.parse import urljoin

from django.conf import settings
from django.db.models import F
from django.utils import timezone
from celery import shared_task, task, group
from celery.decorators import periodic_task
from celery.result import allow_join_result
import pexpect

from .models import Conversion, SceneAnalysis, SceneChange, Stream, Video
from .video_utils import get_video_stream_info

logger = logging.getLogger('tasks')


@shared_task
def autocreate_scene_analysis():
    """Auto-create scene analysis objects and dispatch their associated background jobs"""
    logging.debug('Executing autocreate_scene_analysis task')
    AUTOCREATE_DURATION = timedelta(minutes=15)
    for stream in Stream.objects.all():
        running = stream.scene_analysis.filter(status='STARTED')
        if not running.exists():
            try:
                store = stream.provider_data['current_store_details']
                max_available = datetime.fromtimestamp(int(store['utcEnd']) / 1000, tz=timezone.utc)
                min_available = datetime.fromtimestamp(int(store['utcStart']) / 1000, tz=timezone.utc)
            except:
                logging.error('Could not retrieve current_store data from stream provider details')
                return

            previous_analysis = stream.scene_analysis.all().order_by('-end').first()
            if previous_analysis:
                logging.debug('Previous SceneAnalysis fount: {}'.format(previous_analysis))
                start = previous_analysis.end
            else:
                logging.debug('Previous SceneAnalysis not found, creating one')
                start = min_available.replace(second=0, microsecond=0) + timedelta(minutes=1)

            end = start + AUTOCREATE_DURATION
            if start >= min_available and end <= max_available:
                logging.debug('Autocreating SceneAnalysis')
                scene_analysis = SceneAnalysis.objects.create(stream=stream, start=start, end=end, status='QUEUED')
                analyze_scenes.delay(scene_analysis.pk)
            else:
                logging.info('Autocreate duration falls outside available range, skippong SceneAnalysis cretion')


@shared_task
def dispatch_scene_analysis():
    """Dispatcher task meant for celery beat to dsiaptch SceneAnalysis workables"""
    logging.debug('Executing dispatch_scene_analysis task')
    for scene_analysis in SceneAnalysis.objects.filter(status="PENDING"):
        scene_analysis.set_status('QUEUED')
        analyze_scenes.delay(scene_analysis.pk)


@shared_task
def dispatch_conversions():
   for conversion in Conversion.objects.filter(status='PENDING').order_by('id'):
        conversion.set_status('QUEUED')
        convert.apply_async([conversion.pk], queue='conversions')
        sleep(0.5)


@shared_task
def dispatch_videos():
    for video in Video.objects.filter(status='PENDING').order_by('id'):
        video.set_status('QUEUED')
        process_video.apply_async([video.pk])
        sleep(0.5)


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

    print('Parts are: ', parts)

    for part in parts:
        print('Demuxing to mpegts')
        pexpect.spawn(
            'ffmpeg -y -i {0} -c copy -f mpegts {0}.ts'.format(part)
            ).wait()

    source_filename = video.get_source_filename(absolute=True)

    print('About to join: ', source_filename)
    cmd = 'ffmpeg -y -i "concat:{}" -c copy -f mp4 -movflags +faststart {}'.format(
        '|'.join(map(lambda p: '{}.ts'.format(p), parts)), source_filename)
    print('Concat to mp4 command: ', cmd)
    pexpect.spawn(cmd).wait()

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
    import youtube_dl

    if video_pk: video = Video.objects.get(pk=video_pk)

    def youtubedl_progress(d):
        if video_pk:
            if d['status'] == 'downloading':
                progress = d.get('fragment_index', 0)/float(d.get('fragment_count', 0))
                video.set_status('STARTED', progress=progress - 0.01)
            elif d['status'] == 'finished':
                video.set_status('STARTED', progress=0.99)
            elif d['status'] == 'error':
                video.set_status('ERROR', result=d)

    ydl_opts = {
        'format': 'bestaudio/best',
        'logger': logger,
        # 'hls_use_mpegts': True,
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
    print('Executing command: ', cmd)
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
            #video.set_status('STARTED', pregress=xxxxx)
    thread.close()


# @shared_task(timeout=60)
# def join_conversions(conv_pks):
#     convs = Conversion.objects.filter(pk__in=conv_pks)

#     for pk in conv_pks:

@shared_task
def analyze_scenes(scene_analysis_pk):
    """Perform scene change analysis with FFmpeg"""
    logging.debug('Executing analyze_scenes task')
    try:
        scene_analysis = SceneAnalysis.objects.get(pk=scene_analysis_pk)
    except SceneAnalysis.DoesNotExist:
        logger.warning('No SceneAnalysis object found: {}'.format(scene_analysis_pk))
        return

    change_thresshold = 0.65
    metadata = scene_analysis.stream.metadata
    seconds = scene_analysis.duration.total_seconds()
    input_url = join(
        metadata['wseStreamingUrl'],
        metadata['wseApplication'],
        # 'smil:{}.smil'.format(metadata['wseStream']),
        '{}_360p'.format(metadata['wseStream']),
        'playlist.m3u8'
        ) + '?DVR&wowzadvrplayliststart={}&wowzadvrplaylistduration={}'.format(
                scene_analysis.start.strftime('%Y%m%d%H%M%S'),
                int(seconds * 1000))
    cmd_args = [
        'ffmpeg', '-i', input_url, '-t', str(seconds), '-vsync', 'passthrough', '-an', '-f', 'null',
        '-vf', 'select=\'gte(scene,{})\',metadata=print'.format(change_thresshold),
        '-']
    current_pos = None
    scene_analysis.set_status('STARTED', progress=0)
    with Popen(cmd_args, stderr=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stderr:
            logger.debug('Got scene detection output: {}'.format(line))
            pts_time = re.findall('pts_time:(\d+\.?\d*)', line)
            if pts_time:
                current_pos = float(pts_time[0])
                logger.info('Got current pos: {}'.format(current_pos))
            else:
                scene_score = re.findall('lavfi\.scene_score=(\d+\.?\d*)', line)
                if scene_score and current_pos:
                    logger.info('Got current score: {}'.format(scene_score[0]))
                    SceneChange.objects.create(
                        scene_analysis=scene_analysis,
                        time=scene_analysis.start + timedelta(seconds=current_pos),
                        value=float(scene_score[0])
                    )
                    progress = current_pos / float(scene_analysis.duration.total_seconds())
                    scene_analysis.set_status('STARTED', progress=progress)
    scene_analysis.set_status('SUCCESS', progress=1)


@shared_task
def convert(conversion_pk):
    """Perform live-to-VOD conversion through the streaming provider"""
    try:
        conv = Conversion.objects.get(pk=conversion_pk)
    except Conversion.DoesNotExist:
        logger.warning('No Conversion object found: {}'.format(conversion_pk))
        return

    conv.set_status('STARTED', progress=0)

    provider = conv.stream.get_provider()
    result = provider.request_conversion(conv)

    if not result.get('success'):
        if result.get('message') and 'conversion already in progress' in result['message']:
            conv.set_status('PENDING', result=result)
        else:
            conv.set_status('FAILURE', result=result)
        return False

    while True:
        status = provider.query_conversion(result.get('message'), conv)
        if not status:
            # error
            conv.set_status('FAILURE', result=result)
            break
        code = status.pop('status')
        conv.set_status(code, **status)
        if code in ['FAILURE', 'SUCCESS']:
            sleep(5)
            break
        else:
            sleep(1)
