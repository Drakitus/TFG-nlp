import sys
import time
import traceback

from SPARQLWrapper import SPARQLWrapper, JSON
from tfg_nlp import normalize


def wait_retry_after(response):
    if 'retry-after' in response.info().keys():
        print('Continuing after {}...'.format(response.info()['retry-after']))
        time.sleep(response.info()['retry-after'])


def Wikidata_wrapper(url):
    user_agent = 'Wikidata (marcmasipc@hotmail.com) SPARQLWrapper/1.8.5'
    try:
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
        sparql.setQuery("""
            SELECT DISTINCT ?lang ?name 
            WHERE {{
            ?article schema:about <{url}> ;
                       schema:inLanguage ?lang ;
                       schema:name ?name.
            FILTER(?lang in ('en', 'es', 'ca'))
            FILTER(!CONTAINS(?name, ':'))
        }}""".format(url=url))
        sparql.setReturnFormat(JSON)

        response = sparql.query()
        wait_retry_after(response)
        results = response.convert()

        ent_list = []
        for result in results["results"]["bindings"]:
            keywords = normalize(result["name"]["value"])
            dict = {'keyword': keywords, 'language': result["lang"]["value"]}
            ent_list.append(dict)
        return ent_list

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise e


def DBpedia_wrapper(url):
    user_agent = 'DBpediaExtractor (marcmasipc@hotmail.com) SPARQLWrapper/1.8.5'
    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql", agent=user_agent)
        sparql.setQuery("""
                  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                  SELECT ?label
                  WHERE {{ 
                  <{url}> rdfs:label ?label 
                   FILTER(lang(?label) in ('en', 'es', 'ca'))
                    
                  }}           
        """.format(url=url))
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        ent_list = []
        for result in results["results"]["bindings"]:
            kewords = normalize(result["label"]["value"])
            dict = {'keyword': kewords, 'language': result["label"]["xml:lang"]}
            ent_list.append(dict)
        return ent_list

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise e
