# coding: utf8

import re
from .base import WiktionaryProcessor
from .base import data_file


class PLWiktionaryProcessor(WiktionaryProcessor):
    @property
    def language(self):
        return 'pl'

    def __init__(self, test=False, verbose=False):
        super(PLWiktionaryProcessor, self).__init__(test=test, verbose=verbose)
        try:
            f = open(data_file + 'WiktionaryPL_langdata.dct', 'r').read()
            self.langdata = eval(f)
        except IOError:
            self.langdata = {}

    def retrieve_translations(self, page_c):
        ret = []
        tr_lines = self._get_translation_lines(page_c)
        for line in tr_lines:
            line = line.split(':')
            language = self.langname2languagecode(line[0].strip())
            translations = line[1].strip()
            for translation in translations.split(';'):
                ret.append((language, translation))
        return ret

    def _get_translation_lines(self, page_c):
        ret = []
        # getting borders of translation section
        tr_start = page_c.find(
            "== polski ({{język polski}}) ==") + len("== polski ({{język polski}}) ==")
        tr_end = 0

        if page_c.find("{{tłumaczenia}}", tr_start) != -1:
            tr_start = page_c.find("{{tłumaczenia}}", tr_start)
        else:
            return ret
        if page_c.find("{{źródła}}", tr_start) != -1:
            tr_end = page_c.find("{{źródła}}", tr_start)
        tr_section = page_c[tr_start:tr_end]
        # retrieving translations using regexes
        regex = re.compile('\\*(.*)')
        for translation in re.findall(regex, tr_section):
            ret.append(translation)
        return ret

    def _langname2langcode(self, langname):
        langname = langname.strip()
        return self.langdata[langname]
