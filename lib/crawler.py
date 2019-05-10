import hashlib
import re
from collections import defaultdict
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
import requests
import urllib.parse
import xmltodict
from datetime import timedelta
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from setlistspy.app.models import DJ, Setlist, Artist, Track, Label, TrackPlay

class MixesDBCrawler:
    """ Crawls Mixesdb.com, extracting, cleaning, and saving data as DJs, setlists, tracks, artists, & labels"""
    base_url = "http://www.mixesdb.com"
    artist_category_list_url = base_url + "/w/Category:Artist"
    current_crawler_url = None
    current_html = None
    # Use PhantomJS instead of Chrome headless because Chrome converts raw XML into XHTML.
    driver = webdriver.Remote(command_executor='http://phantomjs:4444/wd/hub',
                              desired_capabilities=webdriver.DesiredCapabilities.PHANTOMJS)

    def crawl_all_artist_categories(self):
        """Crawl all 'artists' and save them to the database as DJs. (Mixesdb does not have a DJ category.)"""
        self.current_crawler_url = self.artist_category_list_url
        while self.current_crawler_url:
            print(self.current_crawler_url)
            dj_data = self.crawl_artist_categories_page(self.current_crawler_url)
            self.save_djs_to_db(dj_data)
            self.seek_next_artist_category_page()
        print("Crawled DJs")

    def crawl_artist_categories_page(self, page_url):
        """Extract the DJ names and link urls on an individual page (max: 200)"""
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73'}
        page = requests.get(page_url, headers=headers)
        self.current_html = html.fromstring(page.content)
        artist_category_names = self.current_html.xpath("//ul[@id='catSubcatsList']//a/text()")
        artist_category_urls = self.current_html.xpath("//ul[@id='catSubcatsList']//a/@href")
        artist_category_urls = list(map(lambda url: f'http://www.mixesdb.com{url}', artist_category_urls))
        dj_data = dict(zip(artist_category_names, artist_category_urls))
        return dj_data

    def save_djs_to_db(self, dj_data):
        with transaction.atomic():
            for dj_name, dj_url in dj_data.items():
                try:
                    dj = DJ.objects.get(url=dj_url)
                except DJ.DoesNotExist:
                    dj = DJ.objects.create(name=dj_name, url=dj_url)

    def seek_next_artist_category_page(self):
        """Find the url of the next page of results"""
        next_url_hrefs = self.current_html.xpath(
            "//div[@class='listPagination'][1]/a[contains(text(), 'next')]/@href")
        next_url_hrefs = [href for href in next_url_hrefs if href is not None]
        self.current_crawler_url = self.base_url + next_url_hrefs[0] if len(next_url_hrefs) else False

    def crawl_all_setlists_by_all_djs(self):
        """ Iterate through all djs whose setlist XML hasn't been checked recently & save setlist data"""
        two_days_ago = timezone.now() - timedelta(days=2)
        dj_iterator = DJ.objects.filter(
            Q(last_check_time__lte=two_days_ago) |
            Q(last_check_time__isnull=True)
        ).iterator()
        for dj in dj_iterator:
            self.crawl_all_setlists_by_dj(dj)

    def crawl_all_setlists_by_dj(self, dj):
        """Get XML dump, check if still valid, and then create/update relevant instances"""
        response_xml = self.get_xml_from_setlists_by_dj(dj)
        if response_xml:
            self.check_xml_md5(dj, response_xml)
            setlists_xml_dict = xmltodict.parse(response_xml) \
                .get('mediawiki', defaultdict(lambda: None)).get('page')
            if setlists_xml_dict:
                self.save_setlists(setlists_xml_dict, dj)

    def get_xml_from_setlists_by_dj(self, dj):
        """Use Selenium to get XML dump for all setlists of one individual DJ"""
        self.driver.get("http://www.mixesdb.com/db/index.php?title=Special:Export")
        # Uncheck box so XML returned as response, not as file download
        self.driver.find_element_by_name("wpDownload").click()
        category_input = self.driver.find_element_by_name("catname")
        dj_category_name = urllib.parse.unquote(dj.url[25:])  # e.g. Category:Helena_Hauff
        print(dj_category_name.encode('utf-8', 'replace'))
        category_input.send_keys(dj_category_name)
        category_input.send_keys(Keys.RETURN)  # Fills textarea with list of DJ sets
        setlists_url_paths = self.driver.find_element_by_tag_name("textarea").get_attribute("value")
        if setlists_url_paths:
            self.driver.find_element_by_xpath("//input[@value='Export']").submit()
            return self.driver.page_source
        else:
            return None

    def check_xml_md5(self, dj, response_xml):
        """Check if XML md5 has changed since last time this script ran"""
        if response_xml:
            response_xml_md5 = hashlib.md5(response_xml.encode('utf-8')).hexdigest()
            if not dj.xml_md5 == response_xml_md5:
                # Setlists and related model instances require checking for updates
                dj.xml_md5 = response_xml_md5
        dj.last_check_time = timezone.now()
        dj.save()

    def extract_setlist_features(self, raw_setlist_datum, dj):
        if not(raw_setlist_datum.get('title', None) and raw_setlist_datum['title'][0:5] != "File:"):
            # Link to a mix and not a setlist
            return None

        # Extract and divide all the text from the li's in the "Tracklist" section of the wiki page for the setlist
        tracklist_lines = raw_setlist_datum['revision']['text']['#text'].split("\n")
        tracklist_lines = list(map(lambda line: line.strip(), tracklist_lines))

        setlist_features = {
            'mixesdb_id': int(raw_setlist_datum['id']),
            'title': raw_setlist_datum['title'],
            'mixesdb_mod_time': raw_setlist_datum['revision']['timestamp'],
            'xml_sha1': raw_setlist_datum['revision']['sha1'],
            'b2b': True if "[[Category:Various]]" in tracklist_lines else False
        }

        if setlist_features['b2b']:
            try:
                # Try to only get the tracks under this DJ's header if it's a B2B set.
                tracklist_lines = tracklist_lines[(1 + tracklist_lines.index(";" + dj.name)):]
            except ValueError:
                # Imperfect data -- not possible to tell which of two DJs played the track
                pass

        tracklist_data = []
        for tracklist_line in tracklist_lines:
            track_features = self.extract_track_features(setlist_features, tracklist_line)
            if track_features:
                tracklist_data.append(track_features)
        setlist_features['tracklist_data'] = tracklist_data
        return setlist_features

    def extract_track_features(self, setlist_features, tracklist_line):
        """Determine if a line contains a track and, if it is, extract and clean the artist, title, and label data"""
        try:
            tracklist_line = tracklist_line.decode('utf-8')
        except AttributeError:
            # Doesn't need decoding
            pass
        track_features = {}
        # Pattern generally supports {Artist} - {title} [{Label}]
        pattern = re.compile('(?:\[[\d:\?]*\])?[\s]?(?!\?)([^\[]*) - ([^\[]*)(\[.*])?$')

        if setlist_features['b2b'] and (len(tracklist_line) == 0 or tracklist_line[0] in ["[", ";"]):
            return None
        match = pattern.match(tracklist_line.strip("# ").strip(''))
        if match:
            artist_name = match.group(1).title()
            if " - " in artist_name:
                # Fringe case
                text_components = artist_name.split(" - ")
                track_features['artist_name'] = text_components[0].strip().title()[:255]
                track_features['title'] = text_components[1].strip().title()[:255]
                try:
                    track_features['label_name'] = match.group(2).strip("[( )]").split("-")[0].strip().title()[:255]
                except AttributeError:
                    track_features['label_name'] = None
            else:
                track_features['artist_name'] = artist_name[:255]
                track_features['title'] = match.group(2).strip()[:255]
                try:
                    track_features['label_name'] = match.group(3).strip("[( )]").split("-")[0].strip().title()[:255]
                except AttributeError:
                    track_features['label_name'] = None
        else:
            if " - " in tracklist_line and len(tracklist_line) > 7 and tracklist_line[0] not in ["[", "{", "|", "="] \
                    and "file details" not in tracklist_line.lower():
                print("irregular line:")
                try:
                    print(tracklist_line.encode('utf-8', 'replace'))
                except AttributeError:
                    # Doesn't need decoding
                    print(tracklist_line)
                    pass
            return None
        return track_features

    @transaction.atomic
    def save_setlists(self, raw_setlist_data, dj):
        """Save setlists to database"""
        # If there are 0-1 setlists, convert to list for iteration
        raw_setlist_data = [raw_setlist_data] if not isinstance(raw_setlist_data, list) else raw_setlist_data
        unchanged_data = UnchangedData()
        for raw_setlist_datum in raw_setlist_data:
            setlist_features = self.extract_setlist_features(raw_setlist_datum, dj)
            if setlist_features:
                try:
                    setlist = Setlist.objects.get(dj=dj, mixesdb_id=setlist_features['mixesdb_id'])
                    if setlist.xml_sha1 != setlist_features['xml_sha1']:
                        setlist.title = setlist_features['title']
                        setlist.mixesdb_mod_time = setlist_features['mixesdb_mod_time']
                        setlist.xml_sha1 = setlist_features['xml_sha1']
                        setlist.b2b = setlist_features['b2b']
                        setlist.save()
                    else:
                        raise unchanged_data
                except Setlist.DoesNotExist:
                    setlist = Setlist.objects.create(
                        dj=dj,
                        mixesdb_id=setlist_features['mixesdb_id'],
                        title=setlist_features['title'],
                        mixesdb_mod_time=setlist_features['mixesdb_mod_time'],
                        xml_sha1=setlist_features['xml_sha1'],
                        b2b=setlist_features['b2b']
                    )
                except UnchangedData:
                    continue
                self.save_tracks(setlist_features['tracklist_data'], setlist)

    @transaction.atomic
    def save_tracks(self, tracklist_data, setlist):
        """Save tracks, artists, labels, and trackplays to database"""
        set_order = 1
        for track_features in tracklist_data:
            try:
                artist = Artist.objects.get(name=track_features['artist_name'])
            except Artist.DoesNotExist:
                artist = Artist(name=track_features['artist_name'])
                artist.save()
            try:
                track = Track.objects.get(artist=artist, title=track_features['title'])
            except Track.DoesNotExist:
                track = Track(artist=artist, title=track_features['title'])
                track.save()
            if track_features.get('label_name', None):
                try:
                    label = Label.objects.get(name=track_features['label_name'])
                except Label.DoesNotExist:
                    label = Label.objects.create(name=track_features['label_name'])
                    label.save()
            else:
                label = None
            try:
                trackplay = TrackPlay.objects.get(track=track, setlist=setlist)
                trackplay.set_order = set_order
                trackplay.label = label
                trackplay.save()
            except TrackPlay.DoesNotExist:
                TrackPlay.objects.create(
                    track=track,
                    setlist=setlist,
                    set_order=set_order,
                    label=label
                )
            set_order += 1

class UnchangedData(Exception):
    pass
