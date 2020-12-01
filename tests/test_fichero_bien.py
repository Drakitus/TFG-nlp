import unittest

import pandas as pd
from src import tfg_nlp


class TestFicheroBien(unittest.TestCase):

    def test_to_lower(self):
        actual = "HOlA"
        expected = "hola"

        self.assertEqual(tfg_nlp.to_lower(actual), expected)

    def test_to_lower_lower(self):
        actual = "hola"
        expected = "hola"

        self.assertEqual(tfg_nlp.to_lower(actual), expected)

    def test_to_lower_random(self):
        actual = "bUeNos dIAs A todOS"
        expected = "buenos dias a todos"

        self.assertEqual(tfg_nlp.to_lower(actual), expected)

    def test_remove_white_spaces(self):
        actual = " hola "
        expected = "hola"

        self.assertEqual(tfg_nlp.remove_white_spaces(actual), expected)

    #def test_remove_multiple_white_spaces(self):
    #    actual = "Aixo  es   un test   "
    #    expected = "Aixo es un test"

    #    self.assertEqual(tfg_nlp.remove_multiple_white_spaces(actual), expected)

    def test_splitter_punctuation_marks(self):
        actual = ["hola - como - estas / que haces; aqui"]
        expected = ["hola", "como", "estas", "que haces", "aqui"]

        self.assertEqual(tfg_nlp.splitter(actual), expected)

    def test_language_en(self):
        actual = "evidence"
        expected = 'en'

        self.assertEqual(tfg_nlp.language_keyword(actual), expected)

    def test_language_es(self):
        actual = "actualidad"
        expected = 'es'

        self.assertEqual(tfg_nlp.language_keyword(actual), expected)

    def test_language_ca(self):
        actual = "igualtat"
        expected = 'ca'

        self.assertEqual(tfg_nlp.language_keyword(actual), expected)





if __name__ == '__main__':
    unittest.main()
