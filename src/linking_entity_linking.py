import json
import logging
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
        payload = {'confidence': self.confidence, 'text': text}
        reqheaders = {'accept': 'application/json'}
        res = requests.post(f"{DBPEDIA_SPOTLIGHT_BASE}/annotate",
                            data=payload,
                            headers={"accept": "application/json"})
        while res.status_code == 403:
            logger.warn("DBPedia spotlight limit reached. Retrying in %d seconds...",
                self.throttling_time)
            time.sleep(self.throttling_time)
            res = requests.post(f"{DBPEDIA_SPOTLIGHT_BASE}/annotate",
                            data=payload,
                            headers={"accept": "application/json"})
        
        res_dict = json.loads(res.content)
        if 'Resources' not in res_dict:
            return []
        
        return [(resource['@surfaceForm'], resource['@URI'])
                for resource in res_dict['Resources']]


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
    
    def link_entity_en(self, entity_label):
        """ Links a single entity to Wikidata.

        Parameters
        ----------
        entity_label : str
            Name of the entity to be linked.
        
        Returns
        -------
        (str, str)
            Tuple where the first element is the name of the entity,
            and the second one is its 'QID' from Wikidata after linking.
        """
        if entity_label in self.linked_entities_cache:
            return (self.linked_entities_cache[entity_label])

        url = f"{WIKIDATA_BASE}/api.php?action=wbsearchentities&search=" + \
            f"{entity_label}&language=en&format=json"
        response = requests.get(url)
        if response.status_code != 200:
            raise Error()
        
        try:
            content = json.loads(response.text)
        except:
            # invalid entity
            self.linked_entities_cache[entity_label] = None
            return self.link_entity_en(entity_label)

        search_results = content['search']
        if len(search_results) == 0:
            self.linked_entities_cache[entity_label] = None
            return self.link_entity_en(entity_label)
        
        self.linked_entities_cache[entity_label] = search_results[0]['concepturi']
        return self.link_entity_en(entity_label)

    def link_entity_es(self, entity_label):
        """ Links a single entity to Wikidata.

        Parameters
        ----------
        entity_label : str
            Name of the entity to be linked.

        Returns
        -------
        (str, str)
            Tuple where the first element is the name of the entity,
            and the second one is its 'QID' from Wikidata after linking.
        """
        if entity_label in self.linked_entities_cache:
            return (self.linked_entities_cache[entity_label])

        url = f"{WIKIDATA_BASE}/api.php?action=wbsearchentities&search=" + \
              f"{entity_label}&language=es&format=json"
        response = requests.get(url)
        if response.status_code != 200:
            raise Error()

        try:
            content = json.loads(response.text)
        except:
            # invalid entity
            self.linked_entities_cache[entity_label] = None
            return self.link_entity_es(entity_label)

        search_results = content['search']
        if len(search_results) == 0:
            self.linked_entities_cache[entity_label] = None
            return self.link_entity_es(entity_label)

        self.linked_entities_cache[entity_label] = search_results[0]['concepturi']
        return self.link_entity_es(entity_label)

    def link_entity_ca(self, entity_label):
        """ Links a single entity to Wikidata.

        Parameters
        ----------
        entity_label : str
            Name of the entity to be linked.

        Returns
        -------
        (str, str)
            Tuple where the first element is the name of the entity,
            and the second one is its 'QID' from Wikidata after linking.
        """
        if entity_label in self.linked_entities_cache:
            return (self.linked_entities_cache[entity_label])

        url = f"{WIKIDATA_BASE}/api.php?action=wbsearchentities&search=" + \
              f"{entity_label}&language=ca&format=json"
        response = requests.get(url)
        if response.status_code != 200:
            raise Error()

        try:
            content = json.loads(response.text)
        except:
            # invalid entity
            self.linked_entities_cache[entity_label] = None
            return self.link_entity_ca(entity_label)

        search_results = content['search']
        if len(search_results) == 0:
            self.linked_entities_cache[entity_label] = None
            return self.link_entity_ca(entity_label)

        self.linked_entities_cache[entity_label] = search_results[0]['concepturi']
        return self.link_entity_ca(entity_label)

