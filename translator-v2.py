from csv import writer

import pywikibot
import redis

from api.entryprocessor import WiktionaryProcessorFactory
from api.translation_v2.core import Translation
from api.translation_v2.functions.postprocessors import \
    add_xlit_if_no_transcription
from page_lister import redis_get_pages_from_category as get_pages_from_category
from redis_wikicache import RedisSite

if __name__ == '__main__':
    postprocessors = [
        # add_language_IPA_if_not_exists('ur'),
        # add_wiktionary_credit('en')
        add_xlit_if_no_transcription
    ]
    t = Translation()
    t.post_processors = postprocessors
    site = RedisSite('en', 'wiktionary', offline=False)
    errored = []
    errors = 0
    k = 100
    entries = 0
    wiktionary_processor_class = WiktionaryProcessorFactory.create('en')
    category = 'Bengali nouns'
    with open(f'user_data/translations/{category}.csv', 'w') as output_file:
        csv_writer = writer(output_file)
        for wiki_page in get_pages_from_category('en', category):
            try:
                entries = t.process_wiktionary_wiki_page(wiki_page)
            except (pywikibot.Error, redis.exceptions.TimeoutError, Exception):
                continue

    print('process error rate:', errors * 100. / (k))
    print('entries created:', entries)
    print(errored)
