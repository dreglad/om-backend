from time import sleep

from celery import shared_task

from .models import Conversion


logger = logging.getLogger('tasks')


@shared_task
def convert(conv):
    try:
        conv = Conversion.objects.get(pk=conv_pk)
    except Conversion.DoesNotExist:
        logger.warning('No Conversion object found: {}'.format(conversion_pk))

    conv.set_status(Conversion.RUNNING, progress=0)

    provider = conv.stream.get_provider()
    conv_ref, error = provider.request_conversion(dvr_store, conv.start, conv.duration)

    if error:
        conv.set_status(Conversion.FAILURE, result=error)
        return False

    while True:
        progress, error = wowza.query_conversion(conv_ref)
        if error:
            conv.set_status(Conversion.RUNNING, progress=progress)
            return False
        elif progress >= 1:
            # finished
            conv.set_status(Conversion.SUCCESS, progress=progress)
            break
        else:
            sleep(2)


@shared_task
def join(x, y):
    return x * y
