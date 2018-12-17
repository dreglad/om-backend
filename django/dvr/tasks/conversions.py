from celery import shared_task

from dvr.models import Conversion

logger = logging.getLogger()


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
