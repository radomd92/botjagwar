"""
This script reads SQLite database file and updates the local one as it goes.

The SQLite database MUST be a Base dictionary generated by botjagwar (see the code at
database/dictionary/__init__.py if you want to know what I'm talking about), or else DictionaryDatabaseManager
supposed to handle both the local and the dictionary-to-be-imported will be lost.

if update_on_wiki is set to True, it also creates entries on-wiki if the latter does not exist on the Malagasy
Wiktionary.
"""

import sys
from pprint import pprint

import pywikibot

from api.data_caching import FastWordLookup
from api.databasemanager import DictionaryDatabaseManager
from api.output import Output
from api.storage import EntryPageFileReader
from api.translation.core import LANGUAGE_BLACKLIST, CYRILLIC_ALPHABET_LANGUAGES, _get_unaccented_word
from object_model.word import Entry

language = sys.argv[1] if len(sys.argv) >= 2 else 'en'


class Importer(object):
    summary = "Fanafarana dikan-teny"

    # Sometimes Pywikibot API will do nothing but slow us down
    site = pywikibot.Site('mg', 'wiktionary')
    update_on_wiki = True

    # Fast word lookup table
    lookup_cache = FastWordLookup()

    def __init__(self):
        self.lookup_cache.build_fast_word_tree()

    def do_import(self):
        """
        Imports database.
        Entry creation could be heavily parallelised but a some point Pywikibot will
        be a serious bottleneck.

        :param workers: Number of items to yield; initially intended to parallelise the work
        but Pywikibot API won't let us flood Wikimedia sites :P
        :return:
        """
        raise NotImplementedError()

    def worker(self, entry: Entry):
        """
        Updates the wiki page with the given entry.
        If entry exists in database, skip;
        else, check language's existence on-wiki and if it exists, skip;
        else, add the entry on-wiki
        :param entry: entry to create
        :return:
        """
        if entry.language in LANGUAGE_BLACKLIST:
            print('blackisted: ', entry.language)
            return

        if self.lookup_cache.lookup(entry):
            return
        else:
            pprint(entry)
            output = Output()
            output.db(entry)

        if not self.update_on_wiki:
            print('not updating on wiki')
            return

        print('attempts to update on wiki...')
        wikipage = output.wikipage(entry)
        if entry.language in CYRILLIC_ALPHABET_LANGUAGES:
            entry.entry = _get_unaccented_word(entry.entry)

        page = pywikibot.Page(self.site, entry.entry)
        try:
            if page.isRedirectPage():
                return
        except Exception:
            return
        if page.exists():
            content = page.get()
            if '{{=%s=}}' % entry.language in content:
                print('exists on-wiki')
                return
            else:
                content = wikipage + '\n' + content
        else:
            content = wikipage

        page.put(content, self.summary)


class BatchImporter(Importer):
    summary = "dikan-teny avy amin'ny tahiry XML"

    def __init__(self, language):
        super(BatchImporter, self).__init__()
        self.language = language
        self.file_reader = EntryPageFileReader(self.language)

    def do_import(self):
        self.file_reader.read()
        for page_name, page_list in self.file_reader.page_dump.items():
            for entry in page_list:
                self.worker(entry)


class DatabaseImporter(Importer):
    export_path = 'user_data/dump_export.db'
    summary = "dikan-teny avy amin'ny tahiry XML"
    fast_tree = {}

    def do_import(self, workers=100):
        input_database = DictionaryDatabaseManager(database_file=self.export_path)
        with input_database.engine.connect() as connection:
            query = connection.execute(
                """
                select 
                    word.id,
                    word.word, 
                    word.language, 
                    word.part_of_speech, 
                    definitions.definition,
                    definitions.definition_language
                from 
                    dictionary,
                    word, 
                    definitions
                where 
                    dictionary.definition = definitions.id
                    and word.id = dictionary.word
                    and definition_language = 'mg'
                """
            )
            print('-- build tree --')
            for w in query.fetchall():
                word, language, part_of_speech, definition = w[1], w[2], w[3], w[4]
                key = (word, language, part_of_speech)
                if key in self.fast_tree:
                    self.fast_tree[key].append(definition)
                else:
                    self.fast_tree[key] = [definition]

            print('-- using tree --')
            for word, language, part_of_speech in self.fast_tree:
                entry = Entry(
                    entry=word,
                    language=language,
                    part_of_speech=part_of_speech,
                    entry_definition=self.fast_tree[(word, language, part_of_speech)]
                )
                try:
                    self.worker(entry)
                except Exception:
                    continue


if __name__ == '__main__':
    dbi = BatchImporter(language)
    dbi.do_import()
