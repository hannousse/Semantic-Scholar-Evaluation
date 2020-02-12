#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 15:28:44 2019

@author: hannousse
"""

import os
import json
import pke
#import pandas as pd 
#from openpyxl import load_workbook
import time
import keyword_cluster as kc
import csv
import spacy
import re
from spacy_cld import LanguageDetector

     
nlp = spacy.load('en')
try :
    language_detector = LanguageDetector()
    nlp.add_pipe(language_detector)
except :
    pass


def prepare(graf_text):
    graf_text = graf_text.replace('- ','')
    pat = re.compile(r'[^a-zA-Z0-9 ,-;.?!]+')
    graf_text = re.sub(pat, '',graf_text)
    graf_text = graf_text.replace('\n', ' ').strip()
    graf_text = graf_text.replace('  ', ' ')
    graf_text = graf_text.replace('\t', '')
#    graf_text = graf_text.replace('\'', '')
    return graf_text


def title_in_english(text) :
    doc = nlp(text)
    #print('% ',doc._.languages)
    if len(doc._.languages)>0 and doc._.languages[0] == 'en' :
        return True
    return False


def kpe_extract_keywords(text) :

    def extract_keys(lkeys):
        keys = []
        for k in lkeys :
            keys += k
        return list(set(keys))
    
#    print('* '+text)

    # initialize keyphrase extraction model, here TopicRank
    extractor = pke.unsupervised.TopicRank()

    # load the content of the document, here document is expected to be in raw
    # format (i.e. a simple text file) and preprocessing is carried out using spacy
    extractor.load_document(input=text.lower(), language='en',normalization=None)

    # keyphrase candidate selection, in the case of TopicRank: sequences of nouns
    # and adjectives (i.e. `(Noun|Adj)*`)
    extractor.candidate_selection()
    try :
        # candidate weighting, in the case of TopicRank: using a random walk algorithm
        extractor.candidate_weighting()
    except :
        return []
    # N-best selection, keyphrases contains the 10 highest scored candidates as
    # (keyphrase, score) tuples
    
    return extract_keys(extractor.topics)




def is_similar(pkeys, keys) :
    
    for e in pkeys :
        for k in keys :
            #print(e,' : ',k,' > sim = ',kc.semantic_similarity(e,k,[]))
            if kc.text_occurrence_similarity(k,e): #kc.semantic_similarity(e,k,[]) == 0:
                #print(e,' - ',k,' | ',kc.semantic_similarity(e,k,[]))
                return True
        return False
    return False

def similar_by_entities(ent,keys) :
    if len(ent) == 0 :
        return False
    else :
        for k in keys :
            if not is_similar(ent,k) :
                return False
        return True

def similar_by_text(paper,keys) :
    # extract keys from title + abstract
#    text = text.replace('"', '')
#    text = text.replace("\\",'')
#    keycorpus,acros = tr.extract_keywords_from_text(text)
    text = paper['title']
    text += '. '+paper['journalName']
    if 'paperAbstract' in paper :
        text += ' '+paper['paperAbstract']
    text = prepare(text)
    keycorpus = kpe_extract_keywords(text)
    if len(paper['entities'])>0 :
        text = text+ ' '.join([e.lower() for e in paper['entities']])
        #keycorpus = list(set().union(keycorpus,[e.lower() for e in paper['entities']]))
    keycorpus = [text.lower()]
    if len(keycorpus)>0 :
        for k in keys :
            if not is_similar(keycorpus,k) :
                return False
        return True
    return False


def test_similar_by_text(text,keys) :
    # extract keys from title + abstract
#    text = text.replace('"', '')
#    text = text.replace("\\",'')
#    keycorpus,acros = tr.extract_keywords_from_text(text)
    text = prepare(text)
    keycorpus = kpe_extract_keywords(text)
    print(keycorpus)
    if len(keycorpus)>0 :
        for k in keys :
            if not is_similar(keycorpus,k) :
                return False
        return True
    return False


#def generate_dataframe_from_large_json(filename,keys,from_date,to_date) :
#    
#    ID = []
#    TITLE = []
#    ABSTRACT = []
#    YEAR =[]
#    AUTHORS = []
#    DOI = []
#
#    def is_condidate(paper,start_date,end_date) :
#        try :
#            if ('year' not in paper or ('year' in paper and int(paper['year'])>=start_date and int(paper['year'])<=end_date)) and title_in_english(paper['title']) :
#                return True
#        except :
#            return False
#        return False
#    
#    def add_paper(paper) :
#        ID.append(paper['id'])
#        TITLE.append(paper['title'])
#        if 'abstract' in paper :
#            ABSTRACT.append(paper['abstract'])
#        else : 
#            ABSTRACT.append('None')
#        AUTHORS.append([o['name'] for o in paper['authors']])
#        if 'year' in paper :
#            YEAR.append(paper['year']) 
#        else :
#            YEAR.append('None')
#        if 'doi' in paper :
#            DOI.append(paper['doi']) 
#        else :
#            DOI.append('None')
#
#
#    with open(filename, encoding="UTF-8") as json_file:
#        line_number = 1
#        for line in json_file :
#            print ("Processing paper number: ", line_number)
#            # Use a new parser for each line
#            paper = json.loads(line)
#            if is_condidate(paper,from_date,to_date) :
#                entities = paper['entities']
#                #authors = [o['name'] for o in paper['authors']]
#                if len(entities)> 0 and similar_by_entities(entities,keys) :
#                        add_paper(paper)
#                else :
#                    if similar_by_text(paper['title'],keys) :
#                        add_paper(paper)
#            line_number += 1
#    data = {'ID':ID,'AUTHORS':AUTHORS, 'TITLE':TITLE, 'ABSTRACT':ABSTRACT,'YEAR':YEAR,'DOI':DOI}
#    # ,columns=['ID','TYPE','YEAR','AUTHORS','TITLE','PAGES','DOI']
#    return pd.DataFrame(data, columns=['ID','AUTHORS','TITLE','ABSTRACT','YEAR', 'DOI']).set_index('ID')


def save_if_relevant(query,filename,keys) :
    
    def add_paper(paper) :
        pid = paper['id']
        authors = ','.join([o['name'] for o in paper['authors']])
        title = paper['title']
#        abstract = 'None'
        doi = ''
        year = ''
        source = ''
        entities = paper['entities']
#        if 'paperAbstract' in paper :
#            abstract = paper['paperAbstract']
        if 'year' in paper :
            year = paper['year'] 
        if 'doi' in paper :
            doi = paper['doi'] 
        if 'journalName' in paper :
            source =  paper['journalName']
        row = [pid, authors, title, year, source, doi, entities]
        if not os.path.exists('data/output'):
            os.makedirs('data/output')
        if os.path.isfile('data/output/'+query+'.csv') :
            with open('data/output/'+query+'.csv', 'a') as f :
                writer = csv.writer(f)
                writer.writerow(row)
        else :
            with open('data/output/'+query+'.csv', 'w') as f :
                writer = csv.writer(f)
                writer.writerow(row)
        f.close()
        
    nb = 0    
    with open(filename, encoding="UTF-8") as json_file:
        line_number = 1
        for line in json_file :
            #print ("Processing paper number: ", line_number)
            # Use a new parser for each line
            paper = json.loads(line)
            
#            if paper['title'][0].isalpha():
#                if len(paper['entities'])>0 and similar_by_entities(paper['entities'],keys) :
#                    add_paper(paper)
#                    nb +=1
#                else :
#                abstract =''
#                if 'abstract' in paper:
#                    abstract= paper['abstract'] 
            if len(paper['authors']) > 0 and similar_by_text(paper,keys) :
                add_paper(paper)
                nb +=1
            line_number += 1
    json_file.close()
    return nb,line_number-1

def search_in_corpus(query,keys,date,source) :
    
    def save_if_relevant(query,filename,keys) :
    
        def add_paper(paper) :
            pid = paper['id']
            authors = ','.join([o['name'] for o in paper['authors']])
            title = paper['title']
#            abstract = 'None'
            doi = ''
            year = ''
            source = ''
            entities = paper['entities']
#            if 'paperAbstract' in paper :
#                abstract = paper['paperAbstract']
            if 'year' in paper :
                year = paper['year'] 
            if 'doi' in paper :
                doi = paper['doi'] 
            if 'journalName' in paper :
                source =  paper['journalName']
            row = [pid, authors, title, year, source, doi, entities]
            if not os.path.exists('data/output'):
                os.makedirs('data/output')
            if os.path.isfile('data/output/'+query+'.csv') :
                with open('data/output/'+query+'.csv', 'a') as f :
                    writer = csv.writer(f)
                    writer.writerow(row)
            else :
                with open('data/output/'+query+'.csv', 'w') as f :
                    writer = csv.writer(f)
                    writer.writerow(row)
            f.close()
        
        nb = 0    
        with open(filename, encoding="UTF-8") as json_file:
            line_number = 1
            for line in json_file :
                #print ("Processing paper number: ", line_number)
                # Use a new parser for each line
                paper = json.loads(line)
                
                
            
#            if paper['title'][0].isalpha():
#                if len(paper['entities'])>0 and similar_by_entities(paper['entities'],keys) :
#                    add_paper(paper)
#                    nb +=1
#                else :
#                abstract =''
#                if 'abstract' in paper:
#                    abstract= paper['abstract'] 
#                if (not paper['paperAbstract'] or not paper['journalName']) and paper['doi']:
#                    ab, jn, paper = lpc.get_missed_data_from_doi(paper)
                if len(paper['authors']) > 0 and similar_by_text(paper,keys) :
                    add_paper(paper)
                    nb +=1
                line_number += 1
            json_file.close()
            return nb,line_number-1
    
    
    filenames = []
    for root, dirs, files in os.walk('data/sscholardump/filtered/en-'+str(date)+'/'+source):  
        for filename in files:
            if filename.startswith('s2-corpus-') :
                filenames.append(filename)
#    fl = len(filenames)
#    if istart>0 and istart < fl :
#        filenames = filenames[istart-1:fl]
#    else :
#        filenames = [filenames[fl-1]]
    #print(filenames)
    start = time.time()
    for filename in filenames :
#        print('Current corpus file: ',filename)
#        action = input('ok? ')
#        if action == 'n':
#            break
        pstart = time.time()
        nbre,nb = save_if_relevant(query,'data/sscholardump/filtered/en-'+str(date)+'/'+source+'/'+filename,keys)
        # ask if the user wants to continue to the next file in corpus
        print('----------------------------------------------------------------------')
        print('Searching in ',source,' > ',filename,' : ',date,' is finished.')
        end = time.time()
        row = [filename, nbre, end - pstart]
        if not os.path.exists('data/output'):
            os.makedirs('data/output')
        if os.path.isfile('data/output/'+query+'-stat-'+str(date)+'.csv') :
            with open('data/output/'+query+'-stat-'+str(date)+'.csv', 'a') as stat_f :
                #stat_f.write('\n')
                writer = csv.writer(stat_f)
                writer.writerow(row)
        else :
            with open('data/output/'+query+'-stat-'+str(date)+'.csv', 'w') as stat_f :
                writer = csv.writer(stat_f)
                writer.writerow(['Filename','Nbre of found papers','Execution time'])
                writer.writerow(row)
        stat_f.close()
        print('Execution time = ',end - start,' seconds.')
        print('Number of found papers = ',nbre)
#        action = input('Do you want to continue (y/n): ')
#        if action == 'n' :
#            break

def search_in_corpus_test(filename,query,keys) : 
    
    start = time.time()
    nbre,nb = save_if_relevant(query,filename,keys)
    # ask if the user wants to continue to the next file in corpus
    print('----------------------------------------------------------------------')
    print('Searching in ',filename,' is finished.')
    end = time.time()
    qn = query.split("/")[-1]
    row = [qn, nbre, end - start]
    if not os.path.exists('data/output'):
        os.makedirs('data/output')
    if os.path.isfile(filename+'-stat.csv') :
        with open(filename+'-stat.csv', 'a') as stat_f :
            #stat_f.write('\n')
            writer = csv.writer(stat_f)
            writer.writerow(row)
    else :
        with open(filename+'-stat.csv', 'w') as stat_f :
            writer = csv.writer(stat_f)
            writer.writerow(['Query','Nbre of found papers','Execution time'])
            writer.writerow(row)
    stat_f.close()
    print('Execution time = ',end - start,' seconds.')
    print('Number of found papers = ',nbre)
    per = nbre/nb*100
    print('Percentage of found papers = %5.2f' % per+'%')
    
        
def search_in_original_corpus(output,keys,from_date,to_date) :
        
    for date in range(from_date,to_date + 1):
        search_in_corpus(output,keys,date,'dblp')
        #search_in_corpus(output,keys,date,1,'other')

def s2_snowballing(e):
    bs = []
    fs = []
    def snowballing(e, filename):
        with open(filename, encoding="UTF-8") as json_file:
            for line in json_file :
                paper = json.loads(line)
                if e['ss_id'] in list(paper['incitations']):
                    fs.append(paper)
                if e['ss_id'] in list(paper['outcitations']):
                    bs.append(paper)
        json_file.close()
    return fs, bs
    
    filenames = []
    for root, dirs, files in os.walk('data/sscholardump/'):  
        for filename in files:
            if filename.startswith('s2-corpus-') :
                filenames.append(filename)
    for filename in filenames :
        pfs,pbs = snowballing(e,'data/sscholardump/'+filename)
        bs = list(set(bs + pbs))
        fs = list(set(fs + pfs))
    return bs, fs
