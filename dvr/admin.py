from django import forms
from django.contrib import admin
from django.contrib.postgres.fields import HStoreField
from django_admin_json_editor import JSONEditorWidget
from django.utils.translation import ugettext_lazy as _

from .models import *


class BaseAdmin(admin.ModelAdmin):
    DICT_SCHEMA = {
        'type': 'object',
        'title': _('metadata'),
    }
    formfield_overrides = {
        HStoreField: {'widget': JSONEditorWidget(DICT_SCHEMA) }
    }


@admin.register(Stream)
class StreamAdmin(BaseAdmin):
    list_display = ('name', 'provider', 'metadata')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)

class MicroDateTimeInput(forms.DateTimeInput):
    supports_microseconds = True


class ConversionForm(forms.ModelForm):
    # start = MicroDateTimeInput(format='%Y-%m-%d %H:%M:%S')
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

    # formfield_overrides = {
    #     models.DateTimeField: {'widget': MicroDateTimeInput()},
    # }


# class ConversionInline(admin.TabularInline):
#     model = Conversion

@admin.register(Video)
class VideoAdmin(BaseAdmin):
    pass


@admin.register(DistributionChannel)
class DistributionChannelAdmin(BaseAdmin):
    list_display = ('name', 'type', 'active', 'created_at', 'metadata', 'configuration')


@admin.register(DistributionProfile)
class DistributionProfileAdmin(BaseAdmin):
    list_display = ('name', 'channel', 'active', 'created_at', 'metadata', 'configuration')


@admin.register(DistributionAttempt)
class DistributionAttemptAdmin(BaseAdmin):
    list_display = ('created_at', 'status', 'profile', 'result')
