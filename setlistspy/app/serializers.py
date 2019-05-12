from django.db.models import Count, Max
from rest_framework import serializers
from setlistspy.app.models import Artist, DJ, Label, Setlist, Track, TrackPlay


class DJSerializer(serializers.ModelSerializer):
    class Meta:
        model = DJ
        fields = ('id', 'name')


class DJStatsSerializer(DJSerializer):
    b2b_collaborators = serializers.SerializerMethodField()
    number_of_setlists = serializers.SerializerMethodField()
    most_stacked_setlist = serializers.SerializerMethodField()
    top_artists = serializers.SerializerMethodField()
    top_labels = serializers.SerializerMethodField()

    class Meta:
        model = DJ
        fields = ('id', 'name', 'number_of_setlists', 'b2b_collaborators', 'most_stacked_setlist',
                  'top_artists', 'top_labels')

    def get_number_of_setlists(self, obj):
        '''Return number of non-empty setlists played by the DJ'''
        return obj.setlists.exclude(tracks=None).count()

    def get_b2b_collaborators(self, obj):
        '''Get list of other DJs this DJ has done sets with'''
        b2b_setlist_mixesdb_ids = obj.setlists.filter(b2b=True).values('mixesdb_id')
        b2b_dj_qs = DJ.objects.filter(
            pk__in=Setlist.objects.filter(mixesdb_id__in=b2b_setlist_mixesdb_ids).exclude(dj=obj)\
                   .values('dj__pk')
        )
        return DJSerializer(many=True, context=self.context).to_representation(b2b_dj_qs)

    def get_most_stacked_setlist(self, obj):
        annotated_setlist_qs = obj.setlists.all().annotate(Count('tracks'))
        max_num_tracks = annotated_setlist_qs.aggregate(Max('tracks__count'))['tracks__count__max']
        if max_num_tracks > 0:
            most_stacked_setlist = annotated_setlist_qs.filter(tracks__count=max_num_tracks).first()
            setlist_context = self.context
            setlist_context['num_tracks'] = max_num_tracks
            return SetlistSerializer(context=self.context).to_representation(instance=most_stacked_setlist)
        return None

    def get_top_artists(self, obj):
        return obj.setlists.values('tracks__artist__name').order_by('tracks__artist__name')\
            .annotate(count=Count('tracks__artist__name')).order_by('-count')[:25]

    def get_top_labels(self, obj):
        return obj.setlists.values('track_plays__label__name').order_by('track_plays__label__name')\
            .annotate(count=Count('track_plays__label__name')).order_by('-count')[:25]


class SetlistSerializer(serializers.ModelSerializer):
    dj = DJSerializer()
    num_tracks = serializers.SerializerMethodField()

    class Meta:
        model = Setlist
        fields = ('id', 'dj', 'title', 'mixesdb_id', 'b2b', 'num_tracks')

    def get_num_tracks(self, obj):
        if self.context.get('num_tracks'):
            return self.context.get('num_tracks')
        return obj.tracks.count()

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



