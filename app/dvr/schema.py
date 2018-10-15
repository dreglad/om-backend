from datetime import datetime
from operator import itemgetter
from urllib.parse import urljoin

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.rest_framework.mutation import SerializerMutation
from graphene.relay import Node
from graphene import (
    ObjectType, Schema, String, DateTime, List, Int, Float, Field, Boolean
)
from rest_framework import serializers

from dvr.models import Video, Stream
from django.contrib.auth.models import User


class StreamRendition(ObjectType):
    name = String()


class StreamStore(ObjectType):
    name = String()
    start = DateTime()
    end = DateTime()
    current = Boolean()
    renditions = List(StreamRendition)
    playlist = String(start=DateTime(), duration=Float())
    thumbnail = String(date=DateTime(), max_width=Int())

    def resolve_playlist(self, info, start=None, duration=60):
        wseStreamingUrl, wseApplication = itemgetter(
            'wseStreamingUrl', 'wseApplication')(self.metadata)
        store, start, end = (0, 0, 0)
        return urljoin(wseStreamingUrl, (
            '{appplication}/{store}/playlist.m3u8?DVR&wowzadvrplayliststart={start}&wowzadvrplaylistduration={end}'.format(
                appplication=wseApplication,
                store=store,
                start=start,
                end=end)
            ))

    def resolve_thumbnail(self, date, max_width):
        return ''


class StreamNode(DjangoObjectType):
    streaming_url = String(resolver=lambda stream, info: stream.metadata.get('wseStreamingUrl'))
    stores = Field(List(StreamStore), current=Boolean())

    def resolve_stores(self, info):
        print('all provider data', self.provider_data)
        stores, current = itemgetter('stores', 'current_store_details')(self.provider_data)
        return stores and [
            StreamStore(
                name=name,
                start=current.get('start'),
                end=current.get('end'),
                renditions=[
                    StreamRendition(name=store['name'])
                    for store in stores
                    ])
            for name, stores in stores.items()
            ]

    class Meta:
        model = Stream
        filter_fields = ['id']
        interfaces = (Node, )


class VideoNode(DjangoObjectType):
    class Meta:
        model = Video
        filter_fields = {
            'stream': ['exact'],
            'status': ['exact', 'in'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
        interfaces = (Node,)


class Query(ObjectType):
    stream = Node.Field(StreamNode)
    streams = DjangoFilterConnectionField(StreamNode)

    video = Node.Field(VideoNode)
    videos = DjangoFilterConnectionField(VideoNode)


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('id', 'stream')


class VideoMutation(SerializerMutation):
    class Meta:
        serializer_class = VideoSerializer


class Mutation(ObjectType):
    serializer = VideoMutation.Field()


schema = Schema(query=Query, mutation=Mutation)
