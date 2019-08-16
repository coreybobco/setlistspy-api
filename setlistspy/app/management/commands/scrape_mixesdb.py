from django.core.management.base import BaseCommand
from lib.crawler import MixesDBCrawler


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--everything',
            action='store_true',
            dest='everything',
            default=False,
            help='Scrape the site for the entire database',
        )
        # Note: Mixesdb.com has removed the export page from its site, so no further data can be seeded using xml dumps
        # Scraping the list of DJs using webdriver still works, however.
        parser.add_argument(
            '--djs',
            action='store_true',
            dest='djs',
            default=False,
            help='Scrape the DJs',
        )
        # Deprecated
        # parser.add_argument(
        #     '--setlists',
        #     action='store_true',
        #     dest='setlists',
        #     default=False,
        #     help='Scrape the setlist data for all DJs in the database',
        # )

    def handle(self, *args, **options):
        crawler = MixesDBCrawler()
        if options['everything'] or options['djs']:
            crawler.crawl_all_artist_categories()
        if options['everything'] or options['setlists']:
            crawler.crawl_all_setlists_by_all_djs()
