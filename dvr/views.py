from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.generics import get_object_or_404  
from rest_framework.response import Response  
import rest_framework_filters as filters


from .serializers import *
from .models import *


class ConversionViewSet(viewsets.ModelViewSet):
    """
    Conversion API endpoint.
    """
    queryset = Conversion.objects.all()
    serializer_class = ConversionSerializer
    filter_fields = ('stream',)


class StreamViewSet(viewsets.ModelViewSet):
    """
    Stream API endpoint.
    """
    queryset = Stream.objects.all()
    serializer_class = StreamListSerializer
    detail_serializer_class = StreamDetailSerializer
    filter_fields = ('name', 'provider')

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = self.detail_serializer_class
        return super(StreamViewSet, self).retrieve(request, *args, **kwargs)


class VideoViewSet(viewsets.ModelViewSet):
    """
    Video API endpoint.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    filter_fields = ('conversions',)


class DistributionAttemptViewSet(viewsets.ModelViewSet):
    """
    DistributionAttempt API endpoint.
    """
    queryset = DistributionAttempt.objects.all()
    serializer_class = DistributionAttemptSerializer
    filter_fields = ('channel', 'video__conversions__stream')


class DistributionChannelViewSet(viewsets.ModelViewSet):
    """
    DistributionChannel API endpoint.
    """
    queryset = DistributionChannel.objects.all()
    serializer_class = DistributionChannelSerializer
    filter_fields = ('name',)


class DistributionProfileViewSet(viewsets.ModelViewSet):
    """
    DistributionProfile API endpoint.
    """
    queryset = DistributionProfile.objects.all()
    serializer_class = DistributionProfileSerializer
    filter_fields = ('name',)


class SceneChangeFilter(filters.FilterSet):
    """
    SceneChange API endpoint filter.
    """
    class Meta:
        model = SceneChange
        fields = {
          'scene_analysis__stream': ['exact'],
          'time': ['exact', 'lt', 'gt', 'lte', 'gte'],
          'value': ['exact', 'lt', 'gt', 'lte', 'gte'],
        }


class SceneChangeViewSet(viewsets.ModelViewSet):
    """
    SceneChange API endpoint.
    """
    queryset = SceneChange.objects.all()
    serializer_class = SceneChangeSerializer
    filter_class = SceneChangeFilter


class SceneAnalysisViewSet(viewsets.ModelViewSet):
    """
    SceneAnalysis API endpoint.
    """
    queryset = SceneAnalysis.objects.all()
    serializer_class = SceneAnalysisSerializer
    filter_fields = ('stream',)

