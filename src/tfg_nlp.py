import csv
import pandas as pd
import spacy
import pycld2 as cld2
import re
import multiprocessing

# import hunspell

from linking_entity_linking import *
from compacting_keys import *

from rake_nltk import Rake
from string import punctuation
from spacy.lang.en.stop_words import STOP_WORDS as ENGLISH_STOP_WORDS
from spacy.lang.es.stop_words import STOP_WORDS as SPANISH_STOP_WORDS
from spacy.lang.ca.stop_words import STOP_WORDS as CATALAN_STOP_WORDS
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from stop_words import get_stop_words  # will be used for catalan
from nltk.corpus import wordnet
from nltk.stem import SnowballStemmer
from collections import defaultdict
from tqdm import tqdm
from rdflib import Graph, RDF, RDFS, SKOS, URIRef, Literal
from rdflib.namespace import Namespace, NamespaceManager


# import nltk
# nltk.download('wordnet')
# from nltk.stem import WordNetLemmatizer


# -------------- Normalize keywords --------------
def normalize(clave):
    word = to_lower(clave)
    # Remove white spaces
    word = remove_white_spaces(word)
    # Remove multiple white spaces
    word = remove_multiple_white_spaces(word)

    word = utf8_format(word)
    # Correct words
    # word = spelling_corrector(None, word)

    return word


# Convert all words to lowercase
def to_lower(clave):
    return clave.lower()


# Remove white spaces
def remove_white_spaces(clave):
    return clave.strip()


def remove_multiple_white_spaces(clave):
    return re.sub("\s\s+", " ", clave)


def utf8_format(clave):
    if clave is not None:
        e = clave.encode('utf-8')
        d = e.decode('utf-8')
    else:
        d = clave
    return d


# Correct misspelled words (need to check the operation with the hunspell library)
def spelling_corrector(corrector, keywords):
    corrected = []
    for k in keywords:
        ok = corrector.spell(k)  # check spelling
        if not ok:
            suggestions = corrector.suggest(k)
            if len(suggestions) > 0:  # suggestions
                # take best suggestion
                best_suggestions = suggestions[0]
                corrected.append(best_suggestions)
            else:
                corrected.append(k)  # no suggestion for the word
        else:
            corrected.append(k)  # corrected word
    return corrected


# Check hyponyms of words to put them in a same group
def hyponyms(clave):
    word = wordnet.sysnet(clave)

    hyponym = word.hiponyms()
    return hyponym


# -------------- Language detector --------------
def language_keyword(keyword):
    r = {
        'en': Rake(stopwords=ENGLISH_STOP_WORDS, punctuations=punctuation),
        'es': Rake(stopwords=SPANISH_STOP_WORDS, punctuations=punctuation),
        'ca': Rake(stopwords=CATALAN_STOP_WORDS, punctuations=punctuation)
    }
    _, _, details = cld2.detect(keyword.encode('utf-8', 'replace'), isPlainText=True, bestEffort=True)
    lang = details[0][1]
    if not lang in r.keys():
        lang = 'en'  # Default language
    return lang


# -------------- Delete stop words --------------
def en_stopWords(keyword):
    text_tokens = word_tokenize(keyword)

    tokens_without_sw = [word for word in text_tokens if word not in stopwords.words('english')]

    return tokens_without_sw


def es_stopWords(keyword):
    text_tokens = word_tokenize(keyword)

    tokens_without_sw = [word for word in text_tokens if word not in stopwords.words('spanish')]

    return tokens_without_sw


def ca_stopWords(keyword):
    text_tokens = word_tokenize(keyword)

    tokens_without_sw = [word for word in text_tokens if word not in get_stop_words('ca')]

    return tokens_without_sw


# -------------- Word synonyms --------------
def synonyms(keyword):
    synonyms_list = []
    for syn in wordnet.synsets(keyword):
        for lemma in syn.lemmas():
            synonyms_list.append(lemma.name())
    # Delete repeated syn
    syn_unique = list(dict.fromkeys(synonyms_list))
    return syn_unique


# -------------- Root words (derivació regressiva) --------------
def en_stemmer(keyword):
    en_stem = SnowballStemmer('english')

    stemmer = en_stem.stem(keyword)
    return stemmer


def es_stemmer(keyword):
    es_stem = SnowballStemmer('spanish')

    stemmer = es_stem.stem(keyword)
    return stemmer


# -------------- spaCy lemmatizer --------------
def en_lemmatizer(keyword):
    nlp = spacy.load('en_core_web_sm', disable=["parser", "ner"])
    doc = nlp(keyword)

    w = " ".join([word.lemma_ for word in doc])
    return w


def es_lemmatizer(keyword):
    nlp = spacy.load('es_core_news_sm', disable=["parser", "ner"])
    doc = nlp(keyword)

    w = " ".join([word.lemma_ for word in doc])
    return w


def ca_lemmatizer(keyword):
    nlp = spacy.load('ca_fasttext_wiki_md', disable=["parser", "ner"])
    doc = nlp(keyword)

    w = " ".join([word.lemma_ for word in doc])
    return w


# -------------- Linkers --------------

def WikidataLinker(keyword, language):
    linker = WikidataEntityLinker()

    entity = linker.link_entity(keyword, language)

    return entity


def DBpediaLinker(keyword):
    linker = DBPediaEntityLinker()

    entity = linker.link_entities(keyword)

    return entity


# -------------- Group words by root --------------
def group(keyword, lang):
    kw_list = []
    kw_list.append(keyword)
    res = defaultdict(list)

    for k in kw_list:
        if lang == 'en':
            res[en_stemmer(k)].append(k)
        elif lang == 'es':
            res[en_stemmer(k)].append(k)
        else:
            res[ca_lemmatizer(k)].append(k)
    return res


# -------------- Prepare the file to be processed --------------
def correct_keywords_file(file_in, file_out):
    with open(file_in, "r", encoding='utf-8') as f_in, open(file_out, "w", encoding='utf-8') as f_out:
        for linea in f_in:
            trozos = linea.rstrip().split(",")  # Split elements by coma
            nombre = trozos[0]  # Get the first element
            palabra = ",".join(trozos[1:]).replace('"', '')  # Put the other elements together
            # Write into the other file but now the second element have quote marks
            f_out.write('{},"{}"\n'.format(nombre, palabra))


def keywords_cleaner(f_in):
    df_dict = clean_file(f_in)

    keywords = [d.get('keyword') for d in df_dict]
    # Delete duplicates from keywords list
    kw_list = list(dict.fromkeys(keywords))

    # Deletes empty strings in case they exist
    kw_clean = list(filter(None, kw_list))

    return kw_clean


def clean_file(f_in):
    # Get the data from the file
    df = pd.read_csv(f_in, delimiter=',')

    # Delete duplicates rows
    df.drop_duplicates(subset=None, keep="first", inplace=True)

    # Delete multiple keywords in one line separated by punctuation marks
    df_split = splitter(df)

    # Delete words with less than 3 words
    df_split = df_split[df_split['keyword'].str.len() > 4]
    df_split.reset_index(drop=True)

    df_split.to_csv(f_in, index=False)

    df_dict = df_split.to_dict('records')

    return df_dict


def splitter(df):
    # Split multiple keywords in one row

    # Delete words in parentheses
    df['keyword'] = df['keyword'].str.replace(r"\s*\([^()]*\)", "").str.strip()
    df['keyword'] = df['keyword'].str.partition('(')
    # Delete words between brakets
    df['keyword'] = df['keyword'].str.replace(r"(\s*\[.*?\]\s*)", "").str.strip()

    # Split by punctuation marks
    df['keyword'] = df['keyword'].str.split('[;,/]|\. |- | -')
    df = df.explode('keyword')
    df['keyword'] = df['keyword'].str.strip()

    # Deletes empty values in dataframe
    nan_value = float("NaN")
    df.replace("", nan_value, inplace=True)
    df.dropna(subset=['keyword'], inplace=True)
    df.reset_index(drop=True)

    return df


# -------------- Build d_keys information --------------
def process(clave):
    print('Processing {}'.format(clave))
    result = {'lang': language_keyword(clave)}
    output = {'keyword': clave, 'result': result}

    # result['Group'] = group(clave, result['lang'])

    if result['lang'] == 'en':
        # result['stop-word'] = en_stopWords(clave)
        # result['synonym'] = synonyms(clave)
        # result['stemmer'] = en_stemmer(clave)
        result['lemmatizer'] = en_lemmatizer(clave)
        result['Wikidata'] = WikidataLinker(result['lemmatizer'], result['lang'])
        if result['Wikidata'] is None:
            result['Wikidata'] = WikidataLinker(clave, result['lang'])

        result['DBpedia'] = DBpediaLinker(result['lemmatizer'])
        if result['DBpedia'] is None:
            result['DBpedia'] = DBpediaLinker(clave)

    elif result['lang'] == 'es':
        # result['stop-word'] = es_stopWords(clave)
        # result['synonym'] = synonyms(clave)
        # result['stemmer'] = es_stemmer(clave)
        result['lemmatizer'] = es_lemmatizer(clave)
        result['Wikidata'] = WikidataLinker(result['lemmatizer'], result['lang'])
        if result['Wikidata'] is None:
            result['Wikidata'] = WikidataLinker(clave, result['lang'])

        result['DBpedia'] = DBpediaLinker(result['lemmatizer'])
        if result['DBpedia'] is None:
            result['DBpedia'] = DBpediaLinker(clave)

    elif result['lang'] == 'ca':
        # result['stop-word'] = ca_stopWords(clave)
        # result['synonym'] = synonyms(clave)
        result['lemmatizer'] = ca_lemmatizer(clave)
        result['Wikidata'] = WikidataLinker(result['lemmatizer'], result['lang'])
        if result['Wikidata'] is None:
            result['Wikidata'] = WikidataLinker(clave, result['lang'])

        result['DBpedia'] = DBpediaLinker(result['lemmatizer'])
        if result['DBpedia'] is None:
            result['DBpedia'] = DBpediaLinker(clave)

    return output


def statistics_d_keys(dict_in):
    multi_cont = 0
    one_cont = 0
    none_cont = 0
    for k in dict_in.keys():
        if dict_in[k]['Wikidata'] and dict_in[k]['DBpedia']:
            multi_cont += 1
        elif dict_in[k]['Wikidata'] or dict_in[k]['DBpedia']:
            one_cont += 1
        else:
            none_cont += 1

    print("------ STADISTICS ------")
    print("Total of keywords processed:", len(dict_in))
    print("Contains two uris:", multi_cont)
    print("Contains one uri:", one_cont)
    print("Contains zero uri:", none_cont)


# -------------- Modify file replace-keywords-uri.csv --------------
def modify_file_keywords_to_uri(dict):
    file = "../files/file-keywords-split.csv"
    file2 = "../files/replace-keywords-uri.csv"
    with open(file, "r") as csv_file, open(file2, "w", encoding='utf-8') as csv_file_out:
        headers = next(csv_file, None)  # Write header
        if headers:
            csv_file_out.write(headers)
        for lane in csv_file:
            part = lane.rstrip().split(",")  # Split elements by coma
            resourcer = part[0]
            key = normalize(part[1])  # Get the first element

            # Replace keywords for uris
            if key in dict.keys():
                if dict[key]['Wikidata'] is not None:
                    f_key = key.replace(key, dict[key]['Wikidata'])
                    csv_file_out.write('{},{}\n'.format(resourcer, f_key))
                else:
                    if dict[key]['DBpedia'] is not None:
                        f_key = key.replace(key, dict[key]['DBpedia'])

                        # Check uri with coma to be read correctly by file
                        if "," in f_key:
                            f_key_q = '"' + f_key + '"'
                            csv_file_out.write('{},{}\n'.format(resourcer, f_key_q))
                        else:
                            csv_file_out.write('{},{}\n'.format(resourcer, f_key))

            else:
                csv_file_out.write('{},{}\n'.format(resourcer, key))


# -------------- Buid comp_keys information --------------
def create_comp_dict(keyword, dict_out, dict_comp):
    db = dict_comp[keyword]['DBpedia']
    wd = dict_comp[keyword]['Wikidata']

    if wd:
        dict_out[wd] = [{'keyword': keyword, 'language': dict_comp[keyword]['lang']}]
        wrapper = Wikidata_wrapper(wd)
        dict_out[wd].extend(wrapper)
    else:
        dict_out[db] = [{'keyword': keyword, 'language': dict_comp[keyword]['lang']}]
        wrapper = DBpedia_wrapper(db)
        dict_out[db].extend(wrapper)
        if db is None:
            dict_out.pop(keyword, None)

    # Delete None keys
    for k in list(dict_out):
        if k is None:
            dict_out.pop(k)

    # Clean repeated labels
    clean_repeated_labels(dict_out)

    return dict_out


def clean_repeated_labels(dict_out):
    for key, value in list(dict_out.items()):
        labels_list = []
        for item in value:
            if item not in labels_list:
                labels_list.append(item)
        dict_out[key] = labels_list

        # Delete words with just one label
        if len(dict_out[key]) == 1:
            dict_out.pop(key, None)

    return dict_out


def statistics_comp_keys(dict_in):
    cont_two = 0
    cont_three = 0
    cont_more = 0
    for values in dict_in.values():
        for ind in range(0, len(values)):
            x = ind + 1
        if x == 2:
            cont_two += 1
        elif x == 3:
            cont_three += 1
        elif x > 3:
            cont_more += 1

    print("------ STADISTICS ------")
    print("Total of keywords processed:", len(dict_in))
    print("Contains two languages:", cont_two)
    print("Contains three languages:", cont_three)
    print("Contains more than three languages:", cont_more)


# -------------- Create compacting_keys file --------------
def create_compacting_keys_structure(dict):
    # File with compacting structure
    salida = "../files/compacting_keys.csv"
    with open(salida, 'w') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(['uri', 'labels'])
        for key, value in dict.items():
            writer.writerow([key, value])


def compare_resource_keywords_uri(file1, dict):
    # Convert the file into dataframe to make changes and skiped uris cant be read by csv
    df_file = pd.read_csv(file1, delimiter=',')

    # Check if file contains the same uris as final dictionary
    for u in df_file['keyword']:
        if u not in dict.keys():
            badwords = df_file[df_file['keyword'] == u].index
            df_file.drop(badwords, inplace=True)

    df_file.drop_duplicates(subset=None, keep="first", inplace=True)
    df_file.reset_index(drop=True)
    df_file.to_csv(file1, index=False)


# -------------- Data serialization --------------
def serialization(dict1, dict2):
    rdf = Graph()
    namespace_manager = NamespaceManager(rdf)
    namespace_manager.bind("skos", SKOS)
    VIVO = Namespace("http://vivoweb.org/ontology/core#")
    namespace_manager.bind("core", VIVO)

    # Delete double quotes in comp_keys keys
    for k in list(dict2):
        if '"' in k:
            k_clean = k.replace('"', "")
            dict2[k_clean] = dict2[k]
            del dict2[k]

    # Build semantic triple of concepts
    for uri in dict2:
        concept = URIRef(uri)
        rdf.add((concept, RDF.type, SKOS.Concept))
        for keyword in dict2[uri]:
            rdf.add((concept, RDFS.label, Literal(keyword["keyword"], lang=keyword["language"])))

    # Build semantic triple of researcher
    for researcher in dict1:
        rdf.add((URIRef(researcher["researcher"]), VIVO.hasResearchArea, URIRef(researcher["term"])))

    print(rdf.serialize(format="turtle", encoding="UTF-8").decode("utf-8"))

    # Serialize to a file
    rdf.serialize(destination="../files/researchers_areas.ttl", format="turtle")


# ------------------------------------------
# -------------- MAIN PROGRAM --------------
# ------------------------------------------

if __name__ == '__main__':

    entrada = "../files/samples_researchers_publications-keywords.csv"
    #entrada = "../files/Researcher-06000001-keywords.csv"
    salida = "../files/file-keywords-split.csv"

    # Generate a new file with same data but this time without quote marks
    correct_keywords_file(entrada, salida)

    start = time.time()

    # Clean file and organize keywords to be processed
    kw_cleaned = keywords_cleaner(salida)

    # --------------------- Dictionary keyword information structure ---------------------
    d_key = {}
    for k in kw_cleaned:
        k_norm = normalize(k)
        d_key[k_norm] = {}

    pool = multiprocessing.Pool()
    try:
        result_async = [pool.apply_async(process, args=(keyword,)) for keyword in d_key.keys()]
        for o in result_async:
            output = o.get()
            d_key[output['keyword']] = output['result']

        print("--------------------------------------------")
        print("------ INFORMATION KEYWORDS STRUCTURE ------")
        print("--------------------------------------------")
        print(json.dumps(d_key, indent=1, ensure_ascii=False).encode('utf-8').decode())
    finally:
        end = time.time()
        pool.close()

    # Statistics of dictionary
    statistics_d_keys(d_key)

    print('Elapsed: {}'.format(time.strftime("%Hh:%Mm:%Ss", time.gmtime(end - start))))

    # File modifier to resource/uri
    modify_file_keywords_to_uri(d_key)

    # --------------------- Compacting keyword dictionary ---------------------
    start2 = time.time()

    com_keys = {}
    loop = tqdm(total=len(d_key.keys()), position=0, leave=False, colour='green')

    for k in d_key.keys():
        k_norm2 = normalize(k)
        loop.set_description("Building compacting keys dictionary".format(k))

        # Create content of dictionary
        com_keys = create_comp_dict(k_norm2, com_keys, d_key)

        loop.update(1)
    loop.close()

    end2 = time.time()

    print("-------------------------------------------")
    print("------ COMPACTING KEYWORDS STRUCTURE ------")
    print("-------------------------------------------")
    print(json.dumps(com_keys, indent=1, ensure_ascii=False).encode('utf-8').decode())

    # Statistics
    statistics_comp_keys(com_keys)

    print('Elapsed: {}'.format(time.strftime("%Hh:%Mm:%Ss", time.gmtime(end2 - start2))))

    # Upadate replace-keywords-uri to restrictions of comp_keys
    file1 = "../files/replace-keywords-uri.csv"
    compare_resource_keywords_uri(file1, com_keys)

    # Create file with keywords compacted
    create_compacting_keys_structure(com_keys)

    # --------------------- SKOS serialization ---------------------
    researcher_terms = []
    # Create new dictionary with file content of replace-keywords-uri.csv
    with open('../files/replace-keywords-uri.csv', mode='r') as file_in:
        reader = csv.reader(file_in, quoting=csv.QUOTE_ALL)
        next(reader)  # Ignore first lane
        for lane in reader:
            researcher = lane[0]
            term = lane[1]

            # Delete quotes of words of file to serialize
            if '"' in term:
                term_clean = term.replace('"', "")
                researcher_terms.append({'researcher': researcher, 'term': term_clean})
            else:
                researcher_terms.append({'researcher': researcher, 'term': term})

    # Serialize results of dictionaries created with final results
    serialization(researcher_terms, com_keys)
