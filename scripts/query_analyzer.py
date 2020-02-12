#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 14:29:14 2019

@author: hannousse
"""
import onto_handler as ont
from pyparsing import CaselessLiteral , Word, alphanums, quotedString,removeQuotes,opAssoc, operatorPrecedence

class UnaryOperation(object):
    'takes one operand,e.g. not'
    def __init__(self, tokens):
        self.op, self.operands = tokens[0]

class BinaryOperation(object):
    'takes two or more operands, e.g. and, or'
    def __init__(self, tokens):
        self.op = tokens[0][1]
        self.operands = tokens[0][0::2]

class SearchAnd(BinaryOperation):
    def __repr__(self):
        return '(AND {0})'.format(' '.join(str(oper) for oper in self.operands))
        
class SearchOr(BinaryOperation):
    def __repr__(self):
        return '(OR {0})'.format(' '.join(str(oper) for oper in self.operands))

class SearchNot(UnaryOperation):
    def __repr__(self):
        return '(NOT {0})'.format(self.operands)

class SearchTerm(object):
    #global root, keys
    'represents a term that is being searched. here just a word'                         
    def __init__(self, tokens):
        self.term = tokens[0]
       

    def __repr__(self):
        return self.term
    

# the grammar
and_ = CaselessLiteral("AND")
or_ = CaselessLiteral("OR")
not_ = CaselessLiteral("NOT")

searchTerm = Word(alphanums) | quotedString.setParseAction(removeQuotes)

searchTerm.setParseAction(SearchTerm)

searchExpr = operatorPrecedence( searchTerm,
                                 [(not_, 1, opAssoc.RIGHT, SearchNot),
                                  (and_, 2, opAssoc.LEFT, SearchAnd),
                                  (or_, 2, opAssoc.LEFT, SearchOr)])
    
#print("= ",searchExpr.parseString('("product line" OR "SLR") AND ("se" OR "software engineering")'))

def get_keys(s,keys) :
    if isinstance(s, SearchTerm):
        return get_Term_keys(s,keys)
    if isinstance(s, SearchOr):
        return get_OR_keys(s,keys)
    if isinstance(s, SearchAnd):
        return get_AND_keys(s,keys)

def get_OR_keys(s,keys) :
    l = []
    for e in s.operands :
        if isinstance(e, SearchTerm):
            l.append(str(e).lower())
        else :
            l.extend(get_keys(e,[]))
    return l

def get_AND_keys(s,keys) :
    l = []
    for e in s.operands :
        if isinstance(e, SearchTerm):
            l.append([str(e).lower()])
        else :
            l.append(get_keys(e,[]))
    return l

def get_Term_keys(s,keys) :
    keys.append([str(s).lower()])
    return keys

def get_keys_from_query() :
    query = input('Enter a Query: ')
    s = searchExpr.parseString(query)[0]
    keys = get_keys(s,[])
    if isinstance(keys[0], str) :
        return [keys]
    return keys


import nltk
import re

def manage_wildcards(text):
    wordlist = [w for w in nltk.corpus.words.words('en') if w.islower()]
    s = text
    s = s.replace('(','')
    s = s.replace(')','')
    s = s.split(" ")
    for e in s :
        if '*' in e:
            e = e.replace('"','')
#            if e[0].isalpha() :
#                le = [w for w in wordlist if re.search('^'+e, w)]
#            else :
            le = [w for w in wordlist if re.search(e, w)]
            if len(le)>0:
                i=1
                st = ''
                for ele in le:
                    if i==1:
                        st+='"'+ele+'"'
                        i+=1
                    else:
                        st+=' OR "'+ele+'"'
                text = text.replace('"'+e+'"',st)
            else:
                text = text.replace(e,e.replace('*',''))
    return text
            
#print(manage_wildcards('("adapt*" OR "reconfigur*")'))

def get_keys_from_text(text) :
    text = manage_wildcards(text)
    s = searchExpr.parseString(text)[0]
    keys = get_keys(s,[])
    if isinstance(keys[0], str) :
        return [keys]
    return keys

def get_expanded_keys(keys,withsupper):
    ekeys = []
    for lk in keys:
        elk = lk.copy()
        for k in lk:
            if not withsupper:
                elk = list(set(elk + ont.get_related_topics(k)))
            else :
                elk = list(set(elk + ont.get_related_topics(k) + ont.get_super_topics(k)))
        ekeys.append(elk)
    return ekeys

def get_synonymous(keys,size):
    ekeys = []
    for lk in keys:
        elk = lk.copy()
        for k in lk:
            elk = list(set(elk + ont.get_synonymous(k,size)))
        ekeys.append(elk)
    return ekeys

#print(ont.get_synonymous('reconfigure'))
def get_close_topics(keys):
    ekeys = []
    for lk in keys:
        elk = lk.copy()
        for k in lk:
            elk = list(set(elk + ont.get_close_ontology_terms(k)))
        ekeys.append(elk)
    return ekeys

def get_friend_keys(keys):
    lkeys = get_close_topics(keys)
    ekeys = []
    for lk in lkeys:
        elk = lk.copy()
        for k in lk:
            parents = ont.get_super_topics(k)
            for p in parents:
                elk = list(set(elk + ont.get_related_topics(p)))
        ekeys.append(elk)
    return ekeys
        

def get_expanded_keys_from_text(text,level,syn,size):
    keys = get_keys_from_text(text)
    friends = []
    #friends = get_friend_keys(keys)
    for i in range(1,level+1):
        if i==1 :
            if syn:
                synonymous = get_synonymous(keys,size)
            keys = get_expanded_keys(keys,False)
        else :
            keys = get_expanded_keys(keys,True)
    if syn:
        for i in range(0,len(keys)) :
            keys[i] = list(set(keys[i] + synonymous[i]))
            #keys[i] = list(set(keys[i] + synonymous[i] + friends[i]))
#    else:
#        for i in range(0,len(keys)) :
#            keys[i] = list(set(keys[i] + friends[i]))
    return keys

#print(ont.get_sub_topics("networked control"))
#print(get_friend_keys([["networked control"]]))
#print(get_friend_keys([["networked control systems"],["software"]])) 
#print(get_expanded_keys_from_text('"networked control"',2,False,0)) 
#+ synonymous[i]
#print(get_keys_from_query())

# Kitchenham:2010 reserch questions
    # "How many SLRs were published between 1st January 2004 and 30th June 2008?"
    # "What research topics are being addressed?"
    # "Which individuals and organizations are most active in SLR-based research?"
    # "Are the limitations of SLRs, as observed in the original study, still an issue?"
    # "Is the quality of SLRs improving?"

#import semantic_scholar_search as sss 
#import spacy
#import nltk
import textrank as tr
#import pke

def get_keys_from_research_questions(rqs) :
#    #rqs = sss.prepare(rqs)
#    # initialize keyphrase extraction model, here TopicRank
#    extractor = pke.unsupervised.TopicRank()
#
#    # load the content of the document, here document is expected to be in raw
#    # format (i.e. a simple text file) and preprocessing is carried out using spacy
#    extractor.load_document(input=rqs, language='en')
#
#    # keyphrase candidate selection, in the case of TopicRank: sequences of nouns
#    # and adjectives (i.e. `(Noun|Adj)*`)
#    extractor.candidate_selection()
#
#    # candidate weighting, in the case of TopicRank: using a random walk algorithm
#    extractor.candidate_weighting()
#
#    # N-best selection, keyphrases contains the 10 highest scored candidates as
#    # (keyphrase, score) tuples
#    return extractor.get_n_best(n=20)

     return tr.extract_keywords_from_text(rqs)
 
def get_expanded_query(text,level,syn,size):
    
    def get_Or_connection(keys):
        query = ''
        for k in keys:
            k = k.replace(' - ','-')
            k = k.replace('- ','-')
            k = k.replace(' -', '-')
            if query :
                query += ' OR ' '"'+k+'"'
            else:
               query += '"'+k+'"'
        return query
        
    keys = get_expanded_keys_from_text(text,level,syn,size)
    equery = ''
    for k in keys:
        if equery :
            equery += ' AND ' '('+get_Or_connection(k)+')'
        else:
            equery += '('+get_Or_connection(k)+')' 
    return equery

#rqs = "How many SLRs were published between 1st January 2004 and 30th June 2008? What research topics are being addressed? Which individuals and organizations are most active in SLR-based research? Are the limitations of SLRs, as observed in the original study, still an issue? Is the quality of SLRs improving?"
#print(get_keys_from_research_questions(rqs))
#print(get_expanded_keys_from_text('evidence-based software engineering',3))
