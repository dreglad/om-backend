import logging
from time import sleep
import shutil

from celery import shared_task
from django.conf import settings

from dvr.models import SceneAnalysis, Video

from .conversions import convert
from .scenes import search_changes
from .videos import process_video

logger = logging.getLogger()


"""Periodic tasks (dispatchers)"""


@shared_task
def dispatch_scene_analysis():
    """Dispatcher task meant for celery beat to dsiaptch SceneAnalysis workables"""
    if settings.DEBUG:
        logging.info('Skipping task in DEBUG mode')
        return
    logging.debug('Executing dispatch_scene_analysis task')
    for scene_analysis in SceneAnalysis.objects.filter(status="PENDING"):
        scene_analysis.set_status('QUEUED')
        search_changes.apply_async([scene_analysis.pk])


@shared_task
def dispatch_videos():
    """Ingest new videos"""
    for video in Video.objects.filter(status='PENDING').order_by('id'):
        video.set_status('QUEUED')
        process_video.apply_async([video.pk])
        sleep(0.5)


@shared_task
def dispatch_conversions():
    """?Wowza's native conversion mechanism"""
    for conversion in Conversion.objects.filter(status='PENDING').order_by('id'):
        conversion.set_status('QUEUED')
        convert.apply_async([conversion.pk], queue='conversions')
        sleep(0.5)


@shared_task
def dispatch_media_dispose():
    if MEDIA_DISPOSE_THRESHOLD > 0:
        total, used, *_ = shutil.disk_usage(settings.MEDIA_ROOT)
        logging.debug('%s filesystem is at %s out of %i', settings.MEDIA_ROOT, used, total)
        if used / total > settings.MEDIA_DISPOSE_THRESHOLD:
            earliest = Video.objects.earliest()
            if earliest:
                logging.info('Disposing %s', earliest)
                os.remove(os.path.join(settings.MEDIA_ROOT, earliest.get_source_filename()))
