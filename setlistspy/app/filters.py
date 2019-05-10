import rest_framework_filters as filters
from rest_framework_filters.filters import BooleanFilter, CharFilter

from setlistspy.app.models import Artist, DJ, Label, Setlist, Track, TrackPlay


class ArtistFilter(filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='iexact')

    class Meta:
        model = Artist
        fields = {
            'name': ['iexact', 'in', 'startswith', 'icontains'],
        }


class LabelFilter(filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='iexact')
    track_plays = filters.RelatedFilter('TrackPlayFilter', field_name='track_plays', queryset=TrackPlay.objects.all())

    class Meta:
        model = Label
        fields = {
            'name': ['iexact', 'in', 'startswith', 'icontains'],
        }


class DJFilter(filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='iexact')
    setlists = filters.RelatedFilter('SetlistFilter', field_name='setlists', queryset=Setlist.objects.all())

    class Meta:
        model = DJ
        fields = {
            'name': ['iexact', 'in', 'startswith', 'icontains'],
        }


class SetlistFilter(filters.FilterSet):
    title = CharFilter(field_name='title', lookup_expr='iexact')
    dj = filters.RelatedFilter('DJFilter', field_name='dj', queryset=DJ.objects.all())
    track_plays = filters.RelatedFilter('TrackPlayFilter', field_name='track_plays', queryset=TrackPlay.objects.all())
    empty = BooleanFilter(field_name='empty', method='filter_empty')

    def filter_empty(self, qs, name, value):
        return qs.filter(track_plays__isnull=value)

    class Meta:
        model = Setlist
        fields = {
            # 'dj__name': ['iexact', 'in', 'startswith', 'icontains'],
            'title': ['iexact', 'in', 'startswith', 'icontains'],
            'mixesdb_id': ['exact', 'in'],
            'b2b': ['exact'],
        }


class TrackFilter(filters.FilterSet):
    title = CharFilter(field_name='title', lookup_expr='iexact')
    artist = filters.RelatedFilter('ArtistFilter', field_name='artist', queryset=Artist.objects.all())
    setlists = filters.RelatedFilter('SetlistFilter', field_name='setlists', queryset=Setlist.objects.all())
    plays = filters.RelatedFilter('TrackPlayFilter', field_name='plays', queryset=TrackPlay.objects.all())

    class Meta:
        model = Track
        fields = {
            'title': ['iexact', 'in', 'startswith', 'icontains'],
        }


class TrackPlayFilter(filters.FilterSet):
    label = filters.RelatedFilter('LabelFilter', field_name='label', queryset=Label.objects.all())
    track = filters.RelatedFilter('TrackFilter', field_name='track', queryset=Track.objects.all())
    setlist = filters.RelatedFilter('SetlistFilter', field_name='setlist', queryset=Setlist.objects.all())

    class Meta:
        model = TrackPlay
        fields = {
            'set_order': ['exact', 'in']
        }