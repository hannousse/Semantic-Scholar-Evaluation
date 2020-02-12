#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 17:02:03 2019

@author: hannousse
"""

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *
import pandas as pd
import base64
from Foundation import NSData, NSPropertyListSerialization
import matplotlib.pyplot as plt
import seaborn as sns


#with open('data/bib.bib') as bibtex_file:
#    bibtex_str = bibtex_file.read()
#
#bib_database = bibtexparser.loads(bibtex_str)
#print(bib_database.entries[0])

# Let's define a function to customize our entries.
# It takes a record and return this record.
def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """
    record = type(record)
    record = author(record)
    record = keyword(record)
    return record

def decode_bdisk(key):
    """Return the relative path of file referenced by key """
    decodedBytes = base64.b64decode(key)
    nsData = NSData.dataWithBytes_length_(decodedBytes, len(decodedBytes))
    plist, fmt, error = NSPropertyListSerialization.propertyListFromData_mutabilityOption_format_errorDescription_(nsData, 0, None, None)
    if plist is None:
        return "Missed"
    else :
        return plist['relativePath']


def bibtex2dframe(bib):
    ID = []
    TYPE = []
    YEAR =[]
    AUTHORS = []
    TITLE = []
    PAGES =[]
    DOI = []
    FILE = []
    KEYWORDS = []
    for b in bib.entries :
        ID.append(b['ID'])
        TYPE.append(b['ENTRYTYPE'])
        YEAR.append(int(b['year']))
        AUTHORS.append(b['author'])
        TITLE.append(b['title'])
        if 'pages' in b :
            PAGES.append(b['pages'])
        else :
            PAGES.append('Missed')
        if 'doi' in b:
            DOI.append(b['doi'])
        else :
            DOI.append('Missed')
        if 'bdsk-file-1' in b:
            FILE.append(decode_bdisk(b['bdsk-file-1']))
        else :
            FILE.append('Missed')
        if 'keywords' in b :
            if b['keywords'].find(',') != -1 :
                KEYWORDS = b['keywords'].split(',')
            else:
                if b['keywords'].find(';') != -1 :
                    KEYWORDS = b['keywords'].split(';')
                else :
                    KEYWORDS = list(b['keywords'])
                
    data = {'ID':ID,'TYPE':TYPE,'YEAR':YEAR,'AUTHORS':AUTHORS,'TITLE':TITLE,'PAGES':PAGES,'DOI':DOI, 'FILE':FILE, 'KEYWORDS':KEYWORDS}
    # ,columns=['ID','TYPE','YEAR','AUTHORS','TITLE','PAGES','DOI']
    return pd.DataFrame(data, columns=['ID','TYPE','YEAR','AUTHORS','TITLE','PAGES','DOI','FILE','KEYWORDS']).set_index('ID')

def getAbstract(bib):
    ID = []
    ABSTRACT = []
    for b in bib.entries :
        ID.append(b['ID'])
        if 'abstract' in b:
            ABSTRACT.append(b['abstract'])
        else :
            ABSTRACT.append('Missed')
    data = {'ID':ID,'ABSTRACT':ABSTRACT}
    return pd.DataFrame.from_dict(data).set_index['ID']

def getText(bib, withkeywords):
    ID = []
    TEXT = []
    KEYS = []
    for b in bib.entries :
        ID.append(b['ID'])
        s = b['title']
        if 'abstract' in b:
            s+='. '+b['abstract']
        if withkeywords :
            s+='. '+b['keywords']
            if b['keywords'].find(',') != -1 :
                KEYS = b['keywords'].split(',')
            else :
                if b['keywords'].find(';') != -1 :
                    KEYS = b['keywords'].split(';')
                else :
                    KEYS += list(b['keywords'])
        TEXT.append(s)
        
    data = {'ID':ID,'TEXT':TEXT}
    FKEYS = []
    for k in KEYS :
       FKEYS.append(k.strip().lower())
    #print(FKEYS)
    return FKEYS, pd.DataFrame(data).set_index('ID')

def de_duplicate(df):
    # remove complete and clear duplicates
    df.drop_duplicates()
    # remove duplicates in doi
    mdoidf = df.loc[df['DOI'] == 'Missed']
    indexes = mdoidf.index.get_values()
    df.drop(indexes)
    df.drop_duplicates('DOI', inplace=True)         
    df.append(mdoidf)
    return df

def get_corpus_from_bibtex(bib):
    with open(bib) as bibtex_file:
        parser = BibTexParser()
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
    return getText(bib_database,True)
    
#with open('data/bib.bib') as bibtex_file:
#    parser = BibTexParser()
##    parser.customization = customizations
#    bib_database = bibtexparser.load(bibtex_file, parser=parser)
##    print(bib_database.entries[0])
##    print(bib_database.entries[0].keys())
#    data = bibtex2dframe(bib_database)
##    data = de_duplicate(data)
##    print(data)
#    sns.set()
#    sns.set_context("poster")
#    sns.distplot(data.YEAR.dropna())
#    plt.show()
#    types = data['TYPE'].unique().tolist()
#    values = data['TYPE'].value_counts()
#    plt.pie(values, labels=types)
#    # add a circle at the center
#    my_circle=plt.Circle( (0,0), 0.7, color='white')
#    p=plt.gcf()
#    p.gca().add_artist(my_circle) 
#    plt.show()

# BM25 can be used instead of TF-IDF to find similarities between documents
    
#from gensim.summarization.bm25 import get_bm25_weights 
#
#corpus = [["black", "cat", "white", "cat"],["cat", "outer", "space"],["wag", "dog"]]
#print(get_bm25_weights(corpus))
#print(get_corpus_from_bibtex('data/bib.bib'))   
        