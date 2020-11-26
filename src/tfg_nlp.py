import pandas as pd
import spacy
import pycld2 as cld2
import re
import en_core_web_sm
import en_core_web_sm
import ca_fasttext_wiki_md

from linking_entity_linking import *

from rake_nltk import Rake
from string import punctuation
from spacy.lang.en.stop_words import STOP_WORDS as ENGLISH_STOP_WORDS
from spacy.lang.es.stop_words import STOP_WORDS as SPANISH_STOP_WORDS
from spacy.lang.ca.stop_words import STOP_WORDS as CATALAN_STOP_WORDS
from nltk.corpus import stopwords
from stop_words import get_stop_words  # will be used for catalan
from nltk.corpus import wordnet
from nltk.stem import SnowballStemmer


# from nltk.stem import WordNetLemmatizer


# -------------- Normalize keywords --------------
def normalize(clave):
    # Convert all words to lowercase
    l = clave.lower()
    # Remove white spaces
    s = l.strip()
    # Remove utf-8 words
    # e = s.encode("utf-8")

    return s


# -------------- Split multiple keywords with punctuation signs --------------
def splitter(kw_list):
    regex = '; | - | / '

    kw_clean = []
    for word in kw_list:
        kw_clean.extend(re.split(regex, word))

    return kw_clean


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


# -------------- Check if words are stop words -------------- 
def en_stopWords(keyword):
    if keyword in stopwords.words('english'):
        print('True')
    else:
        print('False')


def es_stopWords(keyword):
    if keyword in stopwords.words('spanish'):
        return True


def ca_stopWords(keyword):
    stop_words = get_stop_words('ca')
    if keyword in stop_words:
        return True


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
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    doc = nlp(keyword)

    w = " ".join([word.lemma_ for word in doc])
    return w


def es_lemmatizer(keyword):
    nlp = spacy.load('es_core_news_sm', disable=["parser", "ner"])
    doc = nlp(keyword)

    w = " ".join([word.lemma_ for word in doc])
    return w


def ca_lemmatizer(keyword):
    nlp = spacy.load('ca', disable=["parser", "ner"])
    doc = nlp(keyword)

    w = " ".join([word.lemma_ for word in doc])
    return w


# -------------- linkers --------------

def en_WikidataLinker(keyword):
    linker = WikidataEntityLinker()

    entity = linker.link_entity_en(keyword)

    return entity


def es_WikidataLinker(keyword):
    linker = WikidataEntityLinker()

    entity = linker.link_entity_en(keyword)

    return entity


def ca_WikidataLinker(keyword):
    linker = WikidataEntityLinker()

    entity = linker.link_entity_ca(keyword)

    return entity


def DBpediaLinker(keyword):
    linker = DBPediaEntityLinker()

    entity = linker.link_entities(keyword)

    return entity


# ------------------------------------------
# -------------- MAIN PROGRAM --------------
# ------------------------------------------

# Generate a new file with same data but this time without quote marks
entrada = "../files/samples_researchers_publications-keywords.csv"
salida = "../files/fichero_bien.csv"

with open(entrada, "r") as f_in, open(salida, "w") as f_out:
    for linea in f_in:
        trozos = linea.rstrip().split(",")  # Split elements by coma
        nombre = trozos[0]  # Get the first element
        palabra = ",".join(trozos[1:]).replace('"', '')  # Put the other elements together
        # Write into the other file but now the second element have question marks
        f_out.write('{},"{}"\n'.format(nombre, palabra))

# Get the data from the file
df = pd.read_csv('../files/fichero_bien.csv', delimiter=',')

# Delete duplicates rows
df.drop_duplicates(subset=None, keep="first", inplace=True)

# -------------- used to delete multiple keywords in one line --------------
# Convert column keyword into lists
df.keyword = df.keyword.str.split(",")
# Convert lists to columns duplicating the resourcer but with only one keyword which had more than one ','
df = df.explode("keyword")

df_dict = df.to_dict('records')
keywords = [d.get('keyword') for d in df_dict]
# Delete duplicates from keywords list
kw_list = list(dict.fromkeys(keywords))

# Deletes all punctuation marks and create new columns with the resource and the keyword
kw_clean = splitter(kw_list)

# Deletes empty strings in case they exist
kw_clean = list(filter(None, kw_clean))

# Dictionary structure
d_key = {}
for k in kw_clean:
    k_norm = normalize(k)
    d_key[k_norm] = {}

# Dictionary data
for clave in d_key.keys():

    d_key[clave]['lang'] = language_keyword(clave)

    if d_key[clave]['lang'] == 'en':
        # d_key[clave]['stop-word'] = en_stopWords(clave)
        d_key[clave]['synonym'] = synonyms(clave)
        d_key[clave]['stemmer'] = en_stemmer(clave)
        d_key[clave]['lemmatizer'] = en_lemmatizer(clave)
        d_key[clave]['Wikidata'] = en_WikidataLinker(clave)
        # d_key[clave]['DBpedia'] = DBpediaLinker(clave)

    elif d_key[clave]['lang'] == 'es':
        # d_key[clave]['stop-word'] = es_stopWords(clave)
        d_key[clave]['synonym'] = synonyms(clave)
        d_key[clave]['stemmer'] = es_stemmer(clave)
        d_key[clave]['lemmatizer'] = es_lemmatizer(clave)
        d_key[clave]['Wikidata'] = es_WikidataLinker(clave)

    elif d_key[clave]['lang'] == 'ca':
        # d_key[clave]['stop-word'] = ca_stopWords(clave)
        d_key[clave]['synonym'] = synonyms(clave)
        # d_key[clave]['stemmer'] = ca_stemmer(clave)
        d_key[clave]['lemmatizer'] = ca_lemmatizer(clave)
        d_key[clave]['Wikidata'] = ca_WikidataLinker(clave)


print(d_key)
