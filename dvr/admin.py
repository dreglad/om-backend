from django.contrib import admin
from .models import *


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'live_url', 'dvr_url')
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Conversion)
class ConversionAdmin(admin.ModelAdmin):
    pass
