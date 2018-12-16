import rest_framework_filters as filters
from rest_framework_filters.filters import BooleanFilter

from setlistspy.app.models import Artist, DJ, Label, Setlist, Track, TrackPlay


class ArtistFilter(filters.FilterSet):

    class Meta:
        model = Artist
        fields = {
            'name': ['exact', 'in', 'startswith', 'icontains'],
        }


class LabelFilter(filters.FilterSet):

    class Meta:
        model = Label
        fields = {
            'name': ['exact', 'in', 'startswith', 'icontains'],
            'track_plays__setlist__dj__name': ['exact', 'in', 'startswith', 'icontains'],
        }


class DJFilter(filters.FilterSet):

    class Meta:
        model = DJ
        fields = {
            'name': ['exact', 'in', 'startswith', 'icontains'],
            'setlists__track_plays__label__name': ['exact', 'in', 'startswith', 'icontains'],
        }


class SetlistFilter(filters.FilterSet):
    empty = BooleanFilter(field_name='empty', method='filter_empty')

    def filter_empty(self, qs, name, value):
        return qs.filter(track_plays__isnull=value)

    class Meta:
        model = Setlist
        fields = {
            'dj__name': ['exact', 'in', 'startswith', 'icontains'],
            'title': ['exact', 'in', 'startswith', 'icontains'],
            'mixesdb_id': ['exact', 'in'],
            'b2b': ['exact'],
        }


class TrackFilter(filters.FilterSet):

    class Meta:
        model = Track
        fields = {
            'artist__name': ['exact', 'in', 'startswith', 'icontains'],
            'title': ['exact', 'in', 'startswith', 'icontains'],
            'setlists__title': ['exact', 'in', 'startswith', 'icontains'],
            'setlists__dj__name': ['exact', 'in', 'startswith', 'icontains'],
            'plays__label__name': ['exact', 'in', 'startswith', 'icontains'],
            'plays__set_order': ['exact', 'in'],
            'plays__label__name': ['exact', 'in', 'startswith', 'icontains'],
        }


class TrackPlayFilter(filters.FilterSet):

    class Meta:
        model = TrackPlay
        fields = {
            'label__name': ['exact', 'in', 'startswith', 'icontains'],
            'track__artist__name': ['exact', 'in', 'startswith', 'icontains'],
            'track__title': ['exact', 'in', 'startswith', 'icontains'],
            'setlist__title': ['exact', 'in', 'startswith', 'icontains'],
            'setlist__dj__name': ['exact', 'in', 'startswith', 'icontains'],
            'set_order': ['exact', 'in']
        }