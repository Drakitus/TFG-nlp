from SPARQLWrapper import SPARQLWrapper, JSON


def Wikidata_wrapper(keyword):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery("""
        SELECT DISTINCT ?lang ?name WHERE {
        ?article schema:about wd:Q1952416 ;
                   schema:inLanguage ?lang ;
                   schema:name ?name;
                   schema:isPartOf [ wikibase:wikiGroup "wikipedia" ] .
        FILTER(?lang in ('en', 'uz', 'ru', 'ko')).
        FILTER(!CONTAINS(?name, ':')) .
    }""")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        return result["name"]["value"]


def DBpedia_wrapper(keyword):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery("""
              PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
              SELECT ?label
              WHERE { <http://dbpedia.org/resource/{keyword}> rdfs:label ?label }
    """)
    print('\n\n*** JSON Example')
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        return result["label"]["value"]

