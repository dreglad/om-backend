from rest_framework import serializers

from .models import *


class ConversionSerializer(serializers.ModelSerializer):
    stream_url = serializers.HyperlinkedRelatedField(source='stream', view_name='stream-detail', read_only=True)
    # url = serializers.HyperlinkedIdentityField(view_name='conversion-detail', read_only=True)
    class Meta:
        model = Conversion
        fields = (
            'id', 'created_at', 'stream_url', 'dvr_store', 'start', 'duration',
            'end', 'status', 'result', 'stream', 'progress', 'metadata',
        )


class StreamListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='stream-detail', read_only=True)
    class Meta:
        model = Stream
        fields = ('id', 'slug', 'url', 'name', 'provider', 'metadata')


class StreamDetailSerializer(serializers.HyperlinkedModelSerializer):
    # provider_data = serializers.JSONField(read_only=True)
    class Meta:
        model = Stream
        fields = ('id', 'name', 'slug', 'provider', 'metadata', 'provider_data')


class VideoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Video
        fields = ('id', 'status', 'conversions', 'metadata')


class DistributionChannelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DistributionChannel
        fields = ('type', 'active', 'metadata')


class DistributionAttemptSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DistributionAttempt
        fields = ('channel', 'created_at', 'status')
