from rest_framework import serializers
from setlistspy.app.models import Artist, DJ, Label, Setlist, Track, TrackPlay


class DJSerializer(serializers.ModelSerializer):
    class Meta:
        model = DJ
        fields = ('id', 'name')


class SetlistSerializer(serializers.ModelSerializer):
    dj = DJSerializer()

    class Meta:
        model = Setlist
        fields = ('id', 'dj', 'title', 'mixesdb_id', 'b2b')

    @classmethod
    def setup_queryset(cls, queryset, context):
        queryset = queryset.select_related("dj")
        return queryset


class ArtistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Artist
        fields = ('id', 'name')

class LabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Label
        fields = ('id', 'name')


class TrackSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()

    class Meta:
        model = Track
        fields = ('id', 'artist', 'title')

    @classmethod
    def setup_queryset(cls, queryset, context):
        queryset = queryset.select_related('artist')
        return queryset


class TrackStatsSerializer(TrackSerializer):
    setlists = SetlistSerializer(many=True)

    class Meta:
        model = Track
        fields = ('id', 'artist', 'title', 'setlists')

    @classmethod
    def setup_queryset(cls, queryset, context):
        queryset = queryset.select_related(
            'artist'
        ).prefetch_related(
            'setlists__dj'
        )
        return queryset


class TrackPlaySerializer(serializers.ModelSerializer):
    track = TrackSerializer()
    setlist = SetlistSerializer()
    label = LabelSerializer()

    class Meta:
        model = TrackPlay
        fields = ('id', 'set_order', 'track', 'setlist', 'label')

    @classmethod
    def setup_queryset(cls, queryset, context):
        queryset = queryset.select_related(
            'label',
            'track__artist',
            'setlist__dj'
        )
        return queryset



