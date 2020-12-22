import sys
import traceback
import pprint

from SPARQLWrapper import SPARQLWrapper, JSON
from tfg_nlp import *


def Wikidata_wrapper(url):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '\
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

        for result in results["results"]["bindings"]:
            return result["name"]["value"]
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise e


def DBpedia_wrapper(url):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
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
    x = []
    for result in results["results"]["bindings"]:
        x.append(utf8_format(result["label"]["value"]))
    return x


if __name__ == '__main__':

    file = "../files/fichero_bien.csv"
    kw_clean = keywords_cleaner(file)

    # Compacting keys structure
    comp_keys = {}
    for k in kw_clean:
        k_norm = normalize(k)
        db = DBpediaLinker(k_norm)
        if db:
            wrapper = DBpedia_wrapper(db)
        if db is None:
            db = Wikidata_lang(k_norm)
            if db:
                wrapper = Wikidata_wrapper(db)
        comp_keys[db] = {}
        comp_keys[db]['keyword'] = k_norm
        comp_keys[db]['entities'] = wrapper
    pprint.pprint(comp_keys, width=120)
