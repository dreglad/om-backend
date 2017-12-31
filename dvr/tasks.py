from datetime import datetime, timedelta
import logging
from posixpath import join
from subprocess import Popen, PIPE, call, check_output
import re
from time import sleep
from urllib.parse import urljoin

from django.db.models import F
from celery import shared_task
from celery.decorators import periodic_task

from .models import Conversion, SceneAnalysis, SceneChange

logger = logging.getLogger('tasks')


# @periodic_task
# def dispatch_conversions():
#     # Pending convs
#     for conv in Conversion.objects.filter('PENDING'):
#         conv.set_status('QUEUED')
#         convert.delay(conv.pk)


# @periodic_task
# def dispatch_video():
#     # Pending convs
#     for vid in Video.objects.filter('PENDING'):
#         vid.set_status('QUEUED')
#         convert.delay(conv.pk)


@shared_task(bind=True)
@periodic_task(run_every=timedelta(minutes=15))
def autocreate_scene_analysis(self):
    logging.debug('Executing autocreate_scene_analysis task')
    for stream in Stream.objects.all():
        running = stream.scene_analysis.objects.filter(status='STARTED')
        if not running.exists():
            try:
                max_available = datetime.fromtimestamp(
                    int(stream.get_provider().get_data()['current_store']['utcEnd']) / 1000)
            except:
                msg = 'Could not retrieve current_store data from stream provider details'
                logging.error(msg)
                return self.update_state(state='FAILURE', meta={'message': msg })
            recent = stream.scene_analysis.objects.filter(start__gte=max_available - F('duration'))
            if recent.exists():
                logging.info('A recent conversion already exists for the current store max time, looking back...')
            else:
               loggin.info('No recent conversion found, requesting a recent chunk')
        else:
            logging.warning('A scene analysis is already running. Maybe we are autocreating them too frequently')



@shared_task
@periodic_task(run_every=timedelta(minutes=1))
def dispatch_scene_analysis():
    logging.debug('Executing dispatch_scene_analysis task')
    pending = SceneAnalysis.objects.filter(status="PENDING")
    for scene_analysis in pending:
        scene_analysis.set_status('QUEUED')
        analyze_scenes.delay(scene_analysis.pk)


@shared_task
def analyze_scenes(scene_analysis_pk):
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
        'smil:{}.smil'.format(metadata['wseStream']),
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
    try:
        conv = Conversion.objects.get(pk=conversion_pk)
    except Conversion.DoesNotExist:
        logger.warning('No Conversion object found: {}'.format(conversion_pk))
        return

    conv.set_status(Conversion.STARTED, progress=0)

    provider = conv.stream.get_provider()
    result = provider.request_conversion(conv)

    if not result.get('success'):
        conv.set_status(Conversion.FAILURE, result=result.get('message'))
        return False

    while True:
        status = provider.query_conversion(result.get('message'), conv)
        if not status:
            # error
            conv.set_status('FAILURE')
            break
        code = status.pop('status')
        conv.set_status(code, **status)
        if code in ['FAILURE', 'SUCCESS']:
            break
        else:
            logger.debug('Sleeping')
