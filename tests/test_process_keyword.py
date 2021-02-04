import json
import unittest

from compacting_keys import DBpedia_wrapper
from src import tfg_nlp


class TestProcessKeyword(unittest.TestCase):

    def test_ThinkingAloud(self):
        keyword = "thinking aloud"
        result = tfg_nlp.process(keyword)["result"]
        print(json.dumps(result, indent=1, ensure_ascii=False).encode('utf-8').decode())
        self.assertEqual("en", result["lang"])
        self.assertEqual("http://www.wikidata.org/entity/Q97955101", result["Wikidata"])

    def test_SemanticWeb(self):
        keywords = ["web semàntica", "semantic web", "web semántica"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual("http://www.wikidata.org/entity/Q54837", result["result"]["Wikidata"])

    def test_Acronym(self):
        keywords = ["artificial intelligence", "AI"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual("http://dbpedia.org/resource/Artificial_intelligence", result["result"]["DBpedia"])

    def test_case_different_description(self):
        keywords = ["copyright"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual("http://www.wikidata.org/entity/Q1297822", result["result"]["Wikidata"])

    def test_case_different_description2(self):
        keywords = ["search"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual("http://www.wikidata.org/entity/Q671718", result["result"]["Wikidata"])

    def test_case_different_description3(self):
        keywords = ["navegación"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual("http://www.wikidata.org/entity/Q1972518", result["result"]["Wikidata"])

    def test_case_numbers(self):
        keywords = ["1917"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual("http://www.wikidata.org/entity/Q2092", result["result"]["Wikidata"])

    def test_case_punctuation_mark(self):
        keywords = ["long-range interactions"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual("http://www.wikidata.org/entity/Q63926701", result["result"]["Wikidata"])

    def test_case_punctuation_mark2(self):
        keywords = ["qrt-pcr"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual("http://dbpedia.org/resource/Polymerase_chain_reaction", result["result"]["DBpedia"])

    def test_case_other_language(self):
        keywords = ["wilkomen"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual(None, result["result"]["Wikidata"])

    def test_case_name_of_person(self):
        keywords = ["antonio del amo"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual("http://www.wikidata.org/entity/Q607975", result["result"]["Wikidata"])

    def test_case_strange_character(self):
        keywords = ["β-catenin"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual("http://www.wikidata.org/entity/Q10861922", result["result"]["Wikidata"])

    def test_case_article(self):
        keywords = ["article"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual("http://www.wikidata.org/entity/Q191067", result["result"]["Wikidata"])

    def test_case_journal(self):
        keywords = ["journal"]
        results = [tfg_nlp.process(keyword) for keyword in keywords]
        print(json.dumps(results, indent=1, ensure_ascii=False).encode('utf-8').decode())
        for result in results:
            self.assertEqual("http://www.wikidata.org/entity/Q41298", result["result"]["Wikidata"])


if __name__ == '__main__':
    unittest.main()
