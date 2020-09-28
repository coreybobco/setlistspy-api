from lxml import html
import requests

#Abstract class for webcrawling from MixesDb
class Crawler:
    def __init__(self):
        self.base_url = "http://www.mixesdb.com"
        return

    def get_tree(self, url):
        page = requests.get(url)
        return html.fromstring(page.content)