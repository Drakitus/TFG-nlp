import unittest

from linking_entity_linking import WikidataEntityLinker, DBPediaEntityLinker


class TestWikidataEntityLinking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wikidata_linker = WikidataEntityLinker()

    def test_wikidata_linking_en(self):
        entity = self.wikidata_linker.link_entity('e-learning', "en")
        self.assertEqual(entity, 'http://www.wikidata.org/entity/Q1068473')

    def test_wikidata_linking_es(self):
        entity = self.wikidata_linker.link_entity('usabilidad', "es")
        self.assertEqual(entity, 'http://www.wikidata.org/entity/Q216378')

    def test_wikidata_linking_ca(self):
        entity = self.wikidata_linker.link_entity('accessibilitat', "ca")
        self.assertEqual(entity, 'http://www.wikidata.org/entity/Q555097')


class TestDBpediaEntityLinking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dbpedia_linker = DBPediaEntityLinker()

    def test_wikidata_linking(self):
        entity = self.dbpedia_linker.link_entities('e-learning')
        self.assertEqual(entity, 'http://dbpedia.org/resource/Educational_technology')


if __name__ == '__main__':
    unittest.main()
