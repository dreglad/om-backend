from rest_framework import serializers

from .models import Conversion, Stream


class ConversionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Conversion
        fields = ('stream', 'start', 'duration', 'end', 'status')


class StreamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Stream
        fields = ('name', 'slug', 'live_url', 'dvr_url')
