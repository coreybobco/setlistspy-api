'''
Note (8.16.2019):
Because Mixesdb.com has removed its XML export page/API functionality, this library is deprecated.
Technically, scraping the list of DJs still works, but there is nothing further to scrape using that data.
So to speed up Docker build times, I have removed lxml and selenium from the Docker image as well.
'''

import requests
from django.db import transaction
from lxml import html
from selenium import webdriver

from setlistspy.app.models import DJ
# from setlistspy.app.tasks.mixesdb import process_setlists_xml

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
                    DJ.objects.get(url=dj_url)
                except DJ.DoesNotExist:
                    DJ.objects.create(name=dj_name, url=dj_url)

    def seek_next_artist_category_page(self):
        """Find the url of the next page of results"""
        next_url_hrefs = self.current_html.xpath(
            "//div[@class='listPagination'][1]/a[contains(text(), 'next')]/@href")
        next_url_hrefs = [href for href in next_url_hrefs if href is not None]
        self.current_crawler_url = self.base_url + next_url_hrefs[0] if len(next_url_hrefs) else False

    # DEPRECATED by removal of xml export page from Mixesdb.com
    # def crawl_all_setlists_by_all_djs(self):
    #     """ Iterate through all djs whose setlist XML hasn't been checked recently & save setlist data"""
    #     two_days_ago = timezone.now() - timedelta(days=2)
    #     dj_iterator = DJ.objects.filter(
    #         Q(last_check_time__lte=two_days_ago) |
    #         Q(last_check_time__isnull=True)
    #     ).iterator()
    #     for dj in dj_iterator:
    #         self.crawl_all_setlists_by_dj(dj)
    #
    # def crawl_all_setlists_by_dj(self, dj):
    #     """Get XML dump, check if still valid, and then create/update relevant instances"""
    #     process_setlists_xml.delay(self.get_xml_from_setlists_by_dj(dj))
    #
    # def get_xml_from_setlists_by_dj(self, dj):
    #     """Use Selenium to get XML dump for all setlists of one individual DJ"""
    #     self.driver.get("http://www.mixesdb.com/db/index.php?title=Special:Export")
    #     # Uncheck box so XML returned as response, not as file download
    #     import ipdb; ipdb.set_trace()
    #     self.driver.find_element_by_name("wpDownload").click()
    #     category_input = self.driver.find_element_by_name("catname")
    #     dj_category_name = urllib.parse.unquote(dj.url[25:])  # e.g. Category:Helena_Hauff
    #     print(dj_category_name.encode('utf-8', 'replace'))
    #     category_input.send_keys(dj_category_name)
    #     category_input.send_keys(Keys.RETURN)  # Fills textarea with list of DJ sets
    #     setlists_url_paths = self.driver.find_element_by_tag_name("textarea").get_attribute("value")
    #     if setlists_url_paths:
    #         self.driver.find_element_by_xpath("//input[@value='Export']").submit()
    #         return self.driver.page_source
    #     else:
    #         return None