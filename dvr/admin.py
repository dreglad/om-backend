from django import forms
from django.contrib import admin
from django.contrib.postgres.fields import HStoreField
from django_admin_json_editor import JSONEditorWidget
from django.utils.translation import ugettext_lazy as _

from .models import *


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'metadata')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)

    SCHEMA = {
        'type': 'object',
        'title': _('metadata'),
    }
    formfield_overrides = {
        HStoreField: {'widget': JSONEditorWidget(SCHEMA) }
    }


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
class ConversionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'status', 'stream', 'start', 'duration')
    autocomplete_fields = ('stream',)
    form = ConversionForm

    # formfield_overrides = {
    #     models.DateTimeField: {'widget': MicroDateTimeInput()},
    # }


# class ConversionInline(admin.TabularInline):
#     model = Conversion

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    pass


@admin.register(DistributionChannel)
class DistributionChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'active', 'created_at', 'metadata')


@admin.register(DistributionAttempt)
class DistributionAttemptAdmin(admin.ModelAdmin):
    pass

