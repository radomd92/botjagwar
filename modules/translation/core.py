# coding: utf8
import os
import pywikibot as pwbot
from modules import entryprocessor
from modules.exceptions import NoWordException
from modules.output import Output
from modules.autoformatter import Autoformat
from models.word import Entry

default_data_file = os.getcwd() + '/conf/dikantenyvaovao/'


class Translation:
    def __init__(self, data_file=False):
        """Mandika teny ary pejy @ teny malagasy"""
        super(self.__class__, self).__init__()
        self.data_file = data_file or default_data_file
        self.output = Output()
        self.language_blacklist = ['fr', 'en', 'sh', 'ar', 'de', 'zh']

    def _save_translation_from_bridge_language(self, infos):
        summary = "Dikan-teny avy amin'ny dikan-teny avy amin'i %s.wiktionary" % infos.origin_wiktionary_edition
        wikipage = self.output.wikipage(infos)
        mg_page = pwbot.Page(pwbot.Site('mg', 'wiktionary'), infos.entry)
        try:
            if mg_page.exists():
                pagecontent = mg_page.get()
                if pagecontent.find('{{=%s=}}' % infos.language) != -1:
                    self.output.db(infos)
                    return
                else:
                    wikipage += pagecontent
                    summary = "+" + summary
        except pwbot.exceptions.IsRedirectPage:
            infos.entry = mg_page.getRedirectTarget().title()
            self._save_translation_from_bridge_language(infos)
            return

        except pwbot.exceptions.InvalidTitle:
            return

        except Exception as e:
            return

        mg_page.put_async(wikipage, summary)
        self.output.db(infos)

    def _save_translation_from_page(self, infos):
        summary = "Dikan-teny avy amin'ny pejy avy amin'i %s.wiktionary" % infos.language
        wikipage = self.output.wikipage(infos)
        mg_page = pwbot.Page(pwbot.Site('mg', 'wiktionary'), infos.entry)
        if mg_page.exists():
            pagecontent = mg_page.get()
            if pagecontent.find('{{=%s=}}' % infos.language) != -1:
                self.output.db(infos)
                return
            else:
                wikipage += pagecontent
                wikipage, edit_summary = Autoformat(wikipage).wikitext()
                summary = "+" + summary + ", %s" % edit_summary

        mg_page.put_async(wikipage, summary)
        self.output.db(infos)

    def process_entry_in_native_language(self, wiki_page, language, unknowns):
        wiktionary_processor_class = entryprocessor.WiktionaryProcessorFactory.create(language)
        wiktionary_processor = wiktionary_processor_class()
        ret = 0
        try:
            translations = wiktionary_processor.retrieve_translations()
        except Exception as e:
            return ret
        translations_in_mg = {}  # dictionary {string : list of translation tuple (see below)}
        for entry, pos, entry_language in translations:
            # translation = tuple(codelangue, entree)
            if entry_language in self.language_blacklist:  # check in language blacklist
                continue
            title = wiki_page.title()
            try:
                mg_translation = self.translate_word(title, language)
            except NoWordException:
                if title not in unknowns:
                    unknowns.append((title, language))
                break

            infos = Entry(
                entry=entry,
                part_of_speech=str(pos),
                entry_definition=mg_translation,
                language=entry_language,
                origin_wiktionary_edition=language,
                origin_wiktionary_page_name=title)
            if self.word_db.exists(infos.entry, infos.language):
                continue

            _generate_redirections(infos)
            _append_in(infos, translations_in_mg)
            self._save_translation_from_bridge_language(infos)
            ret += 1

        return ret

    def process_entry_in_foreign_language(
            self, wiki_page, word, language_code, language, pos, definition, translations_in_mg, unknowns):
        if language_code in self.language_blacklist:
            return 0

        if self.word_db.exists(word, language_code):
            return 0

        title = wiki_page.title()
        try:
            mg_translation = self.translate_word(definition, language)
        except NoWordException:
            if title not in unknowns:
                unknowns.append((definition, language))
            return 0

        infos = Entry(
            entry=title,
            part_of_speech=str(pos),
            entry_definition=mg_translation,
            language=language_code,
            origin_wiktionary_edition=language,
            origin_wiktionary_page_name=definition)

        _generate_redirections(infos)
        _append_in(infos, translations_in_mg)
        self._save_translation_from_bridge_language(infos)
        self._save_translation_from_page(infos)

        return 1

    def process_wiktionary_wiki_page(self, wiki_page):
        language = wiki_page.site.language()
        unknowns = []
        # fanampiana : wiki_page:wiki_page

        # BEGINNING
        ret = 0
        wiktionary_processor_class = entryprocessor.WiktionaryProcessorFactory.create(language)
        wiktionary_processor = wiktionary_processor_class()

        if wiki_page.title().find(':') != -1:
            return unknowns, ret
        if wiki_page.namespace() != 0:
            return unknowns, ret
        wiktionary_processor.process(wiki_page)

        try:
            entries = wiktionary_processor.getall()
        except Exception as e:
            return unknowns, ret

        translations_in_mg = {}  # dictionary {string : list of translation tuple (see below)}
        for word, pos, language_code, definition in entries:
            if word is None or definition is None:
                continue

            if language_code == language:  # if entry in the content language
                ret += self.process_entry_in_native_language(wiki_page, language, unknowns)
            else:
                ret += self.process_entry_in_foreign_language(
                    wiki_page, word, language_code, language, pos, definition, translations_in_mg, unknowns)

        # Malagasy language pages
        # self.update_malagasy_word(translations_in_mg)
        return unknowns, ret

    def translate_word(self, word, language):
        tr = self.word_db.translate(word, language)
        if not tr:
            raise NoWordException()
        else:
            return tr


def _append_in(infos, translations_in_mg):  # TRANSLATION HANDLING SUBFUNCTION
    for malagasy_translation in infos.entry_definition.split(","):
        malagasy_translation = malagasy_translation.strip()
        if malagasy_translation in translations_in_mg:
            translations_in_mg[malagasy_translation].append((infos.language, infos.entry))
        else:
            translations_in_mg[malagasy_translation] = []
            translations_in_mg[malagasy_translation].append((infos.language, infos.entry))


def _generate_redirections(infos):
    redirection_target = infos.entry
    if infos.language in ['ru', 'uk', 'bg', 'be']:
        for char in "́̀":
            if redirection_target.find(char) != -1:
                redirection_target = redirection_target.replace(char, "")
        if redirection_target.find("æ") != -1:
            redirection_target = redirection_target.replace("æ", "ӕ")
        if infos.entry != redirection_target:
            page = pwbot.Page(pwbot.Site('mg', 'wiktionary'), infos.entry)
            if not page.exists():
                page.put_async("#FIHODINANA [[%s]]" % redirection_target, "fihodinana")
            infos.entry = redirection_target