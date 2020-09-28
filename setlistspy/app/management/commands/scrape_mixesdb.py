from django.core.management.base import BaseCommand
from lib.djs import *
from setlistspy.app.models import *

class Migrator:
    def __init__(self):
        self.db = get_db()
        self.models = [DJ, Setlist, Artist, Label, Track, TrackPlay]

    def seed_db(self, drop_tables=False, starting_url=False):
        seeder = DJsCrawler(starting_url, True, True)
        seeder.crawl_categories_pages()


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         '--everything',
    #         action='store_true',
    #         dest='everything',
    #         default=False,
    #         help='Scrape the site for the entire database',
    #     )
    #     # Note: Mixesdb.com has removed the export page from its site, so no further data can be seeded using xml dumps
    #     # Scraping the list of DJs using webdriver still works, however.
    #     parser.add_argument(
    #         '--djs',
    #         action='store_true',
    #         dest='djs',
    #         default=False,
    #         help='Scrape the DJs',
    #     )
    #     # Deprecated
    #     parser.add_argument(
    #         '--setlists',
    #         action='store_true',
    #         dest='setlists',
    #         default=False,
    #         help='Scrape the setlist data for all DJs in the database',
    #     )

    def handle(self, *args, **options):
        # from models import *
        # from crawler.djs import *
        #
        # class migrator:
        #     def __init__(self):
        #         self.db = get_db()
        #         self.models = [DJ, Setlist, Artist, Label, Track, Track_Setlist_Link]
        migrator = Migrator()
        migrator.seed_db()
