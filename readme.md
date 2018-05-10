
## What is `botjagwar` for?

Bot-Jagwar is a side project which aims to automate editing on the Malagasy Wiktionary as much as possible.

## Current build status
[![master](https://travis-ci.org/radomd92/botjagwar.svg?branch=master)]
[![dev](https://travis-ci.org/radomd92/botjagwar.svg?branch=dev)]

## Prerequisites

You'll need a working Python 3.6 interpreter to run the python scripts of this project.

## Installation

In the project directory, type `make all`. The Python scripts and the required configuration will be deployed on the target machine at `/opt/botjagwar`. They can be removed with
`make uninstall`. 

If you intend to use the bot for editing on Wiktionary, you need to set up your pywikibot instance. 
Visit [Pywikibots installation manual](https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation) for more details on how to do that.

To confirm whether you have a working installation, run `make test`. All tests should pass.
However, some of them may not pass on the Raspberry Pi due files not being deleted after teardowns.


## Components and scripts

### Real-time lemma translator
#### wiktionary_irc.py

Connects to the recent changes real time feed of French and English Wiktionaries on `irc.wikimedia.org` and attempts to translate every entries
that are being created.

#### dictionary_service.py

Word storage engine. REST API required by the `wiktionary_irc.py` to store and get translations.

#### entry_translator.py

Wiki page handling that also uses translation and page rendering APIs. Side effects are page updates and creations to the target wiki.
REST service required by `wiktionary_irc.py`  

### word_forms.py

Independent script to translate non-lemma entries on the English Wiktionary into Malagasy.

### list_wikis.py

Independent script that updates the statistics table for each Wiktionary, Wikipedia and Wikibooks and stores it to the user's subpage on the Malagasy Wiktionary

### unknown_language_management.py

Independent script, which, in detail:
- fetches the words created in the last 30 days;
- checks the missing language templates, and translates them in malagasy with a basic phonetic transcription algorithm;
-- if the language name could be translated: creates the templates and categories for the missing language; or
-- stores a list of untranslated language names in a table, stored on the Malagasy wiktionary at `Mpikambana:<USERNAME>/Lisitry ny kaodim-piteny tsy voafaritra`

## Copyright

© 2018 Rado A. (Terakasorotany) -- MIT Licence.
