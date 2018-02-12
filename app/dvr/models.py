import logging
import os

from django.conf import settings
from django.contrib.postgres.fields import ArrayField, HStoreField
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from .mixins import *
from .stream_providers import *
from .fields import RecurrenceField

logger = logging.getLogger('default')


class Stream(EphemeralMixin, NameableMixin, MetadatableMixin, models.Model):
    """Stream model."""
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
        return self.name or '{} #{}'.format(_('Stream'), self.pk)

    class Meta:
        verbose_name = _('stream')
        verbose_name_plural = _('streams')
        permissions = (
            ('view_stream', 'View stream'),
        )


class SceneAnalysis(EphemeralMixin, WorkableMixin, models.Model):
    """SceneAnalysis model."""
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


class Series(EphemeralMixin, NameableMixin, MetadatableMixin, models.Model):
    """Series model"""
    stream = models.ForeignKey(
        'Stream', null=True, blank=True, on_delete=models.CASCADE, verbose_name=_('stream'),
        related_name='series')
    opening_sequence = models.ForeignKey(
        'Video', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('opening sequence'),
        related_name='opening_sequence_series')
    closing_sequence = models.ForeignKey(
        'Video', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('closing sequence'),
        related_name='closing_sequence_series')
    pause_sequence = models.ForeignKey(
        'Video', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('pause sequence'),
        related_name='pause_sequence_series')
    comeback_sequence = models.ForeignKey(
        'Video', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('comeback sequence'),
        related_name='cmeback_sequence_series')

    class Meta:
        ordering = ['name']
        verbose_name = _('series')
        verbose_name_plural = _('series')


class SeriesRecurrence(EphemeralMixin):
    """SeriesRecurrence"""
    series = models.ForeignKey(
        'Series', on_delete=models.CASCADE, verbose_name=_('series'), related_name='recurrences')
    recurrence = RecurrenceField(_('recurrence'))
    start_date = models.DateField(_('start date'), null=True, blank=True, db_index=True)
    end_date = models.DateField(_('end date'), null=True, blank=True, db_index=True)
    start_time = models.TimeField(_('start time'), db_index=True)
    end_time = models.TimeField(_('end time'), db_index=True)

    class Meta:
        ordering = ['series', 'start_date', 'start_time']
        verbose_name = _('series recurrence')
        verbose_name_plural = _('series recurrences')


class SceneChange(EphemeralMixin, models.Model):
    """SceneChange model"""
    scene_analysis = models.ForeignKey(
        'SceneAnalysis', verbose_name=_('scene analysis'), on_delete=models.CASCADE, related_name='scene_changes')
    time = models.DateTimeField(_('time'), db_index=True)
    value = models.FloatField(_('value'), db_index=True, null=True, blank=True)

    def __str__(self):
        return '{} {} {} {} {} {} {}'.format(
            _('Scene change'), _('of'), self.scene_analysis, _('at'), self.time, _('with value'), self.value)

    class Meta:
        ordering = ['-time', 'created_at']
        verbose_name = _('scene change')
        verbose_name_plural = _('scene changes')


class SceneSeries(EphemeralMixin, models.Model):
    """SceneSeries model"""
    TYPE_CHOICES = (
        ('OPENING', _('Opening')),
        ('ENDING', _('Ending')),
        ('PAUSE', _('Pause')),
        ('CAMEBACK', _('Came back')),
    )
    scene_analysis = models.ForeignKey(
        'SceneAnalysis', verbose_name=_('scene analysis'), related_name='scene_series',on_delete=models.CASCADE)
    type = models.CharField(_('type'), max_length=16, choices=TYPE_CHOICES, db_index=True)
    time = models.DateTimeField(_('time', ), db_index=True)
    series = models.ForeignKey(
        'Series', verbose_name=_('series'), on_delete=models.CASCADE, related_name='scene_series')

    def __str__(self):
        return '{} {} {} {} {} {} {}'.format(
            _('Scene series'), _('of'), self.scene_analysis, _('at'), self.time, _('with series'), self.series)

    class Meta:
        ordering = ['-time', 'created_at']
        verbose_name = _('scene series')
        verbose_name_plural = _('scene series')


class Conversion(WorkableMixin, EphemeralMixin, MetadatableMixin, models.Model):
    """Conversion model."""
    stream = models.ForeignKey(
        'Stream', null=True, blank=True, on_delete=models.CASCADE,
        verbose_name=_('stream'), related_name='conversions'
    )
    dvr_store = models.CharField(_('DVR Store'), max_length=128, blank=True, null=True)
    start = models.DateTimeField(_('start'), db_index=True)
    duration = models.DurationField(_('duration'))

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
    """Video model."""
    stream = models.ForeignKey(
        'Stream', verbose_name=_('stream'), related_name='videos', on_delete=models.CASCADE)
    series = models.ForeignKey(
        'Series', verbose_name=_('series'), blank=True, null=True, on_delete=models.SET_NULL,
        related_name='videos')
    sources = ArrayField(models.URLField(), verbose_name=_('sources'))
    start = models.DateTimeField(_('start'), db_index=True, null=True, blank=True)
    end = models.DateTimeField(_('end'), db_index=True, null=True, blank=True)
    file = models.FileField(_('video file'), blank=True, upload_to="videos/")
    images = ArrayField(models.FileField(upload_to='images'), verbose_name=_('thumbnails'), default=[], blank=True)
    duration = models.DurationField(_('duration'), null=True, blank=True)
    width = models.PositiveSmallIntegerField(_('width'), blank=True, null=True)
    height = models.PositiveSmallIntegerField(_('height'), blank=True, null=True)

    def get_source_filename(self, index=None, absolute=False):
        ext = 'mp4'
        filename = 'videos/{}/{}.{}'.format(self.pk, 'p{}'.format(index) if index else 'source', ext)
        return os.path.join(settings.MEDIA_ROOT, filename) if absolute else filename

    def __str__(self):
        return 'Video #{}'.format(self.pk)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('video')
        verbose_name_plural = _('videos')


class DistributionChannel(EphemeralMixin, NameableMixin, MetadatableMixin, ConfigurableMixin, models.Model):
    """DistributionChannel model."""
    TYPE_CHOICES = (
        ('MULTIMEDIA', _('Captura-Multimedia')),
        ('FTP', _('FTP')),
        ('YOUTUBE', _('YouTube')),
    )
    active = models.BooleanField(_('active'), default=True, db_index=True)
    type = models.CharField(_('type'), max_length=16, choices=TYPE_CHOICES, db_index=True)

    class Meta:
        verbose_name = _('distribution channel')
        verbose_name_plural = _('distribution channels')


class DistributionProfile(NameableMixin, EphemeralMixin, MetadatableMixin, ConfigurableMixin, models.Model):
    """DistributionProfile model."""
    active = models.BooleanField(_('active'), default=True, db_index=True)
    channel = models.ForeignKey(
        'DistributionChannel', verbose_name=_('channel'), related_name='profiles', on_delete=models.CASCADE)

    class Meta:
        ordering = ['channel', '-created_at']
        verbose_name = _('distribution profile')
        verbose_name_plural = _('distribution profiles')


class DistributionAttempt(EphemeralMixin, MetadatableMixin, WorkableMixin, models.Model):
    """DistributionAttempt model."""
    video = models.ForeignKey(
        'Video', verbose_name=_('video'), on_delete=models.CASCADE,
        related_name='distribution_attempts')
    profile = models.ForeignKey(
        'DistributionProfile', verbose_name=_('profile'), on_delete=models.CASCADE, 
        related_name='distribution_attempts')

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('distribution attempt')
        verbose_name_plural = _('distribution attempts')
