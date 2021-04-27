import sys
import time
import traceback

from SPARQLWrapper import SPARQLWrapper, JSON
from tfg_nlp import normalize
from requests import HTTPError, Timeout


def wait_retry_after(response):
    if 'retry-after' in response.info().keys():
        print('Continuing after {}...'.format(response.info()['retry-after']))
        time.sleep(response.info()['retry-after'])


def Wikidata_wrapper(url):
    user_agent = 'Wikidata (marcmasipc@hotmail.com) SPARQLWrapper/1.8.5'
    try:
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
        sparql.setQuery(
            """SELECT DISTINCT (LANG(?name) AS ?lang) ?name (BOUND(?type) AS ?isArticle)
            WHERE {{
              BIND(<{url}>AS ?uri)
              ?uri rdfs:label ?name .
              FILTER(LANG(?name) IN ('en', 'es', 'ca'))
              OPTIONAL {{
                ?uri wdt:P31 ?type .
                ?type wdt:P279* wd:Q732577 . # publication
              }}
            }}""".format(url=url))
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(20)

        response = sparql.query()
        wait_retry_after(response)
        results = response.convert()

        ent_list = []
        for result in results["results"]["bindings"]:
            keywords = normalize(result["name"]["value"])
            if result["isArticle"]["value"] == "false":
                dict = {'keyword': keywords, 'language': result["lang"]["value"]}
                ent_list.append(dict)
        return ent_list

    except (HTTPError, ConnectionResetError, Timeout) as e:
        traceback.print_exc(file=sys.stdout)
        raise e

    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
        raise ex


def DBpedia_wrapper(url):
    user_agent = 'DBpediaExtractor (marcmasipc@hotmail.com) SPARQLWrapper/1.8.5'
    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql", agent=user_agent)
        sparql.setQuery("""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT (LANG(?name) AS ?lang) ?name (BOUND(?type) AS ?isArticle)
            WHERE {{
                BIND(<{url}>AS ?uri)
                ?uri rdfs:label ?name .
                FILTER(LANG(?name) IN ('en', 'es', 'ca'))
                OPTIONAL {{
                    ?uri rdfs:Resource ?type .
                    ?type rdfs:subClassOf <https://dbpedia.org/ontology/publication> . # publication
                }}
            }}          
        """.format(url=url))
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(20)

        response = sparql.query()
        wait_retry_after(response)
        results = response.convert()

        ent_list = []
        for result in results["results"]["bindings"]:
            keywords = normalize(result["name"]["value"])
            if result["isArticle"]["value"] == "0":
                dict = {'keyword': keywords, 'language': result["lang"]["value"]}
                ent_list.append(dict)
        return ent_list

    except (HTTPError, ConnectionError, Timeout) as e:
        traceback.print_exc(file=sys.stdout)
        raise e
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
        raise ex
