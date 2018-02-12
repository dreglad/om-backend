from django import forms
from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from django.contrib.postgres.fields import HStoreField
from django_admin_json_editor import JSONEditorWidget
from django.utils.translation import ugettext_lazy as _

from .models import *


class BaseAdmin(GuardedModelAdmin):
    DICT_SCHEMA = {
        'type': 'object',
        'title': _('metadata'),
    }
    formfield_overrides = {
        HStoreField: {'widget': JSONEditorWidget(DICT_SCHEMA)}
    }


@admin.register(Stream)
class StreamAdmin(BaseAdmin):
    list_display = ('name', 'provider', 'metadata')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)


class MicroDateTimeInput(forms.DateTimeInput):
    supports_microseconds = True


class ConversionForm(forms.ModelForm):
    class Meta:
        model = Conversion
        fields = '__all__'
        widgets = {
            'start': MicroDateTimeInput(format='%Y-%m-%d %H:%M:%S.%f')
        }

@admin.register(Conversion)
class ConversionAdmin(BaseAdmin):
    list_display = ('pk', 'status', 'dvr_store', 'stream', 'start', 'duration')
    list_filter = ('stream', 'status', 'dvr_store')
    autocomplete_fields = ('stream',)
    form = ConversionForm


@admin.register(Video)
class VideoAdmin(BaseAdmin):
    list_display = ('id', 'stream', 'sources', 'duration', 'width', 'height', 'created_at', 'status')
    list_filter = ('stream', 'status')


@admin.register(Series)
class SeriesAdmin(BaseAdmin):
    list_display = (
        'id', 'stream', 'name', 'opening_sequence', 'closing_sequence',
        'pause_sequence', 'comeback_sequence')
    list_filter = ('stream',)


@admin.register(SeriesRecurrence)
class SeriesRecurrenceAdmin(BaseAdmin):
    list_display = (
        'id', 'series', 'recurrence', 'start_time', 'end_time', 'start_date', 'end_date')
    list_filter = ('series', 'series__stream')

    class Media:
        js = ('recurrence/js/recurrence-widget.js',
              'recurrence/js/recurrence.js')
        css = {
             'all': ('recurrence/css/recurrence.css',)
        }

@admin.register(DistributionChannel)
class DistributionChannelAdmin(BaseAdmin):
    list_display = ('name', 'type', 'active', 'created_at', 'metadata', 'configuration')


@admin.register(DistributionProfile)
class DistributionProfileAdmin(BaseAdmin):
    list_display = ('name', 'channel', 'active', 'created_at', 'metadata', 'configuration')


@admin.register(DistributionAttempt)
class DistributionAttemptAdmin(BaseAdmin):
    list_display = ('created_at', 'status', 'profile', 'result')


@admin.register(SceneChange)
class SceneChangeAdmin(BaseAdmin):
    list_display = ('id', 'scene_analysis', 'time', 'value')
    list_filter = ('scene_analysis__stream',)


@admin.register(SceneAnalysis)
class SceneAnalysisAdmin(BaseAdmin):
    list_display = ('id', 'stream', 'start', 'end', 'created_at', 'modified_at', 'progress', 'status')
    list_filter = ('stream',)
