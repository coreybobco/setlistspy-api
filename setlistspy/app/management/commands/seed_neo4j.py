import logging
from django.core.management.base import BaseCommand
from setlistspy.app.models import Setlist, Track, Track_Setlist_Link
from neomodel import db, StructuredNode, StringProperty, UniqueIdProperty, config

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        # Named (optional) arguments
        parser.add_argument(
            '--everything',
            action='store_true',
            dest='everything',
            default=False,
            help='Scrape the site for the entire database',
        )
        parser.add_argument(
            '--djs',
            action='store_true',
            dest='djs',
            default=False,
            help='Scrape the DJs',
        )
        parser.add_argument(
            '--setlists',
            action='store_true',
            dest='setlists',
            default=False,
            help='Scrapet the setlist data for all DJs in the database',
        )
        return

    def handle(self, *args, **options):
        db.set_connection('bolt://neo4j:pyneo@localhost:7687')
        config.DATABASE_URL = 'bolt://py2neo:py2neo@localhost:7687'
        print(options)
        track_iterator = Track.objects.select_related(
            'artist').all().iterator()
        for track in track_iterator:
            try:
                track_node = Track_Node.nodes.get(uid=track.id)
                # print(track.title)
                # print(track.artist.name)
            except Track_Node.DoesNotExist:
                print(track.id)
                track_node = Track_Node(uid=track.id, title=track.title)
                track_node.save()
                try:
                    artist_node = Artist_Node.nodes.get(name=track.artist.name)
                except Artist_Node.DoesNotExist:
                    artist_node = Artist_Node(name=track.artist.name)
                    artist_node.save()
                track_node.artist.connect(artist_node)
        # Todo: finish rewerite
        track_setlist_link_iterator = Track_Setlist_Link.objects.select_related('track').select_related('setlist').all().iterator()
        for track_setlist_link in track_setlist_link_iterator:
            try:
                track_node = Track_Node.nodes.get(uid=track_setlist_link.track.id)
            except Track_Node.DoesNotExist:
                track_node = Track_Node(uid=track.id, title=track.title, artist=)
        track_setlist_link = Track_Setlist_Link
        setlist_iterator = Setlist.objects.all().iterator()
        for setlist in setlist_iterator:

        if options['everything'] or options['djs']:
            djc = DJCrawler()
            djc.crawl()
        if options['everything'] or options['setlists']:
            slc = SetlistCrawler()
            slc.crawl()


class Artist_Node(StructuredNode):
    name = StringProperty(unique_index=True)


class Track_Setlist_Link_Node(StructuredNode):
    uid = UniqueIdProperty()
    title = StringProperty()
    artist = StringProperty()
