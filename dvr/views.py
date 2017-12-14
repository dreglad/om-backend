from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.generics import get_object_or_404  
from rest_framework.response import Response  

from .serializers import *
from .models import *


class ConversionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Conversion.objects.all()
    serializer_class = ConversionSerializer
    filter_fields = ('stream',)


class StreamViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Stream.objects.all()
    serializer_class = StreamListSerializer
    detail_serializer_class = StreamDetailSerializer
    filter_fields = ('name', 'provider')

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = self.detail_serializer_class
        return super(StreamViewSet, self).retrieve(request, *args, **kwargs)

    # @detail_route(methods=['get']):


class VideoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    filter_fields = ('conversions',)


class DistributionAttemptViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = DistributionAttempt.objects.all()
    serializer_class = DistributionAttemptSerializer
    filter_fields = ('channel', 'video__conversions__stream')


class DistributionChannelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = DistributionChannel.objects.all()
    serializer_class = DistributionChannelSerializer
    filter_fields = ('name',)


class DistributionProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = DistributionProfile.objects.all()
    serializer_class = DistributionProfileSerializer
    filter_fields = ('name',)
