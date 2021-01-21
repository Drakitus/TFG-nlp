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
from urllib.parse import urlparse

import nltk


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


# Falta afegir el diccionari quan funcioni correctament la llibreria
def spelling_corrector(corrector, keywords):
    corrected = []
    for k in keywords:
        ok = corrector.spell(k)  # check spelling
        if not ok:
            suggestions = corrector.suggest(k)
            if len(suggestions) > 0:  # hay suggestions
                # take best suggestion
                best_suggestions = suggestions[0]
                corrected.append(best_suggestions)
            else:
                corrected.append(k)  # no suggestion for the word
        else:
            corrected.append(k)  # corrected word
    return corrected


def hyponyms_a(clave):
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


# -------------- linkers --------------

def WikidataLinker(keyword, language):
    linker = WikidataEntityLinker()

    entity = linker.link_entity(keyword, language)

    return entity


def DBpediaLinker(keyword):
    linker = DBPediaEntityLinker()

    entity = linker.link_entities(keyword)

    return entity


# -------------- group words by root --------------
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


# -------------- Prepare the file to be processed --------------
def keywords_cleaner(f_in):
    # Get the data from the file
    df = pd.read_csv(f_in, delimiter=',')

    # Delete duplicates rows
    df.drop_duplicates(subset=None, keep="first", inplace=True)

    # Delete multiple keywords in one line separated by punctuation marks
    df_split = splitter(df)

    df_split.to_csv(f_in, index=False)

    df_dict = df_split.to_dict('records')
    keywords = [d.get('keyword') for d in df_dict]
    # Delete duplicates from keywords list
    kw_list = list(dict.fromkeys(keywords))

    # Deletes empty strings in case they exist
    kw_clean = list(filter(None, kw_list))

    return kw_clean


# -------------- Split multiple keywords in one row --------------
def splitter(df):
    df['keyword'] = df['keyword'].str.split('[;,/]|\. |- | -')
    df = df.explode('keyword')
    df['keyword'] = df['keyword'].str.strip()

    return df


# -------------- build d_keys information --------------
def process(clave):
    # Atributes for stadistics
    multi_cont = 0
    one_cont = 0
    none_cont = 0

    # print('Processing {}'.format(clave))
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


def stadistics_d_keys(dict_in):
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


# -------------- modify file replace-keywords-uri.csv --------------
def modify_file_keywords_to_uri(dict):
    file = "../files/file-keywords-split.csv"
    file2 = "../files/replace-keywors-uri.csv"
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
                if dict[key]['DBpedia'] is not None:
                    f_key = key.replace(key, dict[key]['DBpedia'])
                else:
                    if dict[key]['Wikidata'] is not None:
                        f_key = key.replace(key, dict[key]['Wikidata'])
                    else:
                        f_key = key
            else:
                csv_file_out.write('{},{}\n'.format(resourcer, key))
            csv_file_out.write('{},{}\n'.format(resourcer, f_key))


# -------------- buid comp_keys information --------------
def create_comp_dict(keyword, dict_out, dict_comp):
    db = dict_comp[keyword]['DBpedia']
    wd = dict_comp[keyword]['Wikidata']

    if db:
        dict_out[db] = [{'keyword': keyword, 'language': dict_comp[keyword]['lang']}]
        wrapper = DBpedia_wrapper(db)
        dict_out[db].extend(wrapper)
    else:
        dict_out[wd] = [{'keyword': keyword, 'language': dict_comp[keyword]['lang']}]
        wrapper = Wikidata_wrapper(wd)
        dict_out[wd].extend(wrapper)
        if wd is None:
            dict_out[keyword] = [{'keyword': keyword, 'language': dict_comp[keyword]['lang']}]

    # Clean repeated labels
    for key, value in dict_out.items():
        labels_list = []
        for item in value:
            if item not in labels_list:
                labels_list.append(item)
        dict_out[key] = labels_list

    return dict_out


def stadistics_comp_keys(dict_in, dict_comp):
    cont_uri = 0
    cont_no_uri = 0
    for k in dict_in.keys():
        if k not in dict_comp.keys():
            cont_uri += 1
        else:
            cont_no_uri += 1
    print("------ STADISTICS ------")
    print("Total of keywords processed:", len(dict_in))
    print("Contains uri as key:", cont_uri)
    print("Contains no uri as key:", cont_no_uri)


# -------------- create compacting_keys.csv --------------
def create_compacting_keys_structure(dict):
    # File with compacting structure
    salida = "../files/compacting_keys.csv"
    with open(salida, 'w') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(['uri', 'labels'])
        for key, value in dict.items():
            writer.writerow([key, value])


# ------------------------------------------
# -------------- MAIN PROGRAM --------------
# ------------------------------------------

if __name__ == '__main__':

    # entrada = "../files/samples_researchers_publications-keywords.csv"
    entrada = "../files/Researcher-06000001-keywords.csv"
    salida = "../files/file-keywords-split.csv"

    # Generate a new file with same data but this time without quote marks
    correct_keywords_file(entrada, salida)

    start = time.time()

    # Clean file and organize keywords to be processed
    kw_clean = keywords_cleaner(salida)

    # Dictionary keyword information structure
    d_key = {}
    for k in kw_clean:
        k_norm = normalize(k)
        d_key[k_norm] = {}

    pool = multiprocessing.Pool()
    try:
        result_async = [pool.apply_async(process, args=(keyword,)) for keyword in d_key.keys()]
        loop = tqdm(total=len(result_async), position=0, leave=False, colour='green')
        for o in result_async:
            loop.set_description("Calculando diccionario...".format(o))
            output = o.get()
            d_key[output['keyword']] = output['result']
            loop.update(1)

        print("--------------------------------------------")
        print("------ INFORMATION KEYWORDS STRUCTURE ------")
        print("--------------------------------------------")
        print(json.dumps(d_key, indent=1, ensure_ascii=False).encode('utf-8').decode())
        loop.close()
    finally:
        end = time.time()
        pool.close()

    # Stadistics of dictionary
    stadistics_d_keys(d_key)
    print('Elapsed: {}'.format(time.strftime("%Hh:%Mm:%Ss", time.gmtime(end - start))))

    # File modifier to resource/uri
    modify_file_keywords_to_uri(d_key)

    # --------------------- Compacting keyword dictionary ---------------------
    start2 = time.time()

    com_keys = {}
    loop = tqdm(total=len(kw_clean), position=0, leave=False, colour='green')

    for k in kw_clean:
        k_norm2 = normalize(k)
        loop.set_description("Construint el diccionari per compactar".format(k))

        # Create content of dictionary
        com_keys = create_comp_dict(k_norm2, com_keys, d_key)

        loop.update(1)
    loop.close()

    end2 = time.time()

    print("-------------------------------------------")
    print("------ COMPACTING KEYWORDS STRUCTURE ------")
    print("-------------------------------------------")
    print(json.dumps(com_keys, indent=1, ensure_ascii=False).encode('utf-8').decode())

    stadistics_comp_keys(com_keys, d_key)
    print('Elapsed: {}'.format(time.strftime("%Hh:%Mm:%Ss", time.gmtime(end2 - start2))))

    # Create file with keywords compacted
    create_compacting_keys_structure(com_keys)
