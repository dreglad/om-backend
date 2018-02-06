from datetime import datetime, timedelta
import logging

from django.utils import timezone
from celery import shared_task

from dvr.models import SceneAnalysis, SceneChange, Stream

logger = logging.getLogger()


@shared_task
def autocreate_scene_analysis():
    """Auto-create scene analysis objects and dispatch their associated background jobs"""
    logging.debug('Executing autocreate_scene_analysis task')
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
                analyze_scenes.delay(scene_analysis.pk)
            else:
                logging.info('Autocreate duration falls outside available range, skippong SceneAnalysis cretion')

