import unittest

import pandas as pd
import io
from src import tfg_nlp


class SimpleTestFileKeywordsSplit(unittest.TestCase):

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

    def test_en_stopwords(self):
        sentence = "This is a sample sentence, showing off the stop words filtration."
        result = ['This', 'sample', 'sentence', ',', 'showing', 'stop', 'words', 'filtration', '.']

        print(tfg_nlp.en_stopWords(sentence))
        self.assertEqual(tfg_nlp.en_stopWords(sentence), result)

    def test_es_stopwords(self):
        sentence = "Esto es un pequeño ejemlo mostrando el filtrado de las palabras de parada"
        result = ['Esto', 'pequeño', 'ejemlo', 'mostrando', 'filtrado', 'palabras', 'parada']

        print(tfg_nlp.es_stopWords(sentence))
        self.assertEqual(tfg_nlp.es_stopWords(sentence), result)

    def test_ca_stopwords(self):
        sentence = "Aixo es un petit exemple que ensenya el filte de les paraules de parada"
        result = ['Aixo', 'petit', 'exemple', 'que', 'ensenya', 'filte', 'paraules', 'parada']

        print(tfg_nlp.ca_stopWords(sentence))
        self.assertEqual(tfg_nlp.ca_stopWords(sentence), result)

    def test_en_lemmatizer(self):
        keyword = "city"
        results = tfg_nlp.process(keyword)

        print("Lemma of %s is: %s" % (keyword, tfg_nlp.en_lemmatizer(keyword)))
        self.assertEqual(tfg_nlp.en_lemmatizer(keyword), results["result"]["lemmatizer"])

    def test_es_lemmarizer(self):
        keyword = "ciudades"
        results = tfg_nlp.process(keyword)

        print("Lemma de %s es: %s" % (keyword, tfg_nlp.es_lemmatizer(keyword)))
        self.assertEqual(tfg_nlp.es_lemmatizer(keyword), results["result"]["lemmatizer"])

    def test_ca_lemmarizer(self):
        keyword = "investigació"
        results = tfg_nlp.process(keyword)

        print("Lemma de %s es: %s" % (keyword, tfg_nlp.ca_lemmatizer(keyword)))
        self.assertEqual(tfg_nlp.ca_lemmatizer(keyword), results["result"]["lemmatizer"])


class ComplexTestFileKeywordsSplit(unittest.TestCase):

    def test_punctuation_mark_coma(self):
        file_in = "files/coma/coma_example.csv"
        file_out = "files/coma/coma_result.csv"
        expected_file = "files/coma/expected_coma.csv"

        df = pd.read_csv(file_in, delimiter=',')

        df.drop_duplicates(subset=None, keep="first", inplace=True)

        df_split = tfg_nlp.splitter(df)

        df_split.to_csv(file_out, index=False)

        with io.open(file_out) as f_out, io.open(expected_file) as expected:
            self.assertListEqual(list(f_out), list(expected))

    def test_punctuation_mark_semicolon(self):
        file_in = "files/semicolon/semicolon_example.csv"
        file_out = "files/semicolon/semicolon_result.csv"
        expected_file = "files/semicolon/expected_semicolon.csv"

        df = pd.read_csv(file_in, delimiter=',')

        df.drop_duplicates(subset=None, keep="first", inplace=True)

        df_split = tfg_nlp.splitter(df)

        df_split.to_csv(file_out, index=False)

        with io.open(file_out) as f_out, io.open(expected_file) as expected:
            self.assertListEqual(list(f_out), list(expected))

    def test_punctuation_mark_dot(self):
        file_in = "files/dot/dot_example.csv"
        file_out = "files/dot/dot_result.csv"
        expected_file = "files/dot/expected_dot.csv"

        df = pd.read_csv(file_in, delimiter=',')

        df.drop_duplicates(subset=None, keep="first", inplace=True)

        df_split = tfg_nlp.splitter(df)

        df_split.to_csv(file_out, index=False)

        with io.open(file_out) as f_out, io.open(expected_file) as expected:
            self.assertListEqual(list(f_out), list(expected))

    def test_punctuation_mark_dash(self):
        file_in = "files/dash/dash_example.csv"
        file_out = "files/dash/dash_result.csv"
        expected_file = "files/dash/expected_dash.csv"

        df = pd.read_csv(file_in, delimiter=',')

        df.drop_duplicates(subset=None, keep="first", inplace=True)

        df_split = tfg_nlp.splitter(df)

        df_split.to_csv(file_out, index=False)

        with io.open(file_out) as f_out, io.open(expected_file) as expected:
            self.assertListEqual(list(f_out), list(expected))

    def test_punctuation_mark_dash(self):
        file_in = "files/slash/slash_example.csv"
        file_out = "files/slash/slash_result.csv"
        expected_file = "files/slash/expected_slash.csv"

        df = pd.read_csv(file_in, delimiter=',')

        df.drop_duplicates(subset=None, keep="first", inplace=True)

        df_split = tfg_nlp.splitter(df)

        df_split.to_csv(file_out, index=False)

        with io.open(file_out) as f_out, io.open(expected_file) as expected:
            self.assertListEqual(list(f_out), list(expected))


if __name__ == '__main__':
    unittest.main()
