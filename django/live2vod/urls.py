from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from dvr.views import *
from dvr.schema import schema

from .views import check_streams

admin.site.site_header = "Open Multimedia"
admin.site.site_title = "Open"
admin.site.index_title = "Administración"
admin.site.site_url = None

router = routers.DefaultRouter()

# Model ViewSets
router.register(r'conversions', ConversionViewSet)
router.register(r'distribution_attempts', DistributionAttemptViewSet)
router.register(r'distribution_channels', DistributionChannelViewSet)
router.register(r'distribution_profiles', DistributionProfileViewSet)
router.register(r'streams', StreamViewSet)
router.register(r'scene_changes', SceneChangeViewSet)
router.register(r'scene_analysis', SceneAnalysisViewSet)
router.register(r'videos', VideoViewSet)
router.register(r'series', SeriesViewSet)
router.register(r'series_recurrences', SeriesRecurrenceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # path('webhooks/check_streams/', check_streams),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-docs/', get_swagger_view(title='DVR REST API Documentation')),
    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns \
      + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
      + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
