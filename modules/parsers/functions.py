# coding: utf8

from .inflection_template import WordForm


def parse_one_parameter_template(template_name='plural of', case_name='', number='s', gender=None):
    """
    Very generic code that can parse anything like {{plural of|xxyyzz}}, which is very common on en.wiktionary
    Use with caution, though.
    :param template_expression:
    :return: a function which sould return the contents of the template specified in template_name
    """
    def _parse_one_parameter_template(template_expression):
        for char in '{}':
            template_expression = template_expression.replace(char, '')
        parts = template_expression.split('|')
        lemma = parts[1]
        if parts[0] == template_name:
            return WordForm(lemma, case_name, number, gender=gender)
        else:
            raise ValueError("Unrecognised template: expected '%s' but got '%s'" % (parts[0], template_name))

    return _parse_one_parameter_template


def parse_lv_inflection_of(template_expression):
    """Example of recognised template:
        {{lv-inflection of|bagātīgs|dat|p|f||adj}}
       Should return 4 parameter """
    for char in '{}':
        template_expression = template_expression.replace(char, '')
    parts = template_expression.split('|')
    for tparam in parts:
        if tparam.find('=') != -1:
            parts.remove(tparam)
    t_name, lemma, case_name, number_, gender = parts[:5]
    return WordForm(lemma, case_name, number_, gender)


def parse_inflection_of(template_expression):
    for char in '{}':
        template_expression = template_expression.replace(char, '')
    parts = template_expression.split('|')
    for tparam in parts:
        if tparam.find('=') != -1:
            parts.remove(tparam)
    t_name, lemma, _, case_name, number_ = parts[:5]
    return WordForm(lemma, case_name, number_, gender=None)