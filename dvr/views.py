from rest_framework import viewsets

from .serializers import ConversionSerializer, StreamSerializer
from .models import Stream, Conversion


class ConversionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Conversion.objects.all().order_by('-created_at')
    serializer_class = ConversionSerializer
    filter_fields = ('stream',)


class StreamViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    filter_fields = ('name',)