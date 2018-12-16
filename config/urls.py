from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from setlistspy.app.views import ArtistViewSet, DJViewSet, LabelViewSet, TrackViewSet, TrackPlayViewSet, SetlistViewSet

router = routers.DefaultRouter()
router.register('artists', ArtistViewSet)
router.register('djs', DJViewSet)
router.register('labels', LabelViewSet)
router.register(r'setlists', SetlistViewSet)
router.register(r'tracks', TrackViewSet)
router.register(r'plays', TrackPlayViewSet)


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]