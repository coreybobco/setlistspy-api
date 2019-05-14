from django.db.models import Case, Count, Max, OuterRef, Sum, When
from rest_framework import serializers
from setlistspy.app.models import Artist, DJ, Label, Setlist, Track, TrackPlay


class DJSerializer(serializers.ModelSerializer):
    class Meta:
        model = DJ
        fields = ('id', 'name')

class DJPlayCountSerializer(DJSerializer):
    play_count = serializers.SerializerMethodField()

    class Meta:
        model = DJ
        fields = ('id', 'name', 'play_count')

    def get_play_count(self, obj):
        if self.context.get('play_counts', None):
            return self.context['play_counts'].get(obj.pk, None)
        return None


class DJStatsSerializer(DJSerializer):
    b2b_collaborators = serializers.SerializerMethodField(read_only=True)
    number_of_setlists = serializers.SerializerMethodField(read_only=True)
    most_stacked_setlist = serializers.SerializerMethodField(read_only=True)
    top_played_artists = serializers.SerializerMethodField(read_only=True)
    top_played_labels = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DJ
        fields = ('id', 'name', 'number_of_setlists', 'b2b_collaborators', 'most_stacked_setlist',
                  'top_played_artists', 'top_played_labels')

    def get_number_of_setlists(self, obj):
        '''Return number of non-empty setlists played by the DJ'''
        return obj.setlists.exclude(tracks=None).count()

    def get_b2b_collaborators(self, obj):
        '''Get list of other DJs this DJ has done sets with'''
        b2b_setlist_mixesdb_ids = obj.setlists.filter(b2b=True).values('mixesdb_id')
        b2b_dj_qs = DJ.objects.filter(
            pk__in=Setlist.objects.filter(mixesdb_id__in=b2b_setlist_mixesdb_ids).exclude(dj=obj).values('dj')
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

    def get_top_played_artists(self, obj):
        setlists_qs = obj.setlists.values('tracks__artist').order_by('tracks__artist')\
            .annotate(count=Count('tracks__artist')).order_by('-count')[:25]
        artist_play_counts = {
            setlist['tracks__artist']: setlist['count']
            for setlist in setlists_qs
        }
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(artist_play_counts.keys())])
        top_artists_qs = Artist.objects.filter(pk__in=artist_play_counts.keys()).order_by(preserved_order)
        artist_context = self.context
        artist_context['play_counts'] = artist_play_counts
        return ArtistPlayCountSerializer(many=True, context=artist_context).to_representation(top_artists_qs)

    def get_top_played_labels(self, obj):
        setlists_qs = obj.setlists.values('track_plays__label').order_by('track_plays__label')\
            .annotate(count=Count('track_plays__label')).order_by('-count')[:25]
        label_play_counts = {
            setlist['track_plays__label']: setlist['count']
            for setlist in setlists_qs
        }
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(label_play_counts.keys())])
        top_artists_qs = Label.objects.filter(pk__in=label_play_counts.keys()).order_by(preserved_order)
        label_context = self.context
        label_context['play_counts'] = label_play_counts
        return LabelPlayCountSerializer(many=True, context=label_context).to_representation(top_artists_qs)


class SetlistSerializer(serializers.ModelSerializer):
    dj = DJSerializer()
    num_tracks = serializers.SerializerMethodField(read_only=True)

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


class ArtistStatsSerializer(serializers.ModelSerializer):
    total_plays = serializers.SerializerMethodField(read_only=True)
    top_djs = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Artist
        fields = ('id', 'name', 'total_plays', 'top_djs')

    def get_total_plays(self, obj):
        return obj.tracks.annotate(play_count=Count('plays')).aggregate(total_plays=Sum('play_count'))['total_plays']

    def get_top_djs(self, obj):
        # Group the cumulative track plays on a label by the djs that played the tracks and order by the play count
        tracks_qs = obj.tracks.values('plays__setlist__dj').order_by('plays__setlist__dj')\
            .annotate(count=Count('plays__setlist__dj')).order_by('-count')[:25]
        dj_play_counts = {
            track['plays__setlist__dj']: track['count']
            for track in tracks_qs
        }
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(dj_play_counts.keys())])
        top_djs_qs = DJ.objects.filter(pk__in=dj_play_counts.keys()).order_by(preserved_order)
        dj_context = self.context
        dj_context['play_counts'] = dj_play_counts
        return DJPlayCountSerializer(many=True, context=dj_context).to_representation(top_djs_qs)


class ArtistPlayCountSerializer(DJSerializer):
    play_count = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ('id', 'name', 'play_count')

    def get_play_count(self, obj):
        if self.context.get('play_counts', None):
            return self.context['play_counts'].get(obj.pk, None)
        return None


class BaseLabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Label
        fields = ('id', 'name')

class LabelSerializer(BaseLabelSerializer):
    total_plays = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Label
        fields = ('id', 'name', 'total_plays')

    @classmethod
    def setup_queryset(cls, queryset, context):
        queryset = queryset.annotate(total_plays=Count('track_plays'))
        return queryset

    def get_total_plays(self, obj):
        if hasattr(obj, 'total_plays'):
            return obj.total_plays
        return obj.track_plays.count()


class LabelPlayCountSerializer(LabelSerializer):
    play_count = serializers.SerializerMethodField()

    class Meta:
        model = Label
        fields = ('id', 'name', 'play_count')

    def get_play_count(self, obj):
        if self.context.get('play_counts', None):
            return self.context['play_counts'].get(obj.pk, None)
        return None


class LabelStatsSerializer(LabelSerializer):
    top_djs = serializers.SerializerMethodField(read_only=True)
    top_played_artists = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Label
        fields = ('id', 'name', 'total_plays', 'top_djs', 'top_played_artists')

    def get_top_djs(self, obj):
        # Group the cumulative track plays on a label by the djs that played the tracks and order by the play count
        plays_qs = obj.track_plays.values('setlist__dj').order_by('setlist__dj')\
            .annotate(count=Count('setlist__dj')).order_by('-count')[:25]
        dj_play_counts = {
            play['setlist__dj']: play['count']
            for play in plays_qs
        }
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(dj_play_counts.keys())])
        top_djs_qs = DJ.objects.filter(pk__in=dj_play_counts.keys()).order_by(preserved_order)
        dj_context = self.context
        dj_context['play_counts'] = dj_play_counts
        return DJPlayCountSerializer(many=True, context=dj_context).to_representation(top_djs_qs)

    def get_top_played_artists(self, obj):
        # Group the cumulative track plays on a label by track artists and order by the play count
        plays_qs = obj.track_plays.values('track__artist').order_by('track__artist__name') \
                   .annotate(count=Count('track__artist__name')).order_by('-count')[:25]
        artist_play_counts = {
            play['track__artist']: play['count']
            for play in plays_qs
        }
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(artist_play_counts.keys())])
        top_artists_qs = Artist.objects.filter(pk__in=artist_play_counts.keys()).order_by(preserved_order)
        artist_context = self.context
        artist_context['play_counts'] = artist_play_counts
        return ArtistPlayCountSerializer(many=True, context=artist_context).to_representation(top_artists_qs)


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
    label = BaseLabelSerializer()

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



