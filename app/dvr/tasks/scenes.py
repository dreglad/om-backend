from datetime import datetime, timedelta
import logging
from posixpath import join
from subprocess import Popen, PIPE
import re

from django.conf import settings
from django.utils import timezone
from celery import shared_task

from dvr.models import SceneAnalysis, SceneChange, Stream, Series, FoundSequence

logger = logging.getLogger()


def range_milliseconds(start, stop, step=1000):
    for ms in range(0, int((stop - start).total_seconds() * 1000), step):
        yield start + timedelta(milliseconds=ms)


def search_sequence(start, end, series_qs, sequence_types):
    series_qs.filter(**{'{}__isnull'.format(sequence_type): False})
    for probe_time in range_milliseconds(start, end):
        for series in series_qs:
            for sequence_type in sequence_types:
                video = getattr(series, sequence_type)
                score = compare_videos(series.stream.get_playlist(probe_time, video.duration), video.file.url)
                print(score)
                if (score):
                    # TODO: asses SSIM and PSNR
                    return (prove_time, video)
    return (prove_time, None)



def search_series(start, end, stream_id):
    series_qs = Series.objects.filter(stream_id=stream_id)
    opening_time, opening = search_sequence(start, end, series_qs, ['opening_sequence'])
    if opening:
        series = opening.opening_sequence_series
        found_sequence = FoundSequence.objects.create(
            sequence_type='opening_sequence', series=series, time=opening_time + series.opening_sequence_offset)


@shared_task
def autocreate_scene_analysis():
    """Auto-create scene analysis objects and dispatch their associated background jobs"""
    logging.debug('Executing autocreate_scene_analysis task')
    if settings.DEBUG:
        logging.info('Skupping tasks in DEBUG mode')
        return
    AUTOCREATE_DURATION = timedelta(minutes=20)
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
                search_changes.delay(scene_analysis.pk)
            else:
                logging.info('Autocreate duration falls outside available range, skippong SceneAnalysis cretion')


@shared_task
def search_changes(scene_analysis_pk):
    """Perform scene change analysis with FFmpeg"""
    logging.debug('Executing search_changes task')
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
        'ffmpeg', '-i', input_url, '-vsync', 'passthrough', '-an', '-f', 'null',
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
def compare_videos(test_video, ref_video):
    cmd = 'ffmpeg -i "{}" -i "{}" -lavfi "ssim;[0:v][1:v]psnr" -f null -'
    thread = pexpect.spawn(cmd)
    cpl = thread.compile_pattern_list([
        pexpect.EOF,
        'SSIM Y:(.+) \((.+)\) U:(.+) \((.+)\) V:(.+) \((.+)\) All:(.+) \((.+)\)',
        'PSNR y:(.+) u:(.+) v:(.+) average:(.+) min:(.+) max:(.+)',
        ])
    ssim = psnr = ''
    while True:
        i = thread.expect_list(cpl, timeout=None)
        if i == 0: # EOF
            print('subprocess finished')
        elif i == 1:
            ssim = thread.match.group(0)
        elif i == 2:
            psnr = thread.match.group(0)
    thread.close()
    return (ssim, psnr)
