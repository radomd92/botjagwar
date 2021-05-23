# coding: utf8
import asyncio
import logging
from copy import deepcopy

from pywikibot import Page

from api import entryprocessor
from api.output import Output
from api.servicemanager import DictionaryServiceManager
from object_model.word import Entry
from .functions import \
    translate_using_bridge_language, \
    translate_using_postgrest_json_dictionary, \
    translate_form_of_templates, \
    translate_using_convergent_definition
from .types import \
    UntranslatedDefinition, \
    TranslatedDefinition

log = logging.getLogger(__name__)
default_data_file = '/opt/botjagwar/conf/entry_translator/'
URL_HEAD = DictionaryServiceManager().get_url_head()
WORKING_WIKI_LANGUAGE = 'mg'
translation_methods = [
    translate_using_convergent_definition,
    translate_using_bridge_language,
    translate_using_postgrest_json_dictionary,
    translate_form_of_templates
]


class Translation:
    def __init__(self):
        """Mandika teny ary pejy @ teny malagasy"""
        super(self.__class__, self).__init__()
        self.output = Output()
        self.loop = asyncio.get_event_loop()

    def _save_translation_from_bridge_language(self, infos: Entry):
        self.output.db(infos)

    def _save_translation_from_page(self, infos: Entry):
        self.output.db(infos)

    def process_wiktionary_wiki_page(self, wiki_page: Page):
        if wiki_page.isEmpty():
            return

        if not wiki_page.namespace().content:
            return

        wiktionary_processor_class = entryprocessor.WiktionaryProcessorFactory.create(wiki_page.site.language)
        wiktionary_processor = wiktionary_processor_class()
        if not wiki_page.isRedirectPage():
            wiktionary_processor.set_text(wiki_page.get())
            wiktionary_processor.set_title(wiki_page.title())
        else:
            self.process_wiktionary_wiki_page(wiki_page.getRedirectTarget())

        try:
            entries = wiktionary_processor.getall(human_readable_form_of_definition=True)
            out_entries = []
            for entry in entries:
                # print(entry)
                translated_definition = []
                translated_from_definition = []
                for definition_line in entry.entry_definition:
                    refined_definition_lines = wiktionary_processor.refine_definition(definition_line)
                    for refined_definition_line in refined_definition_lines:
                        for t_method in translation_methods:
                            definitions = t_method(
                                entry.part_of_speech,
                                refined_definition_line,
                                wiki_page.site.language,
                                WORKING_WIKI_LANGUAGE
                            )
                            # print('defn>', definitions)
                            if isinstance(definitions, UntranslatedDefinition):
                                continue
                            elif isinstance(definitions, TranslatedDefinition):
                                translated_definition += [k.strip() for k in definitions.split(',')]
                        translated_from_definition.append(refined_definition_line)

                entry_definitions = sorted(list(set(translated_definition)))
                out_entry = deepcopy(entry)
                out_entry.translated_from_definition = ', '.join(translated_from_definition)
                out_entry.entry_definition = entry_definitions
                out_entry.translated_from_language = wiki_page.site.language
                # print(translated_definition)
                # print(entry)
                # print(out_entry)
                if entry_definitions:
                    out_entries.append(out_entry)

            print('outentry>', out_entries)
        except Exception as exc:
            log.exception(exc)
            return -1