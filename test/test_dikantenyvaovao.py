# coding: utf8

import json
import requests
from time import sleep
from modules.translation.core import Translation
from subprocess import Popen
from test_utils.mocks import PageMock, SiteMock
from unittest.case import TestCase
from modules.decorator import threaded, retry_on_fail


LIST = [
    u"gaon", u"kid", u"精液", u"instar",
    u"bobos", u"大越", u'streak',
    u'weg', u'riz', u'eau',
    u'route',
]


class TestDikantenyVaovaoProcessWiktionaryPage(TestCase):

    def test_process_wiktionary_page_english(self):
        for pagename in LIST:
            translation = Translation()
            page = PageMock(SiteMock('en', 'wiktionary'), pagename)
            translation.process_wiktionary_page(u'en', page)

    def test_process_wiktionary_page_french(self):
        for pagename in LIST:
            translation = Translation()
            page = PageMock(SiteMock('fr', 'wiktionary'), pagename)
            translation.process_wiktionary_page(u'fr', page)


class TestDikantenyVaovaoServices(TestCase):
    def setUp(self):
        self.launch_service()
        sleep(2.5)

    def tearDown(self):
        self.p2.kill()

    @threaded
    def launch_service(self):
        self.p2 = Popen(["python", "dikantenyvaovao.py", "&"])

    def check_response_status(self, url, data):
        resp = requests.put(url, json=data)
        print (resp.text)
        resp_data = json.loads(resp.text) if resp.text else {}
        self.assertEquals(resp.status_code, 200)
        for _, added_entries in resp_data.items():
            self.assertTrue(isinstance(added_entries , list))

    @retry_on_fail(Exception, retries=10, time_between_retries=.5)
    def test_translate_english_word(self):
        data = {
            u"dryrun": True,
            u"word": u"rice",
            u"translation": u"vary",
            u"POS": u"ana",
        }
        url = "http://localhost:8000/translate/en"
        self.check_response_status(url, data)

    @retry_on_fail(Exception, retries=10, time_between_retries=.5)
    def test_translate_french_word(self):
        data = {
            u"dryrun": True,
            u"word": u"riz",
            u"translation": u"vary",
            u"POS": u"ana",
        }
        url = "http://localhost:8000/translate/fr"
        self.check_response_status(url, data)