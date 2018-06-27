from api.parsers.constants import CASES, GENDER, NUMBER, DEFINITENESS, POSSESSIVENESS
from api.parsers.inflection_template import NounForm, AdjectiveForm


def parse_one_parameter_template(out_class, template_name='plural of', case_name='', number='s', gender=None,
                                 definiteness=None):
    """
    Very generic code that can parse anything like {{plural of|xxyyzz}}, which is very common on en.wiktionary
    Use with caution, though.
    :param out_class:
    :param template_name:
    :param case_name:
    :param number:
    :param gender:
    :return: a function which sould return the contents of the template specified in template_name
    """
    def _parse_one_parameter_template(template_expression):
        for char in '{}':
            template_expression = template_expression.replace(char, '')
        parts = template_expression.split('|')
        lemma = parts[1]
        if parts[0] == template_name:
            ret_obj = out_class()
            ret_obj.lemma = lemma
            ret_obj.gender = gender
            ret_obj.case = case_name
            ret_obj.number = number
            ret_obj.definite = definiteness
            return ret_obj
        else:
            raise ValueError("Unrecognised template: expected '%s' but got '%s'" % (parts[0], template_name))

    return _parse_one_parameter_template


def parse_inflection_of(out_class):
    def _parse_inflection_of_partial(template_expression):
        for char in '{}':
            template_expression = template_expression.replace(char, '')
        parts = template_expression.split('|')
        for tparam in parts:
            if tparam.find('=') != -1:
                parts.remove(tparam)
        t_name, lemma = parts[:2]
        case_name = number_ = ''
        gender = None
        definiteness = None
        for pn in parts:
            if pn in NUMBER:
                number_ = pn
            elif pn in CASES:
                case_name = pn
            elif pn in GENDER:
                gender = pn
            elif pn in DEFINITENESS:
                definiteness = pn

        ret_obj = out_class(lemma=lemma, case=case_name, number=number_, gender=gender)
        ret_obj.definite = definiteness
        return ret_obj

    return _parse_inflection_of_partial


def parse_hu_inflection_of(template_expression):
    for char in '{}':
        template_expression = template_expression.replace(char, '')
    parts = template_expression.split('|')
    for tparam in parts:
        if tparam.find('=') != -1:
            parts.remove(tparam)
    t_name, lemma = parts[:2]
    case_name = number_ = ''
    gender = None
    definiteness = None
    possessiveness = None
    for pn in parts:
        if pn in NUMBER:
            number_ = pn
        elif pn in CASES:
            case_name = pn
        elif pn in GENDER:
            gender = pn
        elif pn in DEFINITENESS:
            definiteness = pn
        elif pn in POSSESSIVENESS:
            possessiveness = pn

    ret_obj = NounForm(lemma=lemma, case=case_name, number=number_, gender=gender, possessive=possessiveness)
    ret_obj.definite = definiteness
    return ret_obj


def parse_el_form_of(out_class, lemma_pos=1):
    assert out_class in (NounForm, AdjectiveForm)
    def _wrapped_parse_el_form_of(template_expression):
        for char in '{}':
            template_expression = template_expression.replace(char, '')

        parts = template_expression.split('|')
        number = case = None
        lemma = parts[lemma_pos]
        for tparam in parts:
            if '=' in tparam:
                if tparam.startswith('n='):
                    number = tparam[2:]
                if tparam.startswith('c='):
                    case = tparam[2:]
            elif tparam:
                lemma = tparam

        noun_form = out_class(lemma, case, number, '')
        return noun_form

    return _wrapped_parse_el_form_of