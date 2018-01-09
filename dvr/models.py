import logging

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from .mixins import *
from .stream_providers import *

logger = logging.getLogger('default')

class Stream(EphemeralMixin, NameableMixin, MetadatableMixin, models.Model):
    """
    Stream model
    """
    PROVIDER_CHOICES = (
        ('WowzaStreamingEngine', _('Wowza Streaming Engine')),
    )
    provider = models.CharField(_('provider'), max_length=64, choices=PROVIDER_CHOICES)

    def get_provider(self):
        provider_class = eval(self.provider + 'StreamProvider')
        logger.debug('Instantiating new provider class {}'.format(provider_class))
        return provider_class(self, self.metadata) 

    @cached_property
    def provider_data(self):
        return self.get_provider().get_data()

    def __str__(self):
        return '{} #{}: {}'.format(_('Stream'), self.pk, self.name)

    class Meta:
        verbose_name = _('stream')
        verbose_name_plural = _('streams')


class SceneAnalysis(EphemeralMixin, WorkableMixin, models.Model):
    """
    Scene Analysis model
    """
    stream = models.ForeignKey(
        'Stream', verbose_name=_('stream'), related_name='scene_analysis', on_delete=models.CASCADE)
    start = models.DateTimeField(_('start'), db_index=True)
    end = models.DateTimeField(_('end'), db_index=True)

    @property
    def duration(self):
        return self.end - self.start

    def __str__(self):
        return '{} #{} {} {} {} {} {} {}'.format(
            _('Scene analysis'), self.pk, _('of'), self.stream, _('from'), self.start, _('to'), self.end)

    class Meta:
        ordering = ['-created_at', '-end', '-start']
        verbose_name = _('scene analysis')
        verbose_name_plural = _('scene analysis')


class SceneChange(EphemeralMixin, models.Model):
    """
    Scene Change model
    """
    scene_analysis = models.ForeignKey(
        'SceneAnalysis', verbose_name=_('scene analysis'), related_name='scene_changes',on_delete=models.CASCADE)
    time = models.DateTimeField(_('time', ))
    value = models.FloatField(_('value'), db_index=True, null=True, blank=True)

    def __str__(self):
        return '{} {} {} {} {} {} {}'.format(
            _('Scene change'), _('of'), self.scene_analysis, _('at'), self.time, _('with value'), self.value)

    class Meta:
        ordering = ['-time', 'created_at']
        verbose_name = _('scene change')
        verbose_name_plural = _('scene changes')

# class Store(EphemeralMixin, models.Model):
#     stream = models.ForeignKey('Stream', verbose_name=_('stream'), related_name='stores', )
#     name = models.CharField(_('name'), max_length=128)
#     start = models.DateTimeField(_('start'))
#     start = models.DateTimeField(_('end'))


class Conversion(WorkableMixin, EphemeralMixin, MetadatableMixin, models.Model):
    """
    Conversion model
    """
    stream = models.ForeignKey(
        'Stream', null=True, blank=True, on_delete=models.CASCADE,
        verbose_name=_('stream'), related_name='conversions'
    )
    dvr_store = models.CharField(_('DVR Store'), max_length=128, blank=True, null=True)
    start = models.DateTimeField(_('start'))
    duration = models.DurationField(_('duration'))

    def save(self, *args, **kwargs):
        was_new = not self.pk and self.status == Conversion.PENDING
        super(Conversion, self).save(*args, **kwargs)
        if was_new:
            from .tasks import convert
            convert.delay(self.pk)

    @property
    def end(self):
        return self.start + self.duration

    def __str__(self):
        return '{} #{} {} {} {} {} {} {}'.format(
            _('Conversion'), self.pk, _('of'), self.stream, _('from'), self.start, _('to'), self.end)

    class Meta:
        ordering = ('-pk',)
        verbose_name = _('conversion')
        verbose_name_plural = _('conversions')


class Video(EphemeralMixin, WorkableMixin, ConfigurableMixin, MetadatableMixin, models.Model):
    """
    Video model
    """
    conversions = models.ManyToManyField('Conversion', verbose_name=_('conversions'), blank=True)

    def __str(self):
        return 'Video #{}',forat(self.pk)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('video')
        verbose_name_plural = _('videos')


class DistributionChannel(EphemeralMixin, NameableMixin, MetadatableMixin, ConfigurableMixin, models.Model):
    """
    Distribution channel model
    """
    MULTIMEDIA = 'multimedia'
    FTP = 'ftp'
    YOUTUBE = 'youtube'
    TYPE_CHOICES = (
        (MULTIMEDIA, _('Captura-Multimedia')),
        (FTP, _('FTP')),
        (YOUTUBE, _('YouTube')),
    )
    active = models.BooleanField(_('active'), default=True)
    type = models.CharField(_('type'), max_length=128, choices=TYPE_CHOICES)

    class Meta:
        verbose_name = _('distribution channel')
        verbose_name_plural = _('distribution channels')


class DistributionProfile(NameableMixin, EphemeralMixin, MetadatableMixin, ConfigurableMixin, models.Model):
    """
    Distribution profile model
    """
    active = models.BooleanField(_('active'), default=True)
    channel = models.ForeignKey(
        'DistributionChannel', verbose_name=_('channel'), related_name='profiles', on_delete=models.CASCADE)

    class Meta:
        ordering = ['channel', '-created_at']
        verbose_name = _('distribution profile')
        verbose_name_plural = _('distribution profiles')


class DistributionAttempt(EphemeralMixin, MetadatableMixin, WorkableMixin, models.Model):
    """
    Distribution attemp model
    """
    video = models.ForeignKey(
        'Video', on_delete=models.CASCADE,
        verbose_name=_('video'), related_name='distribution_attempts')
    profile = models.ForeignKey('DistributionProfile', verbose_name=_('profile'), on_delete=models.CASCADE,
                                related_name='attempts')

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('distribution attempt')
        verbose_name_plural = _('distribution attempts')
