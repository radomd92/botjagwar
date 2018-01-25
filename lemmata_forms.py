# coding: utf8

import re
import sys
import pywikibot

from models.word import Entry

from modules.entryprocessor import WiktionaryProcessorFactory
from modules.parsers.functions import parse_inflection_of, parse_one_parameter_template
from modules.parsers.inflection_template import EnWiktionaryInflectionTemplateParser
from modules.output import Output

import traceback


CASES = {
    'nom': u'endriky ny lazaina',
    'acc': u'endrika teny fameno',
    'loc': u'endrika teny famaritan-toerana',
    'dat': u'mpanamarika ny tolorana',
    'gen': u'mpanamarika ny an\'ny tompo',
    'ins': u'mpanamarika fomba fanaovana',
    '': u''
}
NUMBER = {
    's': u'singiolary',
    'p': u'ploraly',
    '': u''
}
SITENAME = 'wiktionary'
SITELANG = 'mg'
last_entry = 0
language_code = sys.argv[1]
category_name = sys.argv[2].decode('utf8')
template = sys.argv[3].decode('utf8') if len(sys.argv) >= 4 else u'e-ana'

templates_parser = EnWiktionaryInflectionTemplateParser()
templates_parser.add_parser(u'feminine singular of', parse_one_parameter_template(u'feminine singular of'))
templates_parser.add_parser(u'feminine plural of', parse_one_parameter_template(u'feminine plural of'))
templates_parser.add_parser(u'feminine of', parse_one_parameter_template(u'feminine of'))
templates_parser.add_parser(u'inflection of', parse_inflection_of)
templates_parser.add_parser(u'inflected form of', parse_one_parameter_template(u'inflected form of'))
templates_parser.add_parser(u'masculine plural of', parse_one_parameter_template(u'masculine plural of'))
templates_parser.add_parser(u'plural of', parse_one_parameter_template(u'plural of'))


def template_expression_to_malagasy_definition(template_expr):
    """
    :param template_expr: template instance string with all its parameters
    :return: A malagasy language definition in unicode
    """
    elements = templates_parser.get_elements(template_expr)
    t_name, lemma, case_name, number_ = elements
    case = CASES[case_name] if case_name in CASES else u''
    num = NUMBER[number_] if number_ in NUMBER else u''
    ret = u'%s %s ny teny [[%s]]' % (case, num, lemma)

    print elements
    return ret


def get_count():
    try:
        with open('user_data/%s-counter' % language_code, 'r') as f:
            counter = int(f.read())
            return counter
    except IOError:
        return 0


def save_count():
    with open('user_data/%s-counter' % language_code, 'w') as f:
        f.write(str(last_entry))


def parse_word_forms():
    global language_code
    global category_name
    global last_entry
    last_entry = get_count()
    en_page_processor_class = WiktionaryProcessorFactory.create('en')
    en_page_processor = en_page_processor_class()
    page_output = Output()
    nouns = pywikibot.Category(pywikibot.Site('en', SITENAME), category_name)
    counter = 0
    for word_page in nouns.articles():
        pywikibot.output(u'▒▒▒▒▒▒▒▒▒▒▒▒▒▒ \03{green}%-25s\03{default} ▒▒▒▒▒▒▒▒▒▒▒▒▒▒' % word_page.title())
        counter += 1
        if last_entry > counter:
            print u'moving on'
            continue
        en_page_processor.process(word_page)
        entries = en_page_processor.getall(definitions_as_is=True)
        entries = [entry for entry in entries if entry[2] == unicode(language_code)]
        for word, pos, language_code, definition in entries:
            last_entry += 1
            mg_page = pywikibot.Page(pywikibot.Site(SITELANG, SITENAME), word)

            try:
                malagasy_definition = template_expression_to_malagasy_definition(definition)
                lemma = templates_parser.get_lemma(definition)
            except (AttributeError, ValueError) as e:
                print traceback.format_exc()
                continue

            # Do not create page if lemma does not exist
            mg_lemma_page = pywikibot.Page(pywikibot.Site(SITELANG, SITENAME), lemma)
            if not mg_lemma_page.exists():
                print u'No lemma :/'
                continue

            mg_entry = Entry(
                entry=word,
                part_of_speech=template,
                entry_definition=malagasy_definition,
                language=language_code,
            )
            if mg_page.exists():
                new_entry = page_output.wikipage(mg_entry)
                page_content = mg_page.get()
                if page_content.find(u'{{=%s=}}' % language_code) != -1:
                    if page_content.find(u'{{-%s-|%s}}' % (template, language_code)) != -1:
                        print u'section already exists: No need to go further'
                        continue
                    else:
                        page_content = re.sub(r'==[ ]?{{=%s=}}[ ]?==' % language_code, new_entry, page_content)
                else:
                    page_content = new_entry + u'\n' + page_content
            else:
                page_content = page_output.wikipage(mg_entry)

            pywikibot.output(u'\03{blue}%s\03{default}' % page_content)
            #mg_page.put(page_content, u'Teny vaovao')


if __name__ == '__main__':
    try:
        parse_word_forms()
    finally:
        save_count()