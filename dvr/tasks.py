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

@shared_task
def join(x, y):
    return x * y
