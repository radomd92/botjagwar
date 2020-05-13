# coding: utf8

import re

from object_model.word import Entry
from .base import WiktionaryProcessor
from .base import stripwikitext


class MGWiktionaryProcessor(WiktionaryProcessor):
    form_of_regex = r'\{\{\-([a-z]+\-[a-z]{3,7})\-\|([a-z]{2,3})\}\}'
    lemma_regex = r"\{\{\-([a-z]{3,7})\-\|([a-z]{2,3})\}\}"

    def __init__(self, test=False, verbose=False):
        super(MGWiktionaryProcessor, self).__init__(test=test, verbose=verbose)
        self.content = None

    def retrieve_translations(self):
        return []

    def getall(self, keep_native_entries=False):
        items = []
        if self.content is None:
            return []
        for regex in [self.form_of_regex, self.lemma_regex]:
            for pos, lang in re.findall(regex, self.content):
                pos = pos.strip()
                if pos.strip() in ('etim'):
                    continue
                # word DEFINITION Retrieving
                d1 = self.content.find("{{-%s-|%s}}" % (pos, lang)) + len("{{-%s-|%s}}" % (pos, lang))
                d2 = self.content.find("=={{=", d1) + 1 or self.content.find("== {{=", d1) + 1
                if d2:
                    definition = self.content[d1:d2]
                else:
                    definition = self.content[d1:]
                try:
                    definitions = definition.split('\n# ')[1:]
                except IndexError:
                    # print(" Hadisoana : Tsy nahitana famaritana")
                    continue

                entry_definition = []
                for definition in definitions:
                    if definition.find('\n') + 1:
                        definition = definition[:definition.find('\n')]
                        definition = re.sub("\[\[(.*)#(.*)\|?\]?\]?", "\\1", definition)
                    definition = stripwikitext(definition)
                    if not definition:
                        continue
                    else:
                        entry_definition.append(definition)

                entry_definition = [d for d in entry_definition if len(d) > 1]

                if entry_definition:
                    i = Entry(
                        entry=self.title,
                        part_of_speech=pos.strip(),
                        language=lang.strip(),
                        entry_definition=entry_definition
                    )
                    items.append(i)
        # print("Nahitana dikanteny ", len(items) ", len(items))
        return items
