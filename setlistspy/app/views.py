from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework_filters.backends import ComplexFilterBackend
from rest_framework.response import Response

from setlistspy.app.mixins import SetSpyListModelMixin
from setlistspy.app.models import Artist, DJ, Label, Setlist, Track, TrackPlay
from setlistspy.app.filters import ArtistFilter, DJFilter, LabelFilter, TrackFilter, TrackPlayFilter, SetlistFilter
from setlistspy.app.serializers import (
    ArtistSerializer,
    ArtistStatsSerializer,
    DJSerializer,
    DJStatsSerializer,
    LabelSerializer,
    LabelStatsSerializer,
    TrackSerializer,
    TrackPlaySerializer,
    TrackStatsSerializer,
    SetlistSerializer
)

# CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class DJViewSet(SetSpyListModelMixin, viewsets.ModelViewSet):
    serializer_class = DJSerializer
    queryset = DJ.objects.all()
    filter_backends = (ComplexFilterBackend, OrderingFilter)
    filter_class = DJFilter

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'stats':
            return DJStatsSerializer
        return super().get_serializer_class(*args, **kwargs)

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context=self.get_serializer_context(), **kwargs)
        return Response(serializer.data)


class SetlistViewSet(SetSpyListModelMixin, viewsets.ModelViewSet):
    serializer_class = SetlistSerializer
    queryset = Setlist.objects.all()
    filter_backends = (ComplexFilterBackend, OrderingFilter)
    filter_class = SetlistFilter

    def get_queryset(self):
        return super(SetlistViewSet, self).get_queryset()\
                .select_related("dj")\
                .prefetch_related("tracks__artist").distinct()


class TrackViewSet(SetSpyListModelMixin, viewsets.ModelViewSet):
    serializer_class = TrackSerializer
    queryset = Track.objects.all()
    filter_backends = (ComplexFilterBackend, OrderingFilter)
    filter_class = TrackFilter

    def get_queryset(self):
        return super(TrackViewSet, self).get_queryset()\
            .select_related("artist").distinct()\
            .order_by("artist__name", "title")

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'stats':
            return TrackStatsSerializer
        return super().get_serializer_class(*args, **kwargs)

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context=self.get_serializer_context(), **kwargs)
        return Response(serializer.data)


class ArtistViewSet(SetSpyListModelMixin, viewsets.ModelViewSet):
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()
    filter_backends = (ComplexFilterBackend, OrderingFilter)
    filter_class = ArtistFilter

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'stats':
            return ArtistStatsSerializer
        return super().get_serializer_class(*args, **kwargs)

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context=self.get_serializer_context(), **kwargs)
        return Response(serializer.data)


class LabelViewSet(SetSpyListModelMixin, viewsets.ModelViewSet):
    serializer_class = LabelSerializer
    queryset = Label.objects.all()
    filter_backends = (ComplexFilterBackend, OrderingFilter)
    filter_class = LabelFilter

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'stats':
            return LabelStatsSerializer
        return super().get_serializer_class(*args, **kwargs)

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context=self.get_serializer_context(), **kwargs)
        return Response(serializer.data)


class TrackPlayViewSet(SetSpyListModelMixin, viewsets.ModelViewSet):
    serializer_class = TrackPlaySerializer
    queryset = TrackPlay.objects.all()
    filter_backends = (ComplexFilterBackend, OrderingFilter)
    filter_class = TrackPlayFilter

