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

if __name__ == '__main__':
    unittest.main()
