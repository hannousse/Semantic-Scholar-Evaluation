# -*- coding: utf-8 -*-

#import codecs
from scipy.cluster.hierarchy import linkage
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram
from nltk.corpus import wordnet
#import spacy

#nlp = spacy.load('en_core_web_sm')
#def levenshtein(s1,s2):
#    if len(s1) < len(s2):
#        return levenshtein(s2, s1)
#
#    # len(s1) >= len(s2)
#    if len(s2) == 0:
#        return len(s1)
#
#    previous_row = range(len(s2) + 1)
#    for i, c1 in enumerate(s1):
#        current_row = [i + 1]
#        for j, c2 in enumerate(s2):
#            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
#            deletions = current_row[j] + 1       # than s2
#            substitutions = previous_row[j] + (c1 != c2)
#            current_row.append(min(insertions, deletions, substitutions))
#        previous_row = current_row
#
#    return previous_row[-1]


from pattern.en import lemma
#from nltk.corpus.reader.wordnet import WordNetError


#from nltk import word_tokenize, pos_tag
 
def penn_to_wn(tag):
    """ Convert between a Penn Treebank tag to a simplified Wordnet tag """
    if tag.startswith('N'):
        return 'n'
  
    if tag.startswith('J'):
        return 'a'
 
    if tag.startswith('R'):
        return 'r'
 
    return None
 
def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None
 
    try:
        return wordnet.synsets(word, wn_tag)[0]
    except:
        return None

def get_wornet_synonyms(word):
    res = []
    for syn in wordnet.synsets(word,wordnet.NOUN):
        for name in syn.lemma_names():
            # composed wordnet synonymous are concatenated with _ 
            # this character should be replaced by space
            name = name.replace('_',' ')
            if name not in res:
                res.append(name)
    return res


from datamuse import datamuse

def get_datamuse_sysnonymous(word) :
    api = datamuse.Datamuse()
    terms = api.words(ml=word)
#    return terms
    syns = []
    for t in terms :
        if 'tags' in t and 'n' in t['tags'] :#and len(t['word'].split(' '))==1:
            syns.append(t)
           #syns.append(t['word']+':'+str(t['score']))
    return syns


def pprint(l):
    for e in l:
        print(e['word'])
#pprint(get_datamuse_sysnonymous('game'))
#from nltk.stem.snowball import PorterStemmer 
#ps = PorterStemmer()
#print(ps.stem("gamified"))

def is_subkeys(term1, term2) :
    def common_words(key1,key2) :
        return len(set(key1) & set(key2))#/len(key2)
    lt1 = lemma(term1)
    lt2 = lemma(term2)
#    llt1 = lt1.split(" ")
#    llt2 = lt2.split(" ")
#    if common_words(llt1,llt2)== len(llt1) :
#       return True
#    else :
#        return False
#    return all(t in llt2  for t in llt1)
    return lt1 in lt2
 
def keyword_similarity(key1, key2):
    """ compute the sentence similarity using Wordnet """
    # Tokenize and tag
#    key1 = pos_tag(word_tokenize(key1))
#    key2 = pos_tag(word_tokenize(key2))
# 
#    # Get the synsets for the tagged words
#    synsets1 = [tagged_to_synset(*tagged_word) for tagged_word in key1]
#    synsets2 = [tagged_to_synset(*tagged_word) for tagged_word in key2]
# 
#    # Filter out the Nones
#    synsets1 = [ss for ss in synsets1 if ss]
#    synsets2 = [ss for ss in synsets2 if ss]
# 
#    score, count = 0.0, 0
# 
#    # For each word in the first sentence
#    for synset in synsets1:
#        # Get the similarity value of the most similar word in the other sentence
#        ls = [synset.wup_similarity(ss) for ss in synsets2]
#        #print(key1,' : ',key2,' = ',ls)
#        # Filter out the Nones
#        ls = [ss for ss in ls if ss]
#        if len(ls) >0 :
#            best_score = max(ls)
#        else :
#            best_score = None
# 
#        # Check that the similarity could have been computed
#        if best_score is not None:
#            score += best_score
#            count += 1
# 
#    # Average the values
#    if count != 0 :
#        score /= count
#    else :
#        score = 0
#    #print('score = ',score)
#    return score
#    doc = nlp(key2)
#    if doc[0].pos_ in ['NOUN', 'PROPN']:
#        ls = get_wornet_synonyms(key2)
#        if lemma(key1) in ls :
#            return 0
#        
#        for s in ls :
#            if is_subkeys(lemma(key1), s):
#                return 0
    return 1


#def symmetric_keyword_similarity(key1, key2):
#    """ compute the symmetric sentence similarity using Wordnet """
#    def common_words(key1,key2) :
#        return len(set(key1) & set(key2))/len(key2)
#    test = key1
#    lt1 = key1.split(" ")
#    lt2 = key2.split(" ")
#    llt1 = [lemma(t) for t in lt1]
#    llt2 = [lemma(t) for t in lt2]
#    key1 = list(set(llt1) - set(llt2))
##    key2 = list(set(llt2) - set(llt1))
##    i = 0
##    for k1 in key1 :
##        sim = min([keyword_similarity(k1, k2) for k2 in key2])
##        if sim == 0 :
##            i+=1
#                
#    #print(key1,' - ',key2, keyword_similarity(key1, key2)*(1-common_words(llt1,llt2)))
#    print(test,' - ',key2, ' : ',common_words(llt1,llt2))
#    if common_words(llt1,llt2)>0 :
#        return 0
#    else :
#        return 1
    #return len(key1) - common_words(llt1,llt2) 
    
def text_occurrence_similarity(s1,s2):
    return is_subkeys(s1, s2)

def semantic_similarity(s1,s2,acros):
    
    def common_acro_expand(term1,term2) :
        for a in acros :
            if all(elem in acros[a] for elem in [term1,term2]) :
                return True
        return False
            
    def is_synonym(term1,term2) :
        if term1=='':
            if term2 == '' :
                return True
            else :
                return False
        else :
            if lemma(term1) == lemma(term2) :
                return True
            else :
                if common_acro_expand(term1,term2) :
                    return True
                else : 
                    if is_subkeys(term1, term2) :
                        return 0
                    else :
                        return 10
    ls1 = s1.split(" ")
    ls2 = s2.split(" ")
    #print(ls1,ls2)
    if len(ls1) > len(ls2) :
        return semantic_similarity(s2,s1,acros)
    else :
        nestedacros1 = [s for s in ls1 if s in acros]
        nestedacros2 = [s for s in ls2 if s in acros]
        if len(nestedacros1) ==  len(nestedacros2) == 0 :
            if is_subkeys(s1,s2) :
                return 0
            else :
                return 10
                #print(symmetric_keyword_similarity(s1, s2)*10)
                #return symmetric_keyword_similarity(s1, s2)*10
        else :
            if (s1 in acros and s2 in acros[s1]) or (s2 in acros and s1 in acros[s2]) :
                return 0
            else :
            #print('- ',s1,' : ',s2)
                if len(nestedacros1)>0 :
                    for e in nestedacros1 :
                        s1 = s1.replace(e,acros[e][0])
                if len(nestedacros2)>0 :
                    for e in nestedacros2 :
                        s2 = s2.replace(e,acros[e][0])
                return semantic_similarity(s1,s2,acros)      
                #print('+ ',s1,' : ',s2,' : ',s )
                #return s
dict_keys = {}
class keyword_cluster:
    def __init__(self, keys, acronyms):

        self.ids = []
        self.acros = None
        self.data_list = []
        self.data_size = 0
        self.distances = []

        self._f2l(keys,acronyms)
        self.data_size = len(self.data_list)
        self._distance()

    def _f2l(self, f, acro):
        for key in f:
            self.ids.append(key)
            self.data_list.append(key)
        self.acros = acro


    def _distance(self):
        global dict_keys
        lsim = []
        for i in range(self.data_size):
            sim = []
            for j in range(1, self.data_size):
#                similarity = levenshtein(self.data_list[i], self.data_list[j])
                similarity = semantic_similarity(self.data_list[i], self.data_list[j], self.acros)
                lsim.append((self.data_list[i],self.data_list[j],similarity))
                #lsim.append((self.data_list[j],self.data_list[i],similarity))
#                print(self.data_list[i],' - ',self.data_list[j],' : ',similarity)
                sim.append(similarity)
                #self.distances.append(similarity)
            self.distances.append(sim)
        dict_keys = print_similar_keywords(lsim)
        from tabulate import tabulate
        f = open('data/similarity.txt','w')
        f.write(tabulate(lsim,['key1','key2','sim'],"grid"))
    def get_ids(self):
        return self.ids
    
    def ward(self):
        return linkage(self.distances, method='ward')


def get_similarity_in_dendrogram(data,acronyms):
    cluster = keyword_cluster(data,acronyms)
    ids = cluster.get_ids()
    result = cluster.ward()
    mod_ids = [id for id in ids]
    dendrogram(result, p=100, truncate_mode='lastp', labels=mod_ids, leaf_rotation=90)
    #dendrogram(result, orientation='top', labels=mod_ids, distance_sort='descending',show_leaf_counts=True)
#    print(r['leaves'])
#    print(r['ivl'])
    plt.ylim(ymin=-0.5)
#    plt.savefig('data/keys.png')
    plt.show()
    return dict_keys
#corpus = ["systematic literature reviews","systematic literature review","literature reviews","Systematic reviews","Hello world"]
#get_similarity_in_dendrogram(corpus)
#print(synonyms("systematic literature reviews","systematic literature review"))

keys = {}

def print_similar_keywords(sim) :
    
    global keys
    # sort tuples by similarity velues to ensure that similar and quasi-similar lists
    # are sorted
    #sim.sort(key=lambda x:x[2])
    #print(sim)
    
    def in_similar(term) :
        for key in keys:
            if term in keys[key]['similar'] or term in keys[key]['quasi_similar']:
                return True
        return False
    
    def get_root_similar(term) :
        for key in keys:
            if term in keys[key]['similar']or term in keys[key]['quasi_similar'] :
                return key
        return None
     
    
    for e1,e2,sm in sim :
        qs = get_root_similar(e1)
        if e1 != e2 and e1 not in keys and not in_similar(e1) and qs == None:
            keys[e1] = {'similar':[],'quasi_similar':[]}
        if e1 in keys :
            if sm == 0 :
                if e2 != e1 and not in_similar(e2) and e2 not in keys[e1]['similar'] :
                    keys[e1]['similar'].append(e2)
            else :
                if sm < 3.5 and not in_similar(e2):
                    if e1 != e2 and e2 not in keys and e2 not in keys[e1]['quasi_similar'] :
                        keys[e1]['quasi_similar'].append(e2) 
                        
    return keys
            #purify_keyword_dict(keys)

#def purify_keyword_dict(keys) :
#    ekeys = keys.copy()
#    for k in ekeys :
#        for sk in ekeys[k]['similar'] :
#            if sk in keys :
#                for s in keys[sk]['similar'] :
#                    if s not in keys[k]['similar'] :
#                        keys[k]['similar'].append(s)
#                for qs in keys[sk]['quasi_similar'] :
#                    if qs not in keys[k]['quasi_similar'] :
#                        keys[k]['quasi_similar'].append(qs)
#                try:
#                    keys.pop(sk)    
#                except KeyError:
#                    pass    
#        for qsk in ekeys[k]['quasi_similar'] :
#            if qsk in keys :
#                if len(keys[qsk]['quasi_similar'])==0 :
#                    for sk in keys[qsk]['similar'] :
#                        if sk not in keys[k]['quasi_similar'] :
#                            keys[k]['quasi_similar'].append(sk)
#                    try:
#                        keys.pop(qsk)    
#                    except KeyError:
#                        pass 
#    return keys