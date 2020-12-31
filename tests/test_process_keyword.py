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


if __name__ == '__main__':
    unittest.main()
