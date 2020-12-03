import pandas as pd
import spacy
import pycld2 as cld2
import re
import multiprocessing

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
import nltk


# nltk.download('wordnet')

# from nltk.stem import WordNetLemmatizer


# -------------- Normalize keywords --------------
def normalize(clave):
    word = to_lower(clave)
    # Remove white spaces
    word = remove_white_spaces(word)

    return word


# Convert all words to lowercase
def to_lower(clave):
    return clave.lower()


# Remove white spaces
def remove_white_spaces(clave):
    return clave.strip()


def remove_multiple_white_spaces(clave):
    return re.sub("\s\s+", " ", clave)


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


# -------------- group words by root --------------

def group(keyword, lang):
    kw_list = [keyword]
    group = ''

    for k in range(0, len(kw_list)):
        if lang == 'en':
            if k == 0:
                group = en_stemmer(kw_list[k])
            elif en_stemmer(kw_list[k]) == en_stemmer(kw_list[k - 1]):
                group = kw_list[k - 1]
            else:
                group = en_stemmer(kw_list[k])
        elif lang == 'es':
            if k == 0:
                group = en_stemmer(kw_list[k])
            elif es_stemmer(kw_list[k]) == es_stemmer(kw_list[k - 1]):
                group = kw_list[k - 1]
            else:
                group = en_stemmer(kw_list[k])
        else:
            if k == 0:
                group = ca_lemmatizer(kw_list[k])
            elif ca_lemmatizer(kw_list[k]) == ca_lemmatizer(kw_list[k - 1]):
                group = kw_list[k - 1]
            else:
                group = ca_lemmatizer(kw_list[k])

    return group


def process(clave):
    print('Processing {}'.format(clave))
    result = {'lang': language_keyword(clave)}
    output = {'keyword': clave, 'result': result}

    result['Group'] = group(clave, result['lang'])

    if result['lang'] == 'en':
        # result['stop-word'] = en_stopWords(clave)
        result['synonym'] = synonyms(clave)
        result['stemmer'] = en_stemmer(clave)
        result['lemmatizer'] = en_lemmatizer(clave)
        result['Wikidata'] = en_WikidataLinker(clave)
        result['DBpedia'] = DBpediaLinker(clave)

    elif result['lang'] == 'es':
        # result['stop-word'] = es_stopWords(clave)
        result['synonym'] = synonyms(clave)
        result['stemmer'] = es_stemmer(clave)
        result['lemmatizer'] = es_lemmatizer(clave)
        result['Wikidata'] = es_WikidataLinker(clave)
        result['DBpedia'] = DBpediaLinker(clave)

    elif result['lang'] == 'ca':
        # result['stop-word'] = ca_stopWords(clave)
        result['synonym'] = synonyms(clave)
        # result['stemmer'] = ca_stemmer(clave)
        result['lemmatizer'] = ca_lemmatizer(clave)
        result['Wikidata'] = ca_WikidataLinker(clave)
        result['DBpedia'] = DBpediaLinker(clave)

    return output


# ------------------------------------------
# -------------- MAIN PROGRAM --------------
# ------------------------------------------


if __name__ == '__main__':

    # Generate a new file with same data but this time without quote marks
    #entrada = "../files/samples_researchers_publications-keywords.csv"
    entrada = "../files/Researcher-06000001-keywords.csv"
    salida = "../files/fichero_bien.csv"

    with open(entrada, "r", encoding='utf-8') as f_in, open(salida, "w") as f_out:
        for linea in f_in:
            trozos = linea.rstrip().split(",")  # Split elements by coma
            nombre = trozos[0]  # Get the first element
            palabra = ",".join(trozos[1:]).replace('"', '')  # Put the other elements together
            # Write into the other file but now the second element have question marks
            f_out.write('{},"{}"\n'.format(nombre, palabra))

    # Get the data from the file
    df = pd.read_csv('../files/fichero_bien.csv', delimiter=',')

    start = time.time()

    # Delete duplicates rows
    df.drop_duplicates(subset=None, keep="first", inplace=True)

    # -------------- used to delete multiple keywords in one line --------------
    # Convert column keyword into lists
    df.keyword = df.keyword.str.split(",")
    # Convert lists to columns duplicating the resource but with only one keyword which had more than one ','
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

    pool = multiprocessing.Pool()
    try:
        result_async = [pool.apply_async(process, args=(keyword,)) for keyword in d_key.keys()]
        for o in result_async:
            output = o.get()
            d_key[output['keyword']] = output['result']
        print(json.dumps(d_key, indent=1))
    finally:
        end = time.time()
        print('Elapsed: {}'.format(time.strftime("%Hh:%Mm:%Ss", time.gmtime(end - start))))
        pool.close()
