from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


class WorkableMixin(models.Model):
    WAITING = 0
    QUEUED = 1
    RUNNING = 2
    SUCCESS = 3
    FAILURE = 4
    STATUS_CHOICES = (
        (WAITING, _('Waiting')),
        (QUEUED, _('Queued')),
        (RUNNING, _('Running')),
        (SUCCESS, _('Success')),
        (FAILURE, _('Failure')),
    )
    status = models.PositiveSmallIntegerField(
        _('status'), db_index=True, choices=STATUS_CHOICES, default=WAITING, editable=False)
    progress = models.FloatField(_('progress'), null=True, blank=True, editable=False)
    result = models.CharField(_('result'), max_length=255, blank=True, null=True, editable=False)

    def set_status(self, status, **field_values):
        """ Update object status without saving with optional additional fields (like progress and/or result"""
        field_values.update({'status': status})
        return obj.__class__.objects.filter(pk=obj.pk).update(**field_values)

    class Meta:
        abstract = True


class EphemeralMixin(models.Model):
    created_at = models.DateTimeField(_('created at'), default=timezone.now, editable=False)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True, null=True, editable=False)

    class Meta:
        abstract = True


class MetadatableMixin(models.Model):
    metadata = HStoreField(_('metadata'), null=True, blank=True)

    class Meta:
        abstract = True


class NameableMixin(models.Model):
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, blank=True, default='', unique=True)

    def _get_unique_slug(self):
        slug = slugify(self.name or self.__class__.__name__)
        unique_slug = slug
        num = 1
        while self.__class__.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        return super(NameableMixin, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
