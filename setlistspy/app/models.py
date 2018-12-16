from django.db import models
from setlistspy.app.base_model import BaseSetSpyModel


class DJ(BaseSetSpyModel):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, unique=True)
    xml_md5 = models.CharField(max_length=32, default='')
    last_check_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['last_check_time']),
            models.Index(fields=['name', 'last_check_time'])
        ]

    def __str__(self):
        return f'{self.name}'


class Setlist(BaseSetSpyModel):
    dj = models.ForeignKey(DJ, on_delete=models.PROTECT, related_name='setlists')
    title = models.CharField(max_length=255)
    mixesdb_id = models.IntegerField()
    mixesdb_mod_time = models.DateTimeField()
    xml_sha1 = models.CharField(max_length=31, null=True)
    b2b = models.NullBooleanField('Other DJs on deck', null=True)

    class Meta:
        indexes = [
            models.Index(fields=['dj']),
            models.Index(fields=['mixesdb_mod_time']),
            models.Index(fields=['dj', 'mixesdb_mod_time'])
        ]
        unique_together = (
            ('dj', 'mixesdb_id'),
        )

    def __str__(self):
        return f'{self.title}'


class Artist(BaseSetSpyModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.name}'


class Label(BaseSetSpyModel):
    name = models.CharField(max_length=255, unique=True)
    discogs_id = models.IntegerField(null=True)

    def __str__(self):
        return f'{self.name}'


class Track(BaseSetSpyModel):
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    setlists = models.ManyToManyField(
        Setlist, through="TrackPlay", related_name="tracks")

    def __str__(self):
        return f'{self.artist.name} - {self.title}'

    class Meta:
        indexes = [
            models.Index(fields=['artist']),
            models.Index(fields=['title']),
            models.Index(fields=['artist', 'title']),
        ]
        unique_together = (
            ('artist', 'title'),
        )


class TrackPlay(BaseSetSpyModel):
    track = models.ForeignKey(Track, related_name='plays', on_delete=models.PROTECT)
    setlist = models.ForeignKey(Setlist, related_name='track_plays', on_delete=models.PROTECT)
    set_order = models.IntegerField()
    label = models.ForeignKey(Label, null=True, related_name='track_plays', on_delete=models.PROTECT)

    class Meta:
        indexes = [
            models.Index(fields=['track']),
            models.Index(fields=['setlist']),
            models.Index(fields=['track', 'setlist']),
        ]
        unique_together = (
            ('setlist', 'set_order'),
        )

    def __str__(self):
        return f'{self.setlist.title} - {self.set_order}. {self.track.artist.name} - {self.track.title}'