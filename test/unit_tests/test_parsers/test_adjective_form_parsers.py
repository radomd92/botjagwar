from unittest import TestCase

from api.parsers.functions import parse_el_form_of
from api.parsers.functions import parse_inflection_of
from api.parsers.functions import parse_one_parameter_template
from api.parsers.functions.adjective_forms import parse_adjective_form
from api.parsers.inflection_template import AdjectiveForm


class TestAdjectiveFormParsers(TestCase):
    def test_parse_adjective_form(self):
        template_expression = '{{es-adj form of|minúsculo|f|sg}}'
        output = parse_adjective_form(template_expression)
        self.assertIsInstance(output, AdjectiveForm)
        self.assertEqual(output.number, 'sg')
        self.assertEqual(output.gender, 'f')
        self.assertEqual(output.lemma, 'minúsculo')

    def test_parse_inflection_of_adjective_form(self):
        template_expression = '{{inflection of|abdominālis||voc|f|p|lang=la}}'
        func = parse_inflection_of(AdjectiveForm)
        output = func(template_expression)
        self.assertIsInstance(output, AdjectiveForm)
        self.assertEqual(output.lemma, 'abdominālis')
        self.assertEqual(output.number, 'p')
        self.assertEqual(output.gender, 'f')
        self.assertEqual(output.case, 'voc')

    def test_parse_one_parameter_template(self):
        template_expression = '{{feminine singular of|comparatif|lang=fr}}'
        func = parse_one_parameter_template(AdjectiveForm, 'feminine singular of', number='s', definiteness='definite')
        output = func(template_expression)
        self.assertEqual(output.number, 's')
        self.assertEqual(output.definite, 'definite')
        self.assertEqual(output.lemma, 'comparatif')

    def test_parse_el_form_of_adjective(self):
        template_expression = '{{el-form-of-nounadj|αβοκέτα|c=gen|n=s}}'
        output = parse_el_form_of(AdjectiveForm)(template_expression)
        self.assertIsInstance(output, AdjectiveForm)
        self.assertEqual(output.number, 's')
        self.assertEqual(output.case, 'gen')
        self.assertEqual(output.lemma, 'αβοκέτα')
