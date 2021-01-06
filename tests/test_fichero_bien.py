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

    def test_remove_multiple_white_spaces(self):
        actual = "Aixo  es   un     test"
        expected = "Aixo es un test"

        self.assertEqual(tfg_nlp.remove_multiple_white_spaces(actual), expected)

    def test_punctuation_mark_coma(self):
        row1 = ['https://vivo.invid.udl.cat/individual/UDL-00000467',
                "colonic metabolism; microbiome; polyphenols;phenol metabolism; ultra-performance liquid chromatography mass spectrometry; wine"]

        row2 = [["https://vivo.invid.udl.cat/individual/UDL-00000467","colonic metabolism"],
                ["https://vivo.invid.udl.cat/individual/UDL-00000467", "microbiome"],
                ["https://vivo.invid.udl.cat/individual/UDL-00000467", "polyphenols"],
                ["https://vivo.invid.udl.cat/individual/UDL-00000467", "phenol metabolism"],
                ["https://vivo.invid.udl.cat/individual/UDL-00000467", "ultra-performance liquid chromatography mass spectrometry"],
                ["https://vivo.invid.udl.cat/individual/UDL-00000467", "wine"]]

        actual = pd.DataFrame(row1, columns=['resource', 'keyword'])
        expected = pd.DataFrame(row2, columns=['resource', 'keyword'])

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
