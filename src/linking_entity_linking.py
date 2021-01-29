import json
import logging
from functools import reduce
from webbrowser import Error

import requests
import time

from sklearn.base import TransformerMixin, BaseEstimator

WIKIDATA_BASE = "https://www.wikidata.org/w"
DBPEDIA_BASE = 'http://dbpedia.org'
DBPEDIA_SPOTLIGHT_BASE = 'http://api.dbpedia-spotlight.org/en'
DBPEDIA_SPOTLIGHT_MAX_CHARS = 15000
OWL_SAME_AS = 'http://www.w3.org/2002/07/owl#sameAs'

logger = logging.getLogger(__name__)


class DBPediaEntityLinker(BaseEstimator, TransformerMixin):
    """

    """

    def __init__(self, confidence_threshold=0.4, throttling_time=5):
        self.confidence = confidence_threshold
        self.throttling_time = throttling_time

    def fit(self, X, y=None):
        return self

    def transform(self, X, *args, **kwargs):
        return [self.link_entities(text[:DBPEDIA_SPOTLIGHT_MAX_CHARS])
                for text in X]

    def link_entities(self, text):
        """
        """
        payload = {'text': text}
        reqheaders = {'accept': 'application/json'}
        res = requests.get(f"{DBPEDIA_SPOTLIGHT_BASE}/annotate",
                           params=payload,
                           headers={"accept": "application/json"})
        while res.status_code == 403:
            logger.warn("DBPedia spotlight limit reached. Retrying in %d seconds...",
                        self.throttling_time)
            time.sleep(self.throttling_time)
            res = requests.get(f"{DBPEDIA_SPOTLIGHT_BASE}/annotate",
                               params=payload,
                               headers={"accept": "application/json"})

            print(res)

        res_dict = json.loads(res.content)
        if 'Resources' not in res_dict:
            return None
        for resource in res_dict['Resources']:
            return resource['@URI']


class WikidataEntityLinker(BaseEstimator, TransformerMixin):
    """ Link a list of entities to Wikidata.

    This transformer receives entities in a string form, and
    returns a tuple (entity_name, entity_uri) for each entity
    with its original name and URI in Wikidata.
    """

    def __init__(self):
        self.linked_entities_cache = {}

    def fit(self, X, y=None):
        return self

    def pick_preferred(self, x):
        for element in x:
            if 'description' in element:
                if 'article' not in element.get('description'):
                    return element
            else:
                return element

    def link_entity(self, entity_label, language):
        """ Links a single entity to Wikidata.

        Parameters
        ----------
        entity_label : str
            Name of the entity to be linked.
        language: str
            Preferred language for linking (en, es,...)
        
        Returns
        -------
        (str, str)
            Tuple where the first element is the name of the entity,
            and the second one is its 'QID' from Wikidata after linking.
            The result with the shortest label and smallest QID is selected.
        """
        if entity_label in self.linked_entities_cache:
            return self.linked_entities_cache[entity_label]

        url = f"{WIKIDATA_BASE}/api.php?action=wbsearchentities&search=" + \
              f"{entity_label}&limit=15&language={language}&format=json"
        response = requests.get(url)
        if response.status_code != 200:
            raise Error()

        try:
            content = json.loads(response.text)
        except:
            # invalid entity
            self.linked_entities_cache[entity_label] = None
            return self.link_entity(entity_label, language)

        search_results = content['search']
        if len(search_results) == 0:
            self.linked_entities_cache[entity_label] = None
            return self.link_entity(entity_label, language)
        result = self.pick_preferred(search_results)
        if result is None:
            self.linked_entities_cache[entity_label] = None
        else:
            self.linked_entities_cache[entity_label] = result['concepturi']
        return self.link_entity(entity_label, language)
