from datetime import datetime

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.rest_framework.mutation import SerializerMutation
from graphene.relay import Node
from graphene import ObjectType, Schema, String, DateTime, List, Field, Boolean
# from graphene.types.datetime import DateTime
from rest_framework import serializers

from dvr.models import Video, Stream
from django.contrib.auth.models import User


class StreamStore(ObjectType):
    name = String()
    start = DateTime()
    end = DateTime()


class StreamRendition(ObjectType):
    name = String()
    stores = List(StreamStore)


class StreamNode(DjangoObjectType):
    renditions = Field(List(StreamRendition), current=Boolean())

    def resolve_renditions(self, info):
        print('all provider data', self.provider_data)
        stores = self.provider_data.get('stores')
        if stores:
            print('tiene;', stores)
            return [
                StreamRendition(
                    name=name,
                    stores=[
                        StreamStore(
                            name=store['name'],
                            start=datetime.fromtimestamp(store.get('utcStart', 0) / 1000),
                            end=datetime.fromtimestamp(store.get('utcEnd', 0) / 1000)
                        )
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
