from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


class WorkableMixin(models.Model):
    """
    Workable mixin. Allows a model to have an asynchronous job attached,
    as well as an status, progress and a result.
    """
    PENDING = 'PENDING'
    QUEUED = 'QUEUED'
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    STATUS_CHOICES = (
        (PENDING, _('Pending')),
        (QUEUED, _('Queued')),
        (STARTED, _('Started')),
        (SUCCESS, _('Success')),
        (FAILURE, _('Failure')),
    )
    status = models.CharField(_('status'), max_length=32, db_index=True, editable=True,
                                choices=STATUS_CHOICES, default=PENDING)
    progress = models.FloatField(_('progress'), null=True, blank=True, editable=True)
    result = HStoreField(_('result'), null=True, blank=True)

    def set_status(self, status, **field_values):
        """ Update object status without saving with optional additional fields (like progress and/or result"""
        field_values.update({'status': status})
        return self.__class__.objects.filter(pk=self.pk).update(**field_values)

    class Meta:
        abstract = True


class EphemeralMixin(models.Model):
    """
    EphemeralMixin. Allows a model to have an associated creation and modification datetime and user
    """
    created_at = models.DateTimeField(_('created at'), default=timezone.now, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('created by'), blank=True, null=True,
        on_delete=models.SET_NULL, related_name='%(class)s_created', editable=False)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True, null=True, editable=False)
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('modified by'), blank=True, null=True,
        on_delete=models.SET_NULL, related_name='%(class)s_modified', editable=False)

    class Meta:
        abstract = True


class MetadatableMixin(models.Model):
    """
    MetadatableMixin. Allows a model to have a user-specified key/value metadata
    """
    metadata = HStoreField(_('metadata'), null=True, blank=True)

    class Meta:
        abstract = True


class ConfigurableMixin(models.Model):
    """
    COnfigurableMixin. Allows a model to have user-specified key/value configuration properties
    """
    configuration = HStoreField(_('configuration'), null=True, blank=True)

    class Meta:
        abstract = True


class MediaContentMixin(models.Model):
    """
    MediaContentMixin. Allow a model to have a file associated to it through a storage backend.
    """
    file = models.FileField(_('file'), blank=True, null=True)

    class Meta:
        abstract = True



class NameableMixin(models.Model):
    """
    NameableMixin. Allows a model to have a name and an associated unique slug.
    """
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
