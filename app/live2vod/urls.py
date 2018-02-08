from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from dvr.views import *

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
# router.register(r'videos', VideoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-docs/', get_swagger_view(title='DVR REST API Documentation'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns \
      + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
      + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
