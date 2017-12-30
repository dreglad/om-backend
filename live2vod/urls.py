"""live2vod URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

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
router.register(r'schene_changes', SceneChangeViewSet)
router.register(r'videos', VideoViewSet)

# Non-model ViewSets
# router.register(r'stream_store', StreamStoreViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
