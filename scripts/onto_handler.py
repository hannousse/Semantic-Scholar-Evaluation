# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import csv as co
import os
import pickle
import json
import pronto
import re
import urllib.parse

#from owlready2 import *
#onto = get_ontology("CSO.owl")
#onto.load()
#print(onto.search(is_a = requirement_engineering))
#import pronto
#from pronto import Ontology
#ont = Ontology('CSO.owl',parser='OwlXMLParser')
#print(ont['RF:XXXXXXX'].rchildren())

CSO_PATH = "data/cso/cso.csv"
CSO_PICKLE_PATH = "data/cso/cso.p"
CSO_JSON_PATH = "data/cso/cso.json"
SWEBOK_PICKLE_PATH = "data/swebok/swebok.p"
SWEBOK_JSON_PATH = "data/swebok/swebok.json"



def generate_swebok_ontology():
    swebok = {}
    ont = pronto.Ontology('http://www.tomrochette.com/log1000/site/ontology/swebok.owl')
    sont = json.loads(ont.json)
    for key in sont.keys():
        name = sont[key]['name'].lower().replace('_',' ')
        if name and name not in swebok:
            swebok[name] = {'desc':'','sup_topics':[],'sub_topics':[]}
            if 'comment' in sont[key]['other']:
                swebok[name]['desc']='. '.join(sont[key]['other']['comment']).replace('\n',' ')
            if 'can_be' in sont[key]['relations'] and len(sont[key]['relations']['can_be'])>0:
                for e in sont[key]['relations']['can_be']:
                    sub_topic = sont[e]['name'].lower().replace('_',' ')
                    if sub_topic not in swebok[name]['sub_topics']:
                        swebok[name]['sub_topics'].append(sub_topic)
            if 'is_a' in sont[key]['relations'] and len(sont[key]['relations']['is_a'])>0:
                for e in sont[key]['relations']['is_a']:
                    sup_topic = sont[e]['name'].lower().replace('_',' ')
                    if sup_topic not in swebok[name]['sup_topics']:
                        swebok[name]['sup_topics'].append(sup_topic)
    with open('data/swebok/swebok.json','w') as f:
        json.dump(swebok,f)
        f.close()
    return swebok

#ont = pronto.Ontology('http://www.tomrochette.com/log1000/site/ontology/swebok.owl')
#swebok = json.loads(ont.json)
##print(swebok['OWLClassImpl:01248090834286027000'])
#get_term("OWLClassImpl:01248090834286027000")
#print(swebok["OWLClassImpl:01248090834286027000"])
#print(get_term_from_corpus("review"))

#swebok = generate_swebok_ontology()


def generate_cso_dict():
    """Function that generates a dictionay for CSO.3.1 and save it into a json file.
       The dictionary has the following attributes : 
           - name: the name of topic
           - super_topics: the list of super topics for a given topic
           - sub_topics: the list of sub topics for a given topic
           - contributors: the list of topics that a given topic contributes to
           - equivalents: the list of equivalent topics for a given topic
    """
    def clean_cso(PATH):
        """Function that removes prefixes from cso triples """
        with open(CSO_PATH, 'r') as ontoFile:
            ontology = co.reader(ontoFile, delimiter=',')
            schema = "http://cso.kmi.open.ac.uk/schema/"
            topic = "https://cso.kmi.open.ac.uk/topics/"
            for triple in ontology:
                for i in range(0,3):
                    triple[i]= triple[i].replace('<','')
                    triple[i]= triple[i].replace('>','')
                    triple[i]= triple[i].replace(schema,'')
                    triple[i]= triple[i].replace(topic,'')
                if os.path.isfile(PATH) :
                    with open(PATH, 'a') as f :
                        writer = co.writer(f)
                        writer.writerow(triple)
                else :
                    with open(PATH, 'w') as f :
                        writer = co.writer(f)
                        writer.writerow(triple)
                        f.close()

    def clean(text):
        """Function that removes undesirable characters from text """
        text = urllib.parse.unquote(text,encoding='utf-8', errors='replace')
        text = text.replace('_',' ')
        pat = re.compile(r'[^a-zA-Z/_\- ]+')
        text = re.sub(pat, '',text)
        text = text.replace('_',' ')
        return text
    
    
    clean_cso("data/cso/cleaned_cso.csv")
    topics = {}
    with open("data/cso/cleaned_cso.csv", 'r') as ontoFile:
        
        ontology = co.reader(ontoFile, delimiter=',')
        
        for triple in ontology:
            topic = clean(triple[0])
            if topic not in topics:
                topics[topic] = {'name':topic,'super_topics':[],'sub_topics':[],'contributors':[],'equivalents':[]}
            if triple[1] == "cso#superTopicOf": 
                # loading broader topics
                sub_topic = clean(triple[2])
                if sub_topic not in topics:
                    topics[sub_topic] = {'name':sub_topic,'super_topics':[],'sub_topics':[],'contributors':[],'equivalents':[]}
                if sub_topic not in topics[topic]['sub_topics']:
                    topics[topic]['sub_topics'].append(sub_topic)
                if topic not in topics[sub_topic]['super_topics']:
                    topics[sub_topic]['super_topics'].append(topic)
            elif triple[1] == 'cso#contributesTo':
                contibutor = clean(triple[2])
                if contibutor not in topics :
                    topics[contibutor] = {'name':contibutor,'super_topics':[],'sub_topics':[],'contributors':[],'equivalents':[]}
                if contibutor not in topics[topic]['contributors']:
                    topics[topic]['contributors'].append(contibutor)
            elif triple[1] == 'cso#relatedEquivalent':
                equivalent = clean(triple[2])
                if equivalent not in topics :
                    topics[equivalent] = {'name':equivalent,'super_topics':[],'sub_topics':[],'contributors':[],'equivalents':[]}
                if equivalent not in topics[topic]['equivalents']:
                    topics[topic]['equivalents'].append(equivalent)
                if topic not in topics[equivalent]['equivalents']:
                    topics[equivalent]['equivalents'].append(topic)    
    ontoFile.close()
    with open('data/cso/cso.json', 'w') as fp:
        json.dump(topics, fp)
        fp.close()
    return topics


def check_ontology():
    """Function that checks if the ontology file is available. 
       Then it will create the pickle file.
    
    """ 

    if not os.path.exists(CSO_PICKLE_PATH) :
        #print("Ontology pickle file is missing.")
        if not os.path.exists(CSO_JSON_PATH):
            generate_cso_dict()
        with open(CSO_JSON_PATH, 'r') as jf:
            cso = json.load(jf)
        with open(CSO_PICKLE_PATH, 'wb') as cso_file:
            #print("Creating ontology pickle file from a copy of the CSO Ontology found in",CSO_PATH)
            pickle.dump(cso, cso_file)
    if not os.path.exists(SWEBOK_PICKLE_PATH) :
        with open(SWEBOK_JSON_PATH, 'r') as jsf:
            swebok = json.load(jsf)
        with open(SWEBOK_PICKLE_PATH, 'wb') as swebok_file:
         #print("Creating ontology pickle file from a copy of the SWEBOK Ontology found in",CSO_PATH)
             pickle.dump(swebok, swebok_file)


def load_ontology_pickle():
    """Function that loads CSO. 
    This file has been serialised using Pickle allowing to be loaded quickly.
    
    Args:
    Returns:
        fcso (dictionary): containing the found topics with their related topics.
    """
    check_ontology()
    fcso = pickle.load(open(CSO_PICKLE_PATH, "rb"))
    fswebok = pickle.load(open(SWEBOK_PICKLE_PATH, "rb"))
    return fcso,fswebok


def get_similar_ontology_terms(ont,topic):
    res = []
    for term in ont:
        subterms = term.split(" ")
        if len(subterms)==1 and subterms[0] == topic:
            res.append(term)
    return res
    

def get_close_ontology_terms(topic):
    res = []
    cso,swebok = load_ontology_pickle()
    for term in cso:
        if topic in term :
            res.append(term)
    for term in swebok:
        if topic in term :
            res.append(term)
    return res
    

def get_related_topics(topic):
    res = []
    cso,swebok = load_ontology_pickle()
    if topic in cso:
#        if withsuper:
        res=list(set(cso[topic]['equivalents']+cso[topic]['sub_topics']))
    else :
        similar = get_similar_ontology_terms(cso,topic)
        for e in similar:
          #res=list(set(res+cso[e]['equivalents']+cso[e]['sub_topics']+cso[e]['super_topics'])) 
          res=list(set(res+cso[e]['equivalents']+cso[e]['sub_topics']))
#    if topic in swebok:
#        res=list(set(res+swebok[topic]['sub_topics']))
#    else :
#        similar = get_similar_ontology_terms(swebok,topic)
#        for e in similar:
#            res=list(set(res+swebok[e]['sub_topics']))
          #res=list(set(res+swebok[e]['sub_topics']+swebok[e]['sup_topics']))  
    return res

def get_super_topics(topic):
    res = []
    cso,swebok = load_ontology_pickle()
    if topic in cso:
        res = cso[topic]['super_topics']
    if topic in swebok:
        res=list(set(res+swebok[topic]['sup_topics']))
    return res

def get_sub_topics(topic):
    res = []
    cso,swebok = load_ontology_pickle()
    if topic in cso:
        res = cso[topic]['sub_topics']
    if topic in swebok:
        res=list(set(res+swebok[topic]['sub_topics']))
    return res

def get_contributors(topic):
    res = []
    cso,swebok = load_ontology_pickle()
    if topic in cso:
        res = cso[topic]['sub_topics']
    return res


from nltk.corpus import wordnet
from pattern.en import lemma

def get_wornet_synonyms(word):
    res = []
    word=lemma(word)
    for syn in wordnet.synsets(word,wordnet.NOUN):
        for name in syn.lemma_names():
            name = name.replace('_',' ')
            if name not in res:
                res.append(name)
#    for syn in wordnet.synsets(word,wordnet.ADJ):
#        for name in syn.lemma_names():
#            name = name.replace('_',' ')
#            if name not in res:
#                res.append(name)
#    for syn in wordnet.synsets(word,wordnet.VERB):
#        for name in syn.lemma_names():
#            name = name.replace('_',' ')
#            if name not in res:
#                res.append(name)
    return res

from datamuse import datamuse

def get_datamuse_sysnonymous(word,size) :
    api = datamuse.Datamuse()
    terms = api.words(ml=word)
#    return terms
    syns = []
    for t in terms :
        if 'tags' in t and 'n' in t['tags']:
#           #syns.append(t)
            syns.append(t['word'])
    if size != -1:
        if len(syns)>size:
            return syns[0:size]
    return syns

#print(get_datamuse_sysnonymous('webrtc',20))

def get_synonymous(topic,size):
    res = []
    cso,swebok = load_ontology_pickle()
    if topic not in cso :
        res = get_datamuse_sysnonymous(topic,size)
    return res
    

def get_wornet_synonyms_for_key(key):
#    words = key.split(" ")
#    res = []
#    for w in words:
    res = get_wornet_synonyms(key)
    return res

def pprint(l):
    for e in l:
        print(e)
#pprint(get_datamuse_sysnonymous('runtime adaptation',20))
#l =[1,2]
#l = list(set(l+[1,3]))
#print(l)