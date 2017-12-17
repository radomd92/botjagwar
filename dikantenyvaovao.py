# -*- coding: utf8 -*-
import os
import sys
import time
import json
import pywikibot as pwbot
from flask import Flask, request
import traceback

from modules import service_ports
from modules.database import Database
from modules.database.word import WordDatabase
from modules.decorator import threaded
from modules.translation.core import Translation

from _mysql_exceptions import DataError, IntegrityError


# GLOBAL VARS
verbose = False
databases = []
data_file = os.getcwd() + '/conf/dikantenyvaovao/'
userdata_file = os.getcwd() + '/user_data/dikantenyvaovao/'
app = Flask(__name__)
translations = Translation(data_file)
languages = {
    u'en': u'anglisy',
    u'fr': u'frantsay'
}


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
        print (type(word))
        f.write(word.encode('utf8'))
    f.close()


def _get_page(name, lang):
    page = pwbot.Page(pwbot.Site(lang, 'wiktionary'), name)
    return page


def _update_statistics(rc_bot):
    if not rc_bot.stats["edits"] % 5:
        cttime = time.gmtime()
        rc_bot.chronometer = time.time() - rc_bot.chronometer
        print ("%d/%02d/%02d %02d:%02d:%02d > " % cttime[:6], \
               "Fanovana: %(edits)d; pejy voaforona: %(newentries)d; hadisoana: %(errors)d" % rc_bot.stats \
               + " taha: fanovana %.1f/min" % (60. * (5 / rc_bot.chronometer)))
        rc_bot.chronometer = time.time()


def _get_word_id(word, lang_code):
    """
    Gets the word ID
    :param word: word
    :param language: ISO language code of the language the word belongs to
    :return: the word ID
    """
    word_db = Database(table=u"%s" % languages[lang_code])
    results = word_db.read({
        languages[lang_code] : word
    }, select="%s_wID" % lang_code)
    return results


@threaded
def put_deletion_notice(page):
    if not page.exists() or page.isRedirectPage():
        return
    if page.namespace() == 0:
        page_c = page.get()
        page_c += u"\n[[sokajy:Pejy voafafa tany an-kafa]]"
        page.put(page_c, "+filazana")


@app.route("/wiktionary_page/<lang>/<pagename>")
def handle_wiktionary_page(pagename, lang):
    """
    Handle a Wiktionary page, attempts to translate the wiktionary page's content and
    uploads it to the Malagasy Wiktionary.
    :param pagename: page name. Must consist of unicode-compatible characters with no slash, and not too long.
    :param lang: Wiktionary edition to look up on.
    :return: 200 if everything worked with the list of database lookups including translations,
    500 if an error occurred
    """
    page = _get_page(pagename, lang)
    if page is None:
        return
    data = {}
    try:
        data[u'unknowns'], data[u'new_entries'] = translations.process_wiktionary_page(lang, page)
        _update_unknowns(data[u'unknowns'])
    except Exception as e:
        traceback.print_exc()
        data[u'traceback'] = traceback.format_exc()
        data[u'message'] = e.message
        response = app.response_class(response=json.dumps(data), status=500, mimetype='application/json')
    else:
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')

    return response


@app.route("/translate/<lang>", methods=["PUT"])
def handle_translate_word(lang):
    """
    POST Service to translate a given word to a native language
    Returns 500 if translation exists or if an error has occurred, 200 otherwise
    :param lang:
    :return:
    """
    data = json.loads(request.get_data())
    word = data[u"word"]
    translation = data[u"translation"]
    part_of_speech = data[u"POS"]
    dry_run = data[u"dryrun"]

    translation_db = WordDatabase()
    translation_write_db = Database(table=u"%s_malagasy" % languages[lang])
    if translation_db.exists(word, lang, part_of_speech):
        raise Exception('exists already')
    else:
        try:
            added = []
            for id_ in _get_word_id(word, lang):
                sql_data = {
                    u"%s_wID" % lang: str(id_),
                    u"mg": translation
                }
                added.append(sql_data)
                print sql_data
                translation_write_db.insert(sql_data, dry_run=dry_run)
        except (DataError, IntegrityError) as e:
            response = app.response_class(
                response=json.dumps({u'message': e.message}),
                status=500, mimetype='application/json')
        else:
            response = app.response_class(
                response=json.dumps({u'added': added}),
                status=200, mimetype='application/json')

    return response


def striplinks(link):
    l = link
    for c in [u'[', u']']:
        l = l.replace(c, '')
    return l


args = sys.argv
if __name__ == '__main__':
    try:
        set_throttle(1)
        app.run(host="0.0.0.0", port=service_ports.get_service_port('dikantenyvaovao'))
    finally:
        pwbot.stopme()
