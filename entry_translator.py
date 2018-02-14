# -*- coding: utf8 -*-
import os
import sys
import time
import json
import pywikibot as pwbot
import traceback


from modules import entryprocessor
from modules.decorator import threaded
from modules.translation.core import Translation

from pywikibot import Site, Page

from aiohttp import web
from aiohttp.web import Response


# GLOBAL VARS
verbose = False
databases = []
data_file = os.getcwd() + '/conf/entry_translator/'
userdata_file = os.getcwd() + '/user_data/entry_translator/'
translations = Translation()
routes = web.RouteTableDef()


# Throttle Config
def set_throttle(i):
    from pywikibot import throttle
    t = throttle.Throttle(pwbot.Site('mg', 'wiktionary'), mindelay=0, maxdelay=1)
    pwbot.config.put_throttle = 1
    t.setDelays(i)


def _update_unknowns(unknowns):
    f = open(userdata_file + "word_hits", 'a')
    for word, lang in unknowns:
        word += ' [%s]\n' % lang
        print((type(word)))
        f.write(word)
    f.close()


def _get_page(name, lang):
    page = pwbot.Page(pwbot.Site(lang, 'wiktionary'), name)
    return page


@threaded
def _update_statistics(rc_bot):
    if not rc_bot.stats["edits"] % 5:
        cttime = time.gmtime()
        rc_bot.chronometer = time.time() - rc_bot.chronometer
        print(("%d/%02d/%02d %02d:%02d:%02d > " % cttime[:6], \
               "Fanovana: %(edits)d; pejy voaforona: %(newentries)d; hadisoana: %(errors)d" % rc_bot.stats \
               + " taha: fanovana %.1f/min" % (60. * (5 / rc_bot.chronometer))))
        rc_bot.chronometer = time.time()


@threaded
def put_deletion_notice(page):
    if not page.exists() or page.isRedirectPage():
        return
    if page.namespace() == 0:
        page_c = page.get()
        page_c += "\n[[sokajy:Pejy voafafa tany an-kafa]]"
        page.put(page_c, "+filazana")


@routes.post("/wiktionary_page/{lang}")
async def handle_wiktionary_page(request):
    """
    Handle a Wiktionary page, attempts to translate the wiktionary page's content and
    uploads it to the Malagasy Wiktionary.
    :param lang: Wiktionary edition to look up on.
    :return: 200 if everything worked with the list of database lookups including translations,
    500 if an error occurred
    """

    data = await request.json()
    pagename = data['title']
    page = _get_page(pagename, request.match_info['lang'])
    if page is None:
        return
    data = {}
    try:
        data['unknowns'], data['new_entries'] = await translations.process_wiktionary_wiki_page(page)
        _update_unknowns(data['unknowns'])
    except Exception as e:
        traceback.print_exc()
        data['traceback'] = traceback.format_exc()
        data['message'] = '' if not hasattr(e, 'message') else getattr(e, 'message')
        response = Response(text=json.dumps(data), status=500, content_type='application/json')
    else:
        response = Response(text=json.dumps(data), status=200, content_type='application/json')
    return response


@routes.get("/wiktionary_page/{language}/{pagename}")
async def get_wiktionary_processed_page(request):
    language = request.match_info['language']
    pagename = request.match_info['pagename']

    wiktionary_processor_class = entryprocessor.WiktionaryProcessorFactory.create(language)
    wiktionary_processor = wiktionary_processor_class()
    ret = []

    page = Page(Site(language, 'wiktionary'), pagename)
    wiktionary_processor.process(page)

    for entry in wiktionary_processor.getall():
        word, pos, language_code, translation = entry
        translation_list = []
        section = dict(
            word=word,
            language=language_code,
            part_of_speech=pos,
            translation=translation)
        for translation in wiktionary_processor.retrieve_translations():
            translation_word, translation_pos, translation_language, translation = translation
            translation_section = dict(
                word=translation_word,
                language=translation_language,
                part_of_speech=translation_pos,
                translation=translation)
            translation_list.append(translation_section)

        if language_code == language:
            section['translations'] = translation_list
        ret.append(section)

    return Response(text=json.dumps(ret), status=200, content_type='application/json')


args = sys.argv
if __name__ == '__main__':
    try:
        set_throttle(1)
        app = web.Application()
        app.router.add_routes(routes)
        web.run_app(app, port=8000)
    finally:
        pwbot.stopme()