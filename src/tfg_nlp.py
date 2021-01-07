import csv
import pandas as pd
import spacy
import pycld2 as cld2
import re
import multiprocessing
# import hunspell

from linking_entity_linking import *
# from compacting_keys import *

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


def Wikidata_lang(keyword):
    lang = language_keyword(keyword)

    return WikidataLinker(keyword, lang)


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
        result['DBpedia'] = DBpediaLinker(result['lemmatizer'])

    elif result['lang'] == 'es':
        # result['stop-word'] = es_stopWords(clave)
        # result['synonym'] = synonyms(clave)
        # result['stemmer'] = es_stemmer(clave)
        result['lemmatizer'] = es_lemmatizer(clave)
        result['Wikidata'] = WikidataLinker(result['lemmatizer'], result['lang'])
        result['DBpedia'] = DBpediaLinker(result['lemmatizer'])

    elif result['lang'] == 'ca':
        # result['stop-word'] = ca_stopWords(clave)
        # result['synonym'] = synonyms(clave)
        result['lemmatizer'] = ca_lemmatizer(clave)
        result['Wikidata'] = WikidataLinker(result['lemmatizer'], result['lang'])
        result['DBpedia'] = DBpediaLinker(result['lemmatizer'])

    return output


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
    # Convert column keyword into lists
    df.keyword = df.keyword.str.split(",")
    # Convert lists to columns duplicating the resource but with only one keyword which had more than one ','
    df = df.explode("keyword")

    df.keyword = df.keyword.str.split("- ")
    df = df.explode("keyword")

    df.keyword = df.keyword.str.split("\. ")  # Need the \ to specify the . if not it will accept any character
    df = df.explode("keyword")

    regex = "; | /"
    df.keyword = df.keyword.str.split(regex)
    df = df.explode("keyword")

    return df


# ------------------------------------------
# -------------- MAIN PROGRAM --------------
# ------------------------------------------


if __name__ == '__main__':

    # Generate a new file with same data but this time without quote marks
    # entrada = "../files/samples_researchers_publications-keywords.csv"
    entrada = "../files/Researcher-06000001-keywords.csv"
    salida = "../files/fichero_bien.csv"

    with open(entrada, "r", encoding='utf-8') as f_in, open(salida, "w", encoding='utf-8') as f_out:
        for linea in f_in:
            trozos = linea.rstrip().split(",")  # Split elements by coma
            nombre = trozos[0]  # Get the first element
            palabra = ",".join(trozos[1:]).replace('"', '')  # Put the other elements together
            # Write into the other file but now the second element have quote marks
            f_out.write('{},"{}"\n'.format(nombre, palabra))

    start = time.time()

    # Clean file and organize keywords to be processed
    kw_clean = keywords_cleaner(salida)

    # Dictionary structure
    d_key = {}
    for k in kw_clean:
        k_norm = normalize(k)
        d_key[k_norm] = {}

    pool = multiprocessing.Pool()
    try:
        result_async = [pool.apply_async(process, args=(keyword,)) for keyword in d_key.keys()]
        for o in result_async:
            output = o.get()
            d_key[output['keyword']] = output['result']
        print(json.dumps(d_key, indent=1, ensure_ascii=False).encode('utf-8').decode())
    finally:
        end = time.time()
        print('Elapsed: {}'.format(time.strftime("%Hh:%Mm:%Ss", time.gmtime(end - start))))
        pool.close()

    # File modifier
    file = "../files/fichero_bien.csv"
    file2= "../files/fichero_bien2.csv"
    with open(file, "r") as csv_file, open(file2, "w", encoding='utf-8') as csv_file_out:
        headers = next(csv_file, None)  # Write header
        if headers:
            csv_file_out.write(headers)
        for lane in csv_file:
            part = lane.rstrip().split(",")  # Split elements by coma
            resourcer = part[0]
            key = part[1]  # Get the first element

            if key in d_key.keys():
                if d_key[key]['DBpedia'] is not None:
                    f_key = key.replace(key, d_key[key]['DBpedia'])
                else:
                    if d_key[key]['Wikidata'] is not None:
                        f_key = key.replace(key, d_key[key]['Wikidata'])
                    else:
                        f_key = key
            csv_file_out.write('{},{}\n'.format(resourcer, f_key))
