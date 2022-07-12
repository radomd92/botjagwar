import re

from api.parsers.constants.fr import \
    VOICE, MOOD, CASES, TENSE, NUMBER, PERSONS, DEFINITENESS, GENDER, POSSESSIVENESS
from api.parsers.inflection_template import VerbForm


def parse_fr_definition(definition_line):
    definition_line = definition_line.lower()
    definition_line = definition_line.replace("''", '')

    returned = VerbForm()

    for determiner in [
        ' du verbe ', ' de l’', ' de ', ' du ', ' de la ', ' des ']:
        definition_line = definition_line.replace(determiner, ' ')

    for voice in VOICE:
        if voice in definition_line:
            returned.voice = VOICE[voice]
            definition_line = definition_line.replace(voice, '')

    for mood in MOOD:
        if mood in definition_line:
            returned.mood = MOOD[mood]
            definition_line = definition_line.replace(mood, '')

    returned.mood = 'indicative' if returned.mood is None else returned.mood

    for cases in CASES:
        if cases in definition_line:
            returned.case = CASES[cases]
            definition_line = definition_line.replace(cases, '')

    for tense in TENSE:
        if tense in definition_line:
            returned.tense = TENSE[tense]
            definition_line = definition_line.replace(tense, '')

    returned.tense = 'present' if returned.tense is None else returned.tense

    for number in NUMBER:
        if number in definition_line:
            returned.number = NUMBER[number]
            definition_line = definition_line.replace(number, '')

    returned.number = 'singular' if returned.number is None else returned.number

    for persons in PERSONS:
        if persons in definition_line:
            returned.person = PERSONS[persons]
            definition_line = definition_line.replace(persons, '')

    for definiteness in DEFINITENESS:
        if definiteness in definition_line:
            returned.definiteness = DEFINITENESS[definiteness]
            definition_line = definition_line.replace(definiteness, '')

    for gender in GENDER:
        if gender in definition_line:
            returned.gender = GENDER[gender]
            definition_line = definition_line.replace(gender, '')

    for possessiveness in POSSESSIVENESS:
        if possessiveness in definition_line:
            returned.possessiveness = POSSESSIVENESS[possessiveness]
            definition_line = definition_line.replace(possessiveness, '')

    definition_line = definition_line.strip()
    lemma = re.sub('{{lien\|(.*)\|(.*)}}.', '\\1', definition_line)
    lemma = re.sub('\[\[(.*)]].', '\\1', lemma)
    returned.lemma = lemma
    return returned
