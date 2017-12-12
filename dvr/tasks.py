import logging
from time import sleep

from celery import shared_task

from .models import Conversion


logger = logging.getLogger('tasks')


@shared_task
def convert(conversion_pk):
    try:
        conv = Conversion.objects.get(pk=conversion_pk)
    except Conversion.DoesNotExist:
        logger.warning('No Conversion object found: {}'.format(conversion_pk))
        return

    conv.set_status(Conversion.STARTED, progress=0)

    provider = conv.stream.get_provider()
    result = provider.request_conversion(conv.dvr_store, conv.start, conv.duration)

    if not result['success']:
        conv.set_status(Conversion.FAILURE, result=result.get('message'))
        return False

    while True:
        progress, error = provider.request_conversion(result['message'])
        if error:
            conv.set_status(Conversion.STARTED, progress=progress)
            return False
        elif progress >= 1:
            # finished
            conv.set_status(Conversion.SUCCESS, progress=progress)
            break
        else:
            sleep(2)

@shared_task
def take_screenshots(file):
    pass

@shared_task
def join(x, y):
    return x * y
