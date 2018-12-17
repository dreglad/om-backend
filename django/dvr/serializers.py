from rest_framework import serializers

from .models import *


class ConversionSerializer(serializers.ModelSerializer):
    stream_url = serializers.HyperlinkedRelatedField(source='stream', view_name='stream-detail', read_only=True)
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
    class Meta:
        model = Stream
        fields = ('id', 'name', 'slug', 'provider', 'metadata', 'provider_data')


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = (
            'id', 'stream', 'sources', 'start', 'end', 'file', 'images', 'duration',
            'status', 'progress', 'metadata', 'created_at', 'modified_at', 'result')


class SeriesRecurrenceSerializer(serializers.ModelSerializer):
    recurrence = serializers.CharField()
    class Meta:
        model = SeriesRecurrence
        fields = (
            'id', 'series', 'recurrence', 'start_time', 'end_time', 'start_date', 'end_date',
            'created_at', 'modified_at')


class SeriesRecurrenceInlineSerializer(SeriesRecurrenceSerializer):
    class Meta:
        model = SeriesRecurrence
        fields = ('id', 'recurrence', 'start_time', 'end_time', 'start_date', 'end_date')


class SeriesSerializer(serializers.ModelSerializer):
    recurrences = SeriesRecurrenceInlineSerializer(many=True)
    class Meta:
        model = Series
        fields = (
            'id', 'stream', 'name', 'recurrences', 'opening_sequence', 'closing_sequence', 'pause_sequence',
            'comeback_sequence', 'metadata', 'created_at', 'modified_at')


class DistributionChannelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DistributionChannel
        fields = ('type', 'active', 'metadata')


class DistributionAttemptSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DistributionAttempt
        fields = ('profile', 'created_at', 'status')


class DistributionProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DistributionProfile
        fields = ('channel', 'created_at')


class SceneChangeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SceneChange
        fields = ('id', 'time', 'value')


class SceneAnalysisSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SceneAnalysis
        fields = ('id', 'stream', 'start', 'end', 'status', 'progress', 'created_at')
