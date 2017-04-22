# coding: utf8

from modules import BJDBmodule
from modules.output import Output
from modules import entryprocessor
from exceptions import NoWordException
import pywikibot as pwbot
import re

verbose = 0


class TranslationsHandler(object):
    def __init__(self):
        """Mitantana ny dikantenin'ny teny hafa amin'ny teny malagasy"""
        self.content = u""
        self.loaded_flag = False
        self.databases = []

    def setcontent(self, content):
        """Tsy maintsy antsoina ity lefa ity alohan'ny miantso ny lefa hafa
           (manipy AssertionError ireo lefa ireo raha tsy manao izany)"""
        self.content = content
        self.loaded_flag = True

    def sort(self):
        """Fampirimana ny dikanteny azo amin'ny alalan'ny REGEX araka ny laharan'ny Abidy"""
        assert self.loaded_flag is True

        if self.content.find('{{}} :') == -1: return self.content
        trads = re.findall("# (.*) : \[\[(.*)\]\]", self.content)
        trads.sort()
        trstr = '{{}} :'
        tran = self.content.replace('{{}} :', '')
        if len(trads) > 200:
            if verbose: print 'hadisoana ?'
            return tran
        for i in trads:
            trstr = trstr.replace("{{}} :", "# %s : [[%s]]\n{{}} :" % i)
            tran = self.content.replace('\n\n', '\n')
        trstr = trstr.strip('\n')
        trstr = re.sub("(\\n)+", "\n", trstr)
        tran = self.content.replace("{{-dika-}}", "{{-dika-}}\n%s" % trstr)

        self.loaded_flag = False
        return self.content.strip('\n')

    def add(self, translations, sort=True):
        """ Afaka mampiditra ny dikanteny eo ambany"""
        assert self.loaded_flag is True

        translations = list(set(translations))
        if sort:
            translations.sort()
        for foreign_translations_tuple in translations[::-1]:
            self.content = self._add(foreign_translations_tuple[0], foreign_translations_tuple[1])

        self.loaded_flag = False
        return self.content

    def delete(self):
        """ Mamerina ny votoatim-pejy tsy misy ny dikanteny."""
        # c1 = self.content.find("{{-dika-}}")
        assert self.loaded_flag is True
        self.content = re.sub(u"# \{\{[a-z]+\}\} : (.*)[\n]?", "", self.content)

        self.loaded_flag = False
        return self.content  # tuple (entry, lang)

    def get(self):
        """ Maka ny dikanteny rehetran'ny votoatim-pejy."""
        assert self.loaded_flag is True
        translations = re.findall("\{\{dikan\-teny|(.*)|([a-z]+)\}\}", self.content)
        translations.sort()

        self.loaded_flag = False
        return translations

    def _add(self, langcode, translation):
        """ Tao fanampiana dikanteny. Mamerina ny votoatim-pejy misy ny dikanteny."""
        try:
            langcode = unicode(langcode)
        except UnicodeError:
            return self.content

        try:
            translation = unicode(translation, 'utf8')
        except UnicodeDecodeError:
            translation = unicode(translation, 'latin1')
        except TypeError:
            pass

        if self.content.find("{{-dika-}}") != -1:
            if self.content.find("{{%s}} :" % (langcode)) != -1:
                if self.content.find(u"{{dikan-teny|%s|%s}}" % (translation, langcode)) != -1:
                    self.content = re.sub("[ ]?\{\{dikan\-teny\|%s\|%s\}\}[\,]?" % (translation, langcode), u"",
                                          self.content)
                    self.content = self.content.replace("# {{%s}} :" % (langcode),
                                                        u"# {{%s}} : {{dikan-teny|%s|%s}}," % (
                                                            langcode, translation, langcode))
                else:
                    self.content = self.content.replace("# {{%s}} :" % (langcode),
                                                        u"# {{%s}} : {{dikan-teny|%s|%s}}," % (
                                                            langcode, translation, langcode))
            else:
                self.content = self.content.replace("{{-dika-}}",
                                                    u"{{-dika-}}\n# {{%s}} : {{dikan-teny|%s|%s}}" % (
                                                        langcode, translation, langcode))

        return self.content


class Translation(TranslationsHandler):
    def __init__(self, data_file):
        """Mandika teny ary pejy @ teny malagasy"""
        super(self.__class__, self).__init__()
        self.sql_db = BJDBmodule.Database()
        self.word_db = BJDBmodule.WordDatabase()

        self.databases.append(self.word_db)
        self.databases.append(self.sql_db)
        self.data_file = data_file
        self.output = Output()
        self.iso2languagename = {}
        self.errlogfile = file(self.data_file + 'dikantenyvaovao.exceptions', 'a')
        self.langblacklist = ['fr', 'en', 'sh', 'ar', 'de', 'zh']
        self.entryprocessors = {}
        self.translationslist = []

    def _codetoname(self, languageISO):
        if self.iso2languagename == {}:
            # initialise variable
            langfile = open(self.data_file + "iso2name.txt", 'r')
            for line in langfile.readlines():
                line = line.split(':')
                self.iso2languagename[line[0]] = line[1]
        else:
            return self.iso2languagename

    @staticmethod
    def process_interwiki(lang, Page):
        summary = "Interwiki mivantana [v1]: "
        langlinks = []

        if Page.isRedirectPage():
            return
        if Page.exists():
            langlinks = re.findall("\[\[([a-z]{2,3}):(.*)\]\]", Page.get())
        mgpage = pwbot.Page(pwbot.Site('mg', 'wiktionary'), Page.title())

        if mgpage.exists():
            opage_c = mgpage.get()
            mgpage_c = mgpage.get()
            mgpagelanglinks = re.findall("\[\[([a-z]{2,3}):(.*)\]\]", mgpage_c)
            mgpage_c = re.sub("\n\[\[([a-z]{2,3}):(.*)\]\]", "", mgpage_c)
            mgpage_c = re.sub("\[\[([a-z]{2,3}):(.*)\]\]", "", mgpage_c)
            mgpage_c = re.sub("\n\[\[mg:(.*)\]\]", "", mgpage_c)

            if mgpage_c.find(u"\n[[%s:%s]]" % (lang, Page.title())) == -1 and lang != 'mg':
                summary += u"%s, " % lang
                # mgpage_c += u"\n[[%s:%s]]"%((lang, Page.title()))

            if len(langlinks) - 1 < len(mgpagelanglinks):
                return

            langlinks.append((lang, Page.title()))

            langlinks.sort()
            mgpagelanglinks.sort()
            tobeadded = list(mgpagelanglinks)

            for langlink in langlinks:
                if langlink not in mgpagelanglinks:
                    if langlink[0] == 'mg':  # rohy anaty tenin'ny wiki iasana (diso)
                        continue
                    tobeadded.append(langlink)
                    summary += u"%s, " % langlink[0]

            tobeadded.sort()
            for langlink in tobeadded:
                iw = u"\n[[%s:%s]]" % langlink
                mgpage_c += iw

            summary = summary.strip(u", ")
            if opage_c != mgpage_c:
                pwbot.showDiff(opage_c, mgpage_c)
                mgpage.put_async(mgpage_c, summary)

    def get_allwords(self):
        alldata = self.sql_db.load()
        ret = {}
        for data in alldata:
            if data[5] in ret:
                ret[data[5]].append(unicode(data[1], 'latin1'))
            else:
                ret[data[5]] = [unicode(data[1], 'latin1')]
        return ret

    def get_alltranslations(self, language='en'):
        alldata = self.sql_db.read({'fiteny': language})
        ret = {}
        for data in alldata:
            if ret.has_key(data[1]):
                ret[data[1]] = unicode(data[3], 'latin1')
            else:
                ret[data[1]] = unicode(data[3], 'latin1')
        return ret

    def translate_word(self, word, language='fr'):
        tr = self.word_db.translate(word, language)
        if not tr:
            raise NoWordException()
        else:
            return tr

    # TODO : refactor
    def process_wiktionary_page(self, language, Page):
        # fanampiana : Page:Page
        def save_translation_from_bridge_language(self, infos):
            summary = "Dikan-teny avy amin'ny dikan-teny avy amin'i %(olang)s.wiktionary" % infos
            wikipage = self.output.wikipage(infos)
            try:
                mg_Page = pwbot.Page(pwbot.Site('mg', 'wiktionary'), infos['entry'])
            except UnicodeDecodeError:
                mg_Page = pwbot.Page(pwbot.Site('mg', 'wiktionary'), infos['entry'].decode('utf8'))

            try:
                if mg_Page.exists():
                    pagecontent = mg_Page.get()
                    if pagecontent.find('{{=%s=}}' % infos['lang']) != -1:
                        if verbose:
                            print "Efa misy ilay teny iditra."
                        self.output.db(infos)
                        return
                    else:
                        wikipage += pagecontent
                        summary = u"+" + summary
            except pwbot.exceptions.IsRedirectPage:
                infos['entry'] = mg_Page.getRedirectTarget().title()
                save_translation_from_bridge_language(self, infos)
                return

            except pwbot.exceptions.InvalidTitle:
                if verbose: print "lohateny tsy mety ho lohatenim-pejy"
                return

            except Exception as e:
                if verbose: print e
                return

            if verbose:
                pwbot.output("\n \03{red}%(entry)s\03{default} : %(lang)s " % infos)
                pwbot.output("\03{white}%s\03{default}" % wikipage)
            mg_Page.put_async(wikipage, summary)
            self.output.db(infos)

        def save_translation_from_page(self, infos):
            summary = "Dikan-teny avy amin'ny pejy avy amin'i %(olang)s.wiktionary" % infos
            wikipage = self.output.wikipage(infos)
            mg_page = pwbot.Page(pwbot.Site('mg', 'wiktionary'), infos["entry"])
            if mg_page.exists():
                pagecontent = mg_page.get()
                if pagecontent.find('{{=%s=}}' % infos['lang']) != -1:
                    if verbose: print "Efa misy ilay teny iditra, fa mbola tsy fantatry ny banky angona izany."
                    self.output.db(infos)
                    return
                else:
                    wikipage += pagecontent
                    summary = u"+" + summary
                    # wikipage = autocleanup.alphasort(wikipage)

            pwbot.output(u"\03{default}>>> \03{lightgreen}%(entry)s\03{default}" % infos
                         + u"<<<\n\03{lightblue}%s\03{default}" % wikipage)
            mg_page.put_async(wikipage, summary)
            self.output.db(infos)

        def generate_redirections(self, infos):
            redirtarget = infos['entry']
            if infos['lang'] in ['ru', 'uk', 'bg', 'be']:
                for char in u"́̀":
                    if redirtarget.find(char) != -1:
                        redirtarget = redirtarget.replace(char, u"")
                if redirtarget.find(u"æ") != -1:
                    redirtarget = redirtarget.replace(u"æ", u"ӕ")
                if infos['entry'] != redirtarget:
                    pwbot.Page(pwbot.Site('mg', 'wiktionary'),
                               infos['entry']).put_async(u"#FIHODINANA [[%s]]" % redirtarget, "fihodinana")
                    infos['entry'] = redirtarget

        def append_in(infos, translations_in_mg):  # TRANSLATION HANDLING SUBFUNCTION
            for mgtranslation in infos['definition'].split(","):
                mgtranslation = mgtranslation.strip()
                if translations_in_mg.has_key(mgtranslation):
                    translations_in_mg[mgtranslation].append((infos["lang"], infos["entry"]))
                else:
                    translations_in_mg[mgtranslation] = []
                    translations_in_mg[mgtranslation].append((infos["lang"], infos["entry"]))

        # BEGINNING
        ret = 0
        if verbose: print "Praosesera:", language.upper()
        if language in self.entryprocessors:
            processor_class = self.entryprocessors[language]
        else:
            try:
                self.entryprocessors[language] = entryprocessor.WiktionaryProcessorFactory.new_wiktionary_processor(
                    language)
                processor_class = self.entryprocessors[language]
            except NotImplementedError:
                return 0

        if verbose: pwbot.output("\n >>> \03{lightgreen}%s\03{default} <<< " % Page.title())

        if Page.title().find(':') != -1:
            if verbose:
                print "Nahitana ':' tao anaty anaram-pejy"
            return ret
        if Page.namespace() != 0:
            if verbose:
                print "Tsy amin'ny anaran-tsehatra fotony"
            return ret
        processor_class.process(Page)

        try:
            entries = processor_class.getall()
        except Exception as e:
            return 0

        translations_in_mg = {}  # dictionary {string : list of translation tuple (see below)}
        for entry in entries:
            # entry = (self.title, pos, self.lang2code(l), defin.strip())
            if entry[2] == language:  # if entry in the content language
                # (self.title, pos, self.lang2code(l), defin.strip())
                try:
                    translations = processor_class.retrieve_translations()
                except Exception:
                    continue
                translations_in_mg = {}  # dictionary {string : list of translation tuple (see below)}
                for translation in translations:
                    # translation = tuple(codelangue, entree)
                    if translation[2] in self.langblacklist:  # check in language blacklist
                        if verbose: print "Fiteny voalisi-mainty: ", translation[2]
                        continue
                    try:
                        mg_translation = self.translate_word(Page.title(), language)
                    except NoWordException:
                        if verbose: pwbot.output(
                            "Tsy nahitana dikantenin'i '%s' ho an'ny teny '%s' tao amin'ny banky angona" % (
                                Page.title(), language))
                        break
                    infos = {
                        'entry': translation[0],
                        'POS': translation[1],
                        'definition': mg_translation,
                        'lang': translation[2],
                        'olang': language,
                        'origin': Page.title()}

                    if self.word_db.exists(infos['entry'], infos['lang']):
                        # print "Efa fantatra tamin'ny alalan'ny banky angona ny fisian'ilay teny"
                        continue

                    generate_redirections(self, infos)
                    append_in(infos, translations_in_mg)
                    if verbose:
                        print translations_in_mg
                    save_translation_from_bridge_language(self, infos)
                    ret += 1

                    # Malagasy language pages

            else:
                # (self.title, pos, self.lang2code(l), defin.strip())
                if entry[2] in self.langblacklist:
                    if verbose:
                        print "Fiteny voalisi-mainty:", entry[2]
                    continue
                title = Page.title()
                try:
                    mg_translation = self.translate_word(entry[3], language)
                except NoWordException:
                    if verbose: pwbot.output(
                        "\03{yellow}Tsy nahitana dikantenin'i '%s' ho an'ny teny '%s' tao amin'ny banky angona\03{default}" % (
                            entry[3], language))
                    continue

                infos = {
                    'entry': title,
                    'POS': entry[1],
                    'definition': mg_translation,
                    'lang': entry[2],
                    'olang': language,
                    'origin': entry[3]}

                if verbose: pwbot.output(
                    "\03{red}%(entry)s\03{default}: dikanteny vaovao amin'ny teny '%(lang)s' " % infos)
                if self.word_db.exists(infos['entry'], infos['lang']):
                    if verbose:
                        print "Efa fantatra tamin'ny alalan'ny banky angona ny fisian'ilay teny"
                    continue

                generate_redirections(self, infos)
                append_in(infos, translations_in_mg)
                if verbose:
                    print translations_in_mg
                save_translation_from_bridge_language(self, infos)
                save_translation_from_page(self, infos)

                ret += 1

        # Malagasy language pages
        # self.update_malagasy_word(translations_in_mg)
        if verbose:
            print " Vita."
        return ret

    def update_malagasy_word(self, translations_in_mg):
        # Malagasy language pages
        def update_malagasy_word(word, translations):
            mg_entry_page = pwbot.Page(pwbot.Site('mg', 'wiktionary'), word)
            try:
                self.setcontent(mg_entry_page.get())
                content = self.add(translations)
                mg_entry_page.put_async(content, "+dikanteny")
            except pwbot.IsRedirectPage:
                redirtarget = mg_entry_page.getRedirectTarget()
                if verbose:
                    pwbot.output("Pejy fihodinana '%s', manakatra ny tanjony: '%s'" %
                                 (mg_entry_page.title(), redirtarget.title()))
                redirtarget = mg_entry_page.getRedirectTarget()
                update_malagasy_word(redirtarget.title(), translations)

            except pwbot.NoPage:
                if verbose:
                    pwbot.output("Tsy misy ilay pejy '%s'" % mg_entry_page.title())
                return
            except Exception as e:
                if verbose:
                    pwbot.output("Nisy hadisoana.")
                return

        if verbose:
            print "Manavao ny pejy malagasy...", "dikanteny %d" % len(translations_in_mg)
        for translation_in_mg in translations_in_mg:
            translation_in_mg = translation_in_mg.strip()
            for char in '[]':
                translation_in_mg = translation_in_mg.replace(char, '')

            translation_in_mg = unicode(translation_in_mg)
            update_malagasy_word(translation_in_mg, translations_in_mg[translation_in_mg])
        if verbose:
            print "tafapetraka ny dikanteny"

    def exists(self, lang, ent):
        try:
            ent = ent.decode('utf8')
        except UnicodeEncodeError:
            pass

        try:
            lang = unicode(lang, 'latin1')
        except TypeError:
            pass

        if self.translationslist.count((lang, ent)) >= 1:
            return True
        else:
            # pwbot.output(u"mitady an'i teny \"%s\" ao amin'ny banky angona..."%ent)
            if ent == 'en':
                return self.word_db.exists(ent, lang)
            self.translationslist.append((lang, ent))
            # print type(lang), type(ent)
            return self.word_db.exists(ent, lang)
