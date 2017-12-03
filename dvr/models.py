from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

class Stream(models.Model):
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'))
    live_url = models.URLField(_('live URL'), blank=True)
    dvr_url = models.URLField(_('DVR URL'), blank=True)
    api_url = models.URLField(_('API URL'), blank=True)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('stream')
        verbose_name_plural = _('streams')


class Conversion(models.Model):
    PENDING = 0
    QUEUED = 1
    RUNNING = 2
    SUCCESS = 3
    FAILURE = 4
    STATUS_CHOICES = (
        (QUEUED, _('Pending')),
        (RUNNING, _('Running')),
        (SUCCESS, _('Success')),
        (FAILURE, _('Failure')),
    )
    NORMAL = 0
    HIGH = 1
    LOW = 2
    PRIORITY_CHOICES = (
        (NORMAL, _('Normal')),
        (NORMAL, _('High')),
        (NORMAL, _('Low')),
    )
    status = models.PositiveSmallIntegerField(
        _('status'), db_index=True, choices=STATUS_CHOICES, default=PENDING)
    stream = models.ForeignKey(
        'Stream', verbose_name=_('stream'), related_name='conversions', on_delete=models.CASCADE)
    start = models.DateTimeField(_('start'))
    duration = models.DurationField(_('duration'))
    priority = models.PositiveSmallIntegerField(_('priority'), choices=PRIORITY_CHOICES, default=NORMAL)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True, null=True)
    metadata = models.HStoreField(_('metadata'), null=True)
    result = models.CharField(_('result'), max_length=64, blank=True, editable=False)

    @property
    def end(self):
        return self.start + self.duration

    class Meta:
        verbose_name = _('Conversion')
        verbose_name_plural = _('Conversions')


class Distribution(models.Model):
    WAITING = 0
    QUEUED = 1
    RUNNING = 2
    SUCCESS = 3
    FAILURE = 4
    STATUS_CHOICES = (
        (WAITING, _('Waiting')),
        (QUEUED, _('Pending')),
        (RUNNING, _('Running')),
        (SUCCESS, _('Success')),
        (FAILURE, _('Failure')),
    )
    status = models.PositiveSmallIntegerField(
        _('status'), db_index=True, choices=STATUS_CHOICES, default=PENDING)
    conversion = models.ForeignKey(
        'Conversion', verbose_name=_('conversion'), related_name='distributions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True, null=True)
    metadata = models.HStoreField(_('metadata'), null=True)
    target = models.CharField(_('target'), max_length=255)
    progress = models.FloatField(_('progress'), null=True)
    result = models.CharField(_('result'), max_length=255, blank=True, editable=False)

    class Meta:
        verbose_name = _('Distribution')
        verbose_name_plural = _('Distributions')
