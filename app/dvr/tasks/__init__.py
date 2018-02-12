import logging
from time import sleep

from celery import shared_task

from dvr.models import SceneAnalysis, Video

# from .conversions import *
from .scenes import search_changes
from .videos import *

logger = logging.getLogger()


"""Periodic tasks (dispatchers)"""

@shared_task
def dispatch_scene_analysis():
    """Dispatcher task meant for celery beat to dsiaptch SceneAnalysis workables"""
    logging.debug('Executing dispatch_scene_analysis task')
    for scene_analysis in SceneAnalysis.objects.filter(status="PENDING"):
        scene_analysis.set_status('QUEUED')
        analyze_scenes.delay(scene_analysis.pk)


@shared_task
def dispatch_videos():
    for video in Video.objects.filter(status='PENDING').order_by('id'):
        video.set_status('QUEUED')
        process_video.apply_async([video.pk])
        sleep(0.5)


# @shared_task
# def dispatch_conversions():
#    for conversion in Conversion.objects.filter(status='PENDING').order_by('id'):
#         conversion.set_status('QUEUED')
#         convert.apply_async([conversion.pk], queue='conversions')
#         sleep(0.5)
