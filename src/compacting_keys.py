import sys
import traceback

from SPARQLWrapper import SPARQLWrapper, JSON
from tfg_nlp import normalize


def utf8_format(clave):
    if clave is not None:
        e = clave.encode('utf-8')
        d = e.decode('utf-8')
    else:
        d = clave
    return d


def Wikidata_wrapper(url):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/50.0.2661.102 Safari/537.36'
    try:
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
        sparql.setQuery("""
            SELECT DISTINCT ?lang ?name 
            WHERE {{
            ?article schema:about <{url}> ;
                       schema:inLanguage ?lang ;
                       schema:name ?name.
            FILTER(?lang in ('en', 'es', 'ca')).
            FILTER(!CONTAINS(?name, ':')) .
        }}""".format(url=url))
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

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
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/50.0.2661.102 Safari/537.36'

    sparql = SPARQLWrapper("http://dbpedia.org/sparql", agent=user_agent)
    sparql.setQuery("""
              PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
              SELECT ?label
              WHERE {{ 
              <{url}> rdfs:label ?label 
               FILTER(lang(?label) in ('en', 'es', 'ca')).
                
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
