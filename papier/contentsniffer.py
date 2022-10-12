#!/usr/bin/env python3
import sys
import os
import sqlite3
import re
import subprocess
import dateparser
import dateparser.search
from dateparser_data.settings import default_parsers
import datetime
import pandas as pd
import spacy
import spacy_fastlang
import pytextrank
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


def predict_date(doc, lang=None, ref=None):
    """
    returns the nth date in the document
    """
    import warnings
    warnings.filterwarnings("ignore", module="dateparser")

    if ref is None:
        ref = datetime.datetime.now()

    settings = {}
    settings['REQUIRE_PARTS'] = ['year', 'month']
    settings['PREFER_DAY_OF_MONTH'] = 'first'
    settings['PARSERS'] = [p for p in default_parsers if p != 'relative-time']

    languages = None
    if lang is not None:
        languages = [lang]

    try:
        candidates = [(text, date) for (text, date) in
                dateparser.search.search_dates(doc, languages=languages, settings=settings) if
                date <= ref]
    except TypeError:
        candidates = []

    if len(candidates) > 0:
        return candidates[0][1].strftime("%Y-%m-%d")
    else:
        return "XXXX-XX-XX"


def extract_features(path):
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    components = basename.split(".")
    extension = components[-1]
    base = ".".join(components[:-1])

    fields = base.split(" - ")
    author = fields[0]
    date = fields[1]
    subject = fields[2]
    return (author, date, subject)


def index(path, con):
    """
    Inserts documents in the DB
    """
    if os.path.isdir(path):
        for name in os.listdir(path):
            index(os.path.join(path, name), con)

    if os.path.isfile(path):
        if indexable(path):
            last_modified = os.path.getmtime(path)
            if previous_mtime(path, con) != last_modified:
                print(f"+ {path}")
                content = extract_content(path)
                author, date, subject = extract_features(path)
                with con as cur:
                    res = cur.execute(
                            "REPLACE INTO files VALUES (?, ?, ?, ?, ?, ?)",
                            (path, last_modified, content, author, date, subject)
                        )




def previous_mtime(path, con):
    """
    Returns the previous modification time known for the file (None if the file was unkown)
    """
    with con as cur:
        res = cur.execute(f"SELECT last_modified FROM files WHERE path = ?", [path])
        row = res.fetchone()
        if row != None:
            return row[0]
        return None



def init_db():
    """
    Initializes a connection to the index (and creates it if necessary)
    """
    con = sqlite3.connect("index.db")
    with con as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS files("
            "path TEXT PRIMARY KEY, "
            "last_modified REAL, "
            "content TEXT, "
            "author TEXT, "
            "date TEXT,"
            "subject TEXT "
            ")")
    return con



def indexable(name):
    """
    Returns true if the file matches the pattern we want
    """
    m = re.compile(".*\(was: [^)]+\)\.pdf")
    return m.match(name)



def extract_content(path):
    """
    Returns the text contained in the file
    """
    content = subprocess.check_output(["pdftotext", path, "-"])
    return content



def purge_index(con):
    """
    Remove from the index the files that do not exist anymore
    """
    with con as cur:
        res = cur.execute("SELECT path from files")

    for row in res.fetchall():
        path = row[0]
        if not os.path.isfile(path):
            print(f"- {path}")
            with con as cur:
                cur.execute("DELETE FROM files WHERE path = ?", (path,))


def reindex(path):
    con = init_db()
    index(path, con)
    purge_index(con)



def predict_author(content):
    con = sqlite3.connect("index.db")
    df = pd.read_sql_query("SELECT * FROM files", con)

    clf = Pipeline(steps=[
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', SGDClassifier(loss='hinge', penalty='l2',
                              alpha=1e-3, random_state=42,
                              max_iter=5, tol=None))
    ])

    clf.fit(df["content"], df["author"])
    res = clf.predict([content])
    return res[0]



def predict_language(content):
    import fasttext
    fasttext.FastText.eprint = lambda x: None
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("language_detector")
    doc = nlp(content)
    return doc._.language


def clean(content, spacy_model="en_core_web_md", remove_numbers=True,
        remove_stopwords=False, remove_punct=True, remove_special=True,
        remove_oov=True, pos_to_remove=[], lemmatize=True,
        remove_duplicates=True):

    text = " ".join(content.split())
    nlp = spacy.load(spacy_model, disable=['ner'])
    doc = nlp(text)

    tokens = []
    for token in doc:
        # Remove selected parts of speach
        if token.pos_ in pos_to_remove:
            continue
        # Remove numbers
        if remove_numbers:
            if token.like_num or token.is_currency:
                continue
        # Remove stopwords
        if remove_stopwords:
            if token.is_stop:
                continue
        # Remove empty words
        if token.is_space or token.text.strip() == "":
            continue
        # Remove punctuation
        if remove_punct:
            if token.is_punct:
                continue
        # Remove out of vocabulary words
        if remove_oov:
            if token.is_oov:
                continue
        # Remove words smaller than 2 letters
        if len(token.text.strip()) <= 2:
            continue

        tokens.append(token)

    if lemmatize:
        text = " ".join([token.lemma_ for token in tokens])
    else:
        text = " ".join([token.text for token in tokens])

    # Remove duplicates
    if remove_duplicates:
        text = " ".join(list(set(text.split())))

    return text



def predict_subject(content, lang):

    spacy_model = "en_core_web_md"
    if lang != "en":
        spacy_model = lang + "_core_news_md"

    nlp = spacy.load(spacy_model)

    doc = nlp(content)

    clean_doc = nlp(clean(content, spacy_model=spacy_model))

    #tokens = []
    #for sent in doc.sents:
    #    address = False
    #    for token in sent:
    #        if token.ent_type_ in ("LOC", "PER", "ORG"):
    #            address = True
    #    if not address:
    #        for token in sent:
    #            tokens.append(token)
    #return tokens[0]

    sim = {}
    for token in doc:
        ent_type = token.ent_type_
        if token.vector_norm and token.ent_type_ not in ("LOC", "PER", "ORG"):
            sim[token.text] = token.similarity(clean_doc)

    similarities = [(k, v) for k, v in sim.items()]

    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[0][0]


#def predict_subject(content):
#    import spacy
#    import gensim.models.keyedvectors
#
#    print("loading")
#    nlp = spacy.load('en_core_web_lg')
#
#    wordList =[]
#    vectorList = []
#    for key, vector in nlp.vocab.vectors.items():
#        wordList.append(nlp.vocab.strings[key])
#        vectorList.append(vector)
#
#    kv = gensim.models.keyedvectors.KeyedVectors(nlp.vocab.vectors_length)
#
#    kv.add_vectors(wordList, vectorList)
#    print("loaded")
#
#    print(kv.most_similar('frau'))
#    #import gensim.downloader as api
#
#    #print("loading")
#    #model = api.load("glove-wiki-gigaword-50")
#    #print("loaded")
#    #print(model.most_similar("frau"))
#    return ""


def main():
    path = os.path.expanduser("~/documents/gdrive")
    if not os.path.exists(path):
        sys.exit(1)

    if len(sys.argv) == 1 or sys.argv[1] == "train":
        reindex(path)
        sys.exit(0)

    if len(sys.argv) == 2:
        if os.path.isfile(sys.argv[1]):
            path = sys.argv[1]
            dirname = os.path.dirname(path) or "."
            old = ".".join(os.path.basename(path).split(".")[:-1])
            ext = os.path.basename(path).split(".")[-1]

            content = extract_content(path).decode()

            language = predict_language(content)
            print(f"language: {language}")

            date = predict_date(content, lang=language, ref=datetime.datetime.now())
            print(f"date: {date}")

            author = predict_author(content)
            print(f"author: {author}")

            subject = predict_subject(content, lang=language)
            print(f"subject: {subject}")

            newname = f"{dirname}/{author} - {date} - {subject} (was: {old}).{ext}"
            print(f'Will move {path} -> {newname}')
            try:
                #print(f'Do you want to proceed? [Y/n]')
                #choice = input().lower()
                choice = "y"
                if choice == "" or choice == "y":
                    os.rename(path, newname)
            except KeyboardInterrupt:
                print("no file moved")
                sys.exit(1)

            sys.exit(0)




if __name__ == "__main__":
    main()
