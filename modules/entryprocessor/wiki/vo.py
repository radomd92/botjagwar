# coding: utf8

import re
import pywikibot
from base import WiktionaryProcessor
from base import data_file


class VOWiktionaryProcessor(WiktionaryProcessor):
    def get_WW_definition(self):
        return self._get_param_in_temp(u"Samafomot:VpVöd", 'WW')

    def _get_param_in_temp(self, templatestr, parameterstr):
        # print templatestr, parameterstr
        RET_text = u""
        templates_withparams = self.Page.templatesWithParams()
        for template in templates_withparams:
            if template[0].title() == templatestr:
                for params in template[1]:
                    if params.startswith(parameterstr + u'='):
                        RET_text = params[len(parameterstr) + 1:]
        return RET_text

    def getall(self, keepNativeEntries=False):
        POStran = {u"värb": 'mat',
                   u'subsat': 'ana',
                   u'ladyek': 'mpam-ana'}

        POS = self._get_param_in_temp(u'Samafomot:VpVöd', u'klad')
        definition = self.get_WW_definition()
        if POStran.has_key(POS):
            postran = POStran[POS]
        else:
            postran = POS

        return postran, 'vo', definition

    def retrieve_translations(self, page_c):
        pass