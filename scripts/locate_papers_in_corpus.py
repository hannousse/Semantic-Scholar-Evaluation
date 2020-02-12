#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 11:34:52 2019

@author: basmaphotography
"""

import os
import json
import time
import csv
import bibtexparser
import xploreapi

ELSEVIER_API_KEY = '78a9947113182f75193060ee9fdc5617'
IEEEXPLORER_API_KEY = 'kzh6akjd45a3gvjx9a22gz9u'
SPRINGER__API_KEY = '3f4296e80b3ba278b20a5b3a3a1a4d17'

def generate_corpus_from_bibtex(bib,year):
    i = 1
    corpus = {}
    with open(bib) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
        for e in bib_database.entries:
            entry = {}
            if int(e['year']) == year :
                entry['id'] = e['ID']
                entry['title'] = e['title']
                entry['year'] = e['year']
                if 'doi' in e:
                    entry['doi'] = e['doi'].replace('https://doi.org/','').replace('http://dx.doi.org/','').lower()
                else:
                    entry['doi'] = ""
                corpus[i] = entry
                i+=1
    return corpus

def generate_all_corpus_from_bibtex(bib):
    i = 1
    corpus = {}
    with open(bib) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
        for e in bib_database.entries:
            entry = {}
            entry['id'] = e['ID']
            entry['title'] = e['title']
            entry['year'] = e['year']
            if 'doi' in e:
                entry['doi'] = e['doi'].replace('https://doi.org/','').replace('http://dx.doi.org/','').lower()
            else:
                entry['doi'] = ""
            corpus[i] = entry
            i+=1
    return corpus


def save_if_found(query,corpus,filename,path,date,indblp) :
    
    def save_paper(paper,row) :
        
        if os.path.isfile('data/output/'+query) :
            with open('data/output/'+query, 'a') as jf :
                jf.write('\n')
                json.dump(paper,jf)
                jf.close()
        else :
            with open('data/output/'+query, 'w') as jf :
                json.dump(paper,jf)
                jf.close()

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
    
    
    found = 0        
    with open(path, encoding="UTF-8") as json_file:
        line_number = 1
        for line in json_file :
            #print ("Processing paper number: ", line_number)
            # Use a new parser for each line
            #print(json_file)
            paper = json.loads(line)
            for p_id, p_info in corpus.items():
                if ('doi' in p_info and paper['doi'] and p_info['doi'].replace('https://doi.org/','').lower() == paper['doi'].lower()) or (p_info['title'].lower() == paper['title'].lower()) :
                    if not paper['doi'] and p_info['doi'] :
                        paper['doi'] = p_info['doi']
                    if 'year' in paper:
                        date = paper['year']
                    pdate = p_info['year']
                    if indblp :
                        save_paper(paper,[p_info['id'],filename,'DBLP',str(date), str(pdate),paper['title'],paper['doi']])
                    else :
                        save_paper(paper,[p_info['id'],filename,'Other',str(date), str(pdate), paper['title'],paper['doi']])
                    found +=1
            line_number += 1
    json_file.close()
    return found

def search_in_corpus_file(query,corpus,filename,source,date) :
    global nb

    nbre = 0
    start = time.time()
    nbre += save_if_found(query,corpus,filename,'data/sscholardump/filtered/en-'+str(date)+'/'+source+'/'+filename,date,True)

    print('----------------------------------------------------------------------')
    print('Searching in ',filename,' is finished.')
    end = time.time()
    print('Execution time = ',end - start,' seconds.')
    print('Number of found papers = ',nbre, '/',nb)



def search_in_corpus(query,corpus,date) :
    global nb

    filenames = []
    for filename in os.listdir('data/sscholardump/filtered/en-'+str(date)+'/dblp'):
        if filename.startswith('s2-corpus-') :
            filenames.append(filename)
    nbre = 0
    start = time.time()
    for filename in filenames :
        nbre += save_if_found(query,corpus,filename,'data/sscholardump/filtered/en-'+str(date)+'/dblp/'+filename,date,True)
        if nbre == nb:
            break
    
    if nbre<nb :
        for filename in filenames :
            nbre += save_if_found(query,corpus,filename,'data/sscholardump/filtered/en-'+str(date)+'/other/'+filename,date,False)
            if nbre == nb:
                break

    print('----------------------------------------------------------------------')
    print('Searching in ',filename,' is finished.')
    end = time.time()
    print('Execution time = ',end - start,' seconds.')
    print('Number of found papers = ',nbre, '/',nb)
    return nbre

def search_in_original_corpus(query,corpus) :
    global nb
    def save_if_found(query,corpus,filename,path) :
    
        def save_paper(paper,row) :
        
            if os.path.isfile('data/output/'+query) :
                with open('data/output/'+query, 'a') as jf :
                    jf.write('\n')
                    json.dump(paper,jf)
                    jf.close()
            else :
                with open('data/output/'+query, 'w') as jf :
                    json.dump(paper,jf)
                    jf.close()

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
    
    
        found = 0        
        with open(path, encoding="UTF-8") as json_file:
            line_number = 1
            isfound = False
            for line in json_file :
                #print ("Processing paper number: ", line_number)
                # Use a new parser for each line
                #print(json_file)
                paper = json.loads(line)
                for p_id, p_info in corpus.items():
                    if 'doi' in p_info and paper['doi']:
                        if p_info['doi'].replace('https://doi.org/','').lower() == paper['doi'].lower():
                            isfound = True
                        else:
                            isfound = False
                    else:
                        if p_info['title'].lower() == paper['title'].lower():
                            isfound = True
                        else:
                            isfound = False
                    if isfound:
                        if not paper['doi'] and p_info['doi'] :
                            paper['doi'] = p_info['doi']
                        pdate = paper['year']
                        cdate = p_info['year']
                        if 'DBLP' in paper['sources'] :
                            save_paper(paper,[p_info['id'],filename,'DBLP',str(pdate), str(cdate),paper['title'],paper['doi']])
                        else :
                            save_paper(paper,[p_info['id'],filename,'Other',str(pdate), str(cdate), paper['title'],paper['doi']])
                        found +=1
                line_number += 1
        json_file.close()
        return found


    filenames = []
    for filename in os.listdir('data/sscholardump'):  
        if filename.startswith('s2-corpus-') :
            filenames.append(filename)
    nbre = 0
    start = time.time()
    for filename in filenames :
        nbre += save_if_found(query,corpus,filename,'data/sscholardump/'+filename)
        print (nbre, "Found in : ", filename)
        if nbre == nb:
            break
    
    print('----------------------------------------------------------------------')
    end = time.time()
    print('Execution time = ',end - start,' seconds.')
    print('Number of found papers = ',nbre, '/',nb)
   
    return nbre


def search_in_corpus_from_to(query,corpus,from_date,to_date) :
    global nb
    nbre = 0
    start = time.time()
    for date in range(from_date,to_date):
        nbre += search_in_corpus(query,corpus,date)
    
    print('----------------------------------------------------------------------')
    print('Searching in corpus is finished.')
    end = time.time()
    print('Execution time = ',end - start,' seconds.')
    print('Number of found papers = ',nbre,'/',nb)

import requests

def get_missed_data_from_doi(paper):
    # search in crossref
    abstract = paper['paperAbstract']
    journalName = paper['journalName']
    doi = paper['doi']
    info = requests.get('https://api.crossref.org/v1/works/'+doi)
    info = info.content.decode('utf-8')
    abstract_source = None
    journalName_source = None
    #print(doi)
#    if info != 'Resource not found.' :
#        if not abstract and 'abstract' in json.loads(info)['message'].keys():
#            if json.loads(info)['message']['abstract'].startswith('<jats:p>'):
#                start='<jats:p>'
#                end = '</dc:jats:p>' 
#                info = json.loads(info)['message']['abstract']
#                abstract = info[info.find(start)+len(start):info.find(end)]
#                abstract_source = 'crossref'
#            else :
#                abstract = json.loads(info)['message']['abstract']
#        if not journalName and 'container-title' in json.loads(info)['message'].keys() and len(json.loads(info)['message']['container-title'])>0:
#            journalName = json.loads(info)['message']['container-title'][0]
#            journalName_source = 'crossref'
    
    # search in elsevier
    if not abstract or not journalName :
        info = requests.get('https://api.elsevier.com/content/article/doi/'+doi+'?APIKey='+ELSEVIER_API_KEY+'&httpAccept=text/xml')
        info= info.content.decode('utf-8')
        if not info.startswith('<service-error>'):
            if not abstract :
                start='<dc:description>'
                end = '</dc:description>'
                abstract = info[info.find(start)+len(start):info.find(end)]
                abstract = abstract.replace("\n               ",'')
                abstract_source = 'elsevier'
            if not journalName:
                start='<prism:publicationName>'
                end = '</prism:publicationName>'
                journalName = info[info.find(start)+len(start):info.find(end)]
                journalName_source = 'elsevier'
    # search in ieeexplorer
    if not abstract or not journalName :
        query = xploreapi.XPLORE(IEEEXPLORER_API_KEY)
        query.doi(doi)
        query.dataType('json')
        query.dataFormat('object')
        data = query.callAPI()
        if (data['total_records']>0):
            if not abstract and data['articles'][0]['abstract']:
                abstract = data['articles'][0]['abstract']
                abstract_source = 'ieee'
            if not journalName and data['articles'][0]['publication_title']:
                journalName = data['articles'][0]['publication_title']
                journalName_source = 'ieee'
    # search in springer
    if not abstract or not journalName :        
        info = requests.get('http://api.springernature.com/metadata/json?q=doi:'+doi+'&api_key='+SPRINGER__API_KEY)
        info = info.content.decode('utf-8')
        data = json.loads(info)['records']
        if len(data)>0 :
            if not abstract and  'abstract' in data[0].keys() and data[0]['abstract'] :
                    if (data[0]['abstract'].startswith('Abstract')):
                        abstract = data[0]['abstract'][8:-1]
                    else :
                        abstract = data[0]['abstract']
                    abstract_source = 'springer'
            if not journalName and 'publicationName' in data[0].keys() and data[0]['publicationName'] :
                journalName = data[0]['publicationName']
                journalName_source = 'springer'
                
    if not paper['paperAbstract'] and abstract :
        paper['paperAbstract'] = abstract
    if not paper['journalName'] and journalName :
        paper['journalName'] = journalName  
    return abstract_source, journalName_source, paper


def update_paper_info(filename,ufilename):
    ieee = (0,0)
    elsevier = (0,0)
    springer = (0,0)
    crossref = (0,0)
    missed = (0,0)
    with open(filename, "r") as json_file:
        for line in json_file :
            paper = json.loads(line)
            if (not paper['paperAbstract'] or not paper['journalName']) and paper['doi']:
                if not paper['paperAbstract'] :
                    missed = (missed[0] + 1, missed[1])
                if not paper['journalName'] :
                    missed = (missed[0], missed[1] + 1)
                abstract_source,journalName_source, paper = get_missed_data_from_doi(paper)
                if abstract_source == 'crossref':
                    crossref = (crossref[0] + 1, crossref[1])
                if abstract_source == 'elsevier':
                    elsevier = (elsevier[0] + 1, elsevier[1])
                if abstract_source == 'ieee':
                    ieee = (ieee[0] + 1, ieee[1])
                if abstract_source == 'springer':
                    springer = (springer[0] + 1, springer[1])
                if journalName_source == 'crossref':
                    crossref = (crossref[0], crossref[1]+1)
                if journalName_source == 'elsevier':
                    elsevier = (elsevier[0], elsevier[1]+1)
                if journalName_source == 'ieee':
                    ieee = (ieee[0], ieee[1]+1)
                if journalName_source == 'springer':
                    springer = (springer[0], springer[1]+1)
            if os.path.isfile(ufilename) :
                with open(ufilename, 'a') as jf :
                    jf.write('\n')
                    json.dump(paper,jf)
                    jf.close()
            else :
                with open(ufilename, 'w') as jf :
                    json.dump(paper,jf)
                    jf.close()
        json_file.close()
    print('missed = ',missed)    
    print('ieee = ',ieee)
    print('elsevier = ',elsevier)
    print('springer = ',springer)
    print('crossref = ',crossref)
    

def get_missed_info(filename):
    missed = (0,0)
    with open(filename, "r") as json_file:
        for line in json_file :
            paper = json.loads(line)
            if not paper['paperAbstract'] :
                missed = (missed[0] + 1, missed[1])
            if len(paper['entities']) == 0 :
                    missed = (missed[0], missed[1] + 1)
        json_file.close()
    return missed
         
                        
                    

#        action = input('Do you want to continue (y/n): ')
#        if action == 'n' :
#            break


# Kitchenham 2010 for 2004
#corpus= {
#1: { "id" : "Molokken-Ostvold:2004" , "title" : "A Survey on Software Estimation in the Norwegian Industry"},
#2: { "id" : "Jorgensen:2004" , "title" : "A Review of Studies on Expert Estimation of Software Development Effort"},
#3: { "id" : "Torchiano:2004" , "title" : "Overlooked Aspects of COTS-Based Development"},
#4: { "id" : "Petersson:2004" , "title" : "in software inspections after 10 years research"}
#}

# Kitchenham 2010 for 2005
#corpus= {
#1: { "id" : "Hosbond:2005" , "title" : "Mobile Systems Development: A Literature Review"},
#2: { "id" : "Mair:2005a" , "title" : "The consistency of empirical comparisons of regression and analogy-based software project cost prediction"},
#3: { "id" : "Grimstad:2005" , "title" : "The Clients' Impact on Effort Estimation Accuracy in Software Development Projects"},
#4: { "id" : "Host:2005" , "title" : "Experimental Context Classification: Incentives and Experience of Subjects"},
#5: { "id" : "Segal:2005" , "title" : "The Type of Evidence Produced by Empirical Software Engineers"},
#6: { "id" : "Mair:2005" , "title" : "An Analysis of Data Sets Used to Train and Validate Cost Prediction Systems"},
#7: { "id" : "Jorgensen:2005" , "title" : "Evidence-Based Guidelines for Assessment of Software Development Cost Uncertainty"}
#}


# Kitchenham 2010 for 2006
#corpus= {
#1: { "id" : "Davis:2006" , "title" : "Effectiveness of Requirements Elicitation Techniques: Empirical Results Derived from a Systematic Review"},
#2: { "id" : "Barcelos:2006" , "title" : "Evaluation Approaches for Software Architectural Documents: a Systematic Review"},
#3: { "id" : "Hofer:2006" , "title" : "Status of Empirical Research in Software Engineering"},
#4: { "id" : "Shaw:2006" , "title" : "The Golden Age of Software Architecture : A Comprehensive Survey"},
#5: { "id" : "Galin:2006" , "title" : "Are CMM Program Investments Beneficial? Analyzing Past Studies"},
#6: { "id" : "Juzgado:2006" , "title" : "In Search of What We Experimentally Know about Unit Testing"},
#7: { "id" : "Thelin:2006" , "title" : "What Do We Know about Defect Detection Methods?"},
#8: { "id" : "Yalaho:2006" , "title" : "A Conceptual Model of ICT-Supported Unified Process of International Outsourcing of Software Production"},
#9: { "id" : "Grimstad:2006" , "title" : "Software effort estimation terminology: The tower of Babel"},
#10: { "id" : "Feller:2006" , "title" : "Developing Open Source Software: A Community-Based Analysis of Research"}
#}

    
# Kitchenham 2010 for 2007
#corpus= {
#1: { "id" : "Hanssen:2007" , "title" : "Tailoring and Introduction of the Rational Unified Process"},
#2: { "id" : "Kagdi:2007" , "title" : "A survey and taxonomy of approaches for mining software repositories in the context of software evolution"},
#3: { "id" : "Mohagheghi:2007" , "title" : "Quality, productivity and economic benefits of software reuse: a review of industrial studies"},
#4: { "id" : "Pino:2008" , "title" : "Software process improvement in small and medium software enterprises: a systematic review"},
#5: { "id" : "Wicks:2007" , "title" : "A new research agenda for tool integration"},
#6: { "id" : "Kampenes:2007" , "title" : "A systematic review of effect size in software engineering experiments"},
#7: { "id" : "Freire:2007" , "title" : "Techniques for Developing More Accessible Web Applications: A Survey Towards a Process Classification"},
#8: { "id" : "Davis:2007" , "title" : "A Quantitative Assessment of Requirements Engineering Publications"},
#9: { "id" : "MacDonell:2007" , "title" : "Comparing Local and Global Software Effort Estimation Models -- Reflections on a Systematic Review"},
#10: { "id" : "Jorgensen:2007" , "title" : "Forecasting of Software Development Work Effort : Evidence on Expert Judgment and Formal Models"},
#11: { "id" : "Shepperd:2007" , "title" : "Software Project Economics: A Roadmap"},
#12: { "id" : "Kitchenham:2007" , "title" : "Cross Versus Within-Company Cost Estimation Studies: A Systematic Review"},
#13: { "id" : "Turner:2007" , "title" : "Evidence relating to Object-Oriented software design: A survey"}
#}




# Kitchenham 2010 for 2008
#corpus= {
#1: { "id" : "Bellini:2008" , "title" : "Measurement in Software Engineering: from the Roadmap to the Crossroads"},
#2: { "id" : "Mohagheghi:2008" , "title" : "A Review of Experiences from Applying MDE in Industry"},
#3: { "id" : "DeBoer:2008" , "title" : "In search of 'architectural knowledge'"},
##4: { "id" : "Pino:2008" , "title" : "Software process improvement in small and medium software enterprises: a systematic review"},
#5: { "id" : "Zhang:2008" , "title" : "Reflections on 10 Years of Software Process Simulation Modeling: A Systematic Review"},
#6: { "id" : "Renger:2008" , "title" : "Challenges in Collaborative Modeling: A Literature Review"},
#7: { "id" : "Harjumaa:2008" , "title" : "How Does a Measurement Programme Evolve in Software Organizations?"},
#8: { "id" : "Staples:2008" , "title" : "Systematic review of organizational motivations for adopting CMM-based"},
#9: { "id" : "Liebchen:2008" , "title" : "Data Sets and Data Quality in Software Engineering"},
#10: { "id" : "Neto:2008" , "title" : "Improving Evidence about Software Technologies:"},
#11: { "id" : "Jefferies:2008" , "title" : "A Systematic Literature Review of Approaches to Reengineering for Multi-Channel Access"},
#12: { "id" : "Hannay:2008" , "title" : "The Role of Deliberate Artificial Design Elements in Software Engineering Experiments"}
#}


# Alzubidy 2018 for 2006
#corpus= {
#1: { "id" : "Staples:2007" , "title" : "Experiences using systematic review guidelines"}
#}

# Alzubidy 2018 for 2007

#corpus= {
#1: { "id" : "Malheiros:2007" , "title" : "A Visual Text Mining Approach for Systematic Reviews"},
#2: { "id" : "Brereton:2007" , "title" : "Lessons from Applying the Systematic Literature Review Process Within the Software Engineering Domain"},
#3: { "id" : "De-Almeida-Biolchini:2007" , "title" : "Scientific Research Ontology to Support Systematic Review in Software Engineering"}
#}


# Alzubidy 2018 for 2008

#corpus= {
#1: { "id" : "Beecham:2008" , "title" : "Motivation in Software Engineering: A systematic literature review"},
#2: { "id" : "Staples:2008" , "title" : "Systematic review of organizational motivations for adopting CMM-based SP"},
#3: { "id" : "Dieste:2009" , "title" : "Developing Search Strategies for Detecting Relevant Experiments"}
#}

# Alzubidy 2018 for 2009

#corpus= {
#1: { "id" : "Kitchenham:2009" , "title" : "The impact of limited search procedures for systematic literature reviews — A participant-observer case study"},
#2: { "id" : "Liu:2009" , "title" : "The Role of Software Process Simulation Modeling in Software Risk Management: A Systematic Review"}
#}

# Alzubidy 2018 for 2010

#corpus= {
#1: { "id" : "Fernandez-Saez:2010" , "title" : "SLR-Tool - A Tool for Performing Systematic Literature Reviews"},
#2: { "id" : "Kitchenham:2010" , "title" : "The Educational Value of Mapping Studies of Software Engineering Literature"},
#3: { "id" : "Zhang:2010" , "title" : "Software Process Simulation Modeling: An Extended Systematic Review"},
#4: { "id" : "Rabiser:2010" , "title" : "Requirements for Product Derivation Support: Results from a Systematic Literature Review and an Expert Survey"},
#5: { "id" : "Turner:2010" , "title" : "Does the Technology Acceptance Model Predict Actual Use? A Systematic Literature Review"},
#6: { "id" : "Alves:2010" , "title" : "Requirements Engineering for Software Product Lines: A Systematic Literature Review"},
#7: { "id" : "Da-Silva:2010" , "title" : "Challenges and solutions in distributed software development project management: A systematic literature review"},
#8: { "id" : "Kitchenham:2010b" , "title" : "Systematic literature reviews in software engineering - A tertiary study"},
#9: { "id" : "Prikladnicki:2010" , "title" : "Process Models in the Practice of Distributed Software Development: A Systematic Review of the Literature"},
#10: { "id" : "Ali:2010" , "title" : "A Systematic Review of Comparative Evidence of Aspect-oriented Programming"},
#11: { "id" : "Ramampiaro:2010" , "title" : "Supporting evidence-based Software Engineering with collaborative information retrieval"},
#12: { "id" : "Ali:2010a" , "title" : "A Systematic Review of the Application and Empirical Investigation of Search-Based Test Case Generation"},
#13: { "id" : "Kitchenham:2010a" , "title" : "Refining the systematic literature review process—two participant-observer case studies"}
#}


# Alzubidy 2018 for 2011

#corpus= {
#1: { "id" : "Lane:2011" , "title" : "Process models for service-based applications"},
#2: { "id" : "Petersen:2011" , "title" : "Measuring and predicting software productivity: A systematic map and review"},
#3: { "id" : "Chen:2011" , "title" : "A Systematic Review of Evaluation of Variability Management Approaches in Software Product Lines"},
#4: { "id" : "Zhang:2011" , "title" : "Identifying Relevant Studies in Software Engineering"},
#5: { "id" : "Khan:2011" , "title" : "Barriers in the Selection of Offshore Software Development Outsourcing Vendors: An Exploratory Study Using a Systematic Literature Review"},
#6: { "id" : "Fernandez:2011" , "title" : "Usability Evaluation Methods for the Web: A Systematic Mapping Study"},
#7: { "id" : "Da-Silva:2011" , "title" : "Six Years of Systematic Literature Reviews in Software Engineering: An Updated Tertiary Study"},
#8: { "id" : "Martinez-Ruiz:2012" , "title" : "Requirements and Constructors for Tailoring Software Processes: A Systematic Literature Review"},
#9: { "id" : "Savolainen:2012" , "title" : "Software development project success and failure from the supplier ' s perspective : A systematic literature review"}
#}


# Alzubidy 2018 for 2012

#corpus= {
#1: { "id" : "Bowes:2012" , "title" : "SLuRp: A Tool to Help Large Complex Systematic Literature Reviews Deliver Valid and Rigorous Results"},
#2: { "id" : "Da-Sila:2012" , "title" : "An evidence-based model of distributed software development project management: results from a systematic mapping study"},
#3: { "id" : "Jalali:2012" , "title" : "Systematic Literature Studies: Database Searches vs. Backward Snowballing"},
#4: { "id" : "Pons:2012" , "title" : "A systematic review of applying modern software engineering techniques to developing robotic systems"},
#5: { "id" : "Wen:2012" , "title" : "Systematic literature review of machine learning based software development effort estimation models"},
#6: { "id" : "Hernandes:2012" , "title" : "Using GQM and TAM to evaluate StArt - a tool that supports Systematic Review"},
#7: { "id" : "Barney:2012" , "title" : "Software Quality Trade-offs: A Systematic Map"},
#8: { "id" : "Portillo-Rodriguez:2012" , "title" : "Tools Used in Global Software Engineering: A Systematic Mapping Review"},
#9: { "id" : "Holl:2012" , "title" : "A Systematic Review and an Expert Survey on Capabilities Supporting Multi Product Lines"},
#10: { "id" : "DomiNguez:2012" , "title" : "A Systematic Review of Code Generation Proposals from State Machine Specifications"},
#11: { "id" : "Santiago:2012" , "title" : "Model-Driven Engineering As a New Landscape for Traceability Management: A Systematic Literature Review"},
#12: { "id" : "Silva:2014" , "title" : "Replication of Empirical Studies in Software Engineering Research: A Systematic Mapping Study"}
#}

# Alzubidy 2018 for 2013

#corpus= {
#1: { "id" : "Fernandez:2013" , "title" : "Empirical studies concerning the maintenance of UML diagrams and their use in the maintenance of code: A systematic mapping study"},
#2: { "id" : "Mehmood:2013" , "title" : "Aspect-oriented model-driven code generation: A systematic mapping study"},
#3: { "id" : "Nidhra:2013" , "title" : "Knowledge transfer challenges and mitigation strategies in global software development - A systematic literature review and industrial validation"},
#4: { "id" : "Radjenovic:2013" , "title" : "Software fault prediction metrics"},
#5: { "id" : "Ruiz-Rube:2013" , "title" : "Uses and applications of Software & Systems Process Engineering Meta-Model process models. A systematic mapping study"},
#6: { "id" : "Santos-Rocha:2013" , "title" : "The use of software product lines for business process management"},
#7: { "id" : "Zhang:2013" , "title" : "Systematic reviews in software engineering: An empirical investigation"},
#8: { "id" : "Mahdavi-Hezavehi:2013" , "title" : "Variability in Quality Attributes of Service-based Software Systems: A Systematic Literature Review"},
#9: { "id" : "RievicS:2013" , "title" : "Equality in Cumulative Voting: A Systematic Review with an Improvement Proposal"},
#10: { "id" : "Li:2013" , "title" : "Application of Knowledge-based Approaches in Software Architecture: A Systematic Mapping Study"},
#11: { "id" : "Razas:2013" , "title" : "Topics and Treatments in Global Software Engineering Research - A Systematic Snapshot"},
#12: { "id" : "Carver:2013" , "title" : "Identifying Barriers to the Systematic Literature Review Process"},
#13: { "id" : "Marshall:2013" , "title" : "Tools to Support Systematic Literature Reviews in Software Engineering: A Mapping Study"},
#14: { "id" : "Niazi:2013" , "title" : "Establishing trust in offshore software outsourcing relationships: an exploratory study using a systematic literature review"},
#15: { "id" : "Tahir:2013" , "title" : "A Systematic Review on the Functional Testing of Semantic Web Services"},
#16: { "id" : "Kitchenham:2013" , "title" : "A Systematic Review of Systematic Review Process Research in Software Engineering"}
#}


# Alzubidy 2018 for 2014

#corpus= {
#1: { "id" : "Chagas:2014" , "title" : "Systematic Literature Review on the Characteristics of Agile Project Management in the Context of Maturity Models"},
#2: { "id" : "Gonzalez:2014" , "title" : "Formal verification of static software models in MDE: A systematic review"},
#3: { "id" : "Hassler:2014" , "title" : "Outcomes of a Community Workshop to Identify and Rank Barriers to the Systematic Literature Review Process"},
#4: { "id" : "Luna:2014" , "title" : "State of the Art of Agile Governance: A Systematic Review"},
#5: { "id" : "Manuel:2014" , "title" : "An Approach and a Tool for Systematic Review Research"},
#6: { "id" : "Marshall:2014" , "title" : "Tools to Support Systematic Reviews in Software Engineering: A Feature Analysis"},
#7: { "id" : "Seriai:2014" , "title" : "Validation of Software Visualization Tools: A Systematic Mapping Study"},
#8: { "id" : "Shahin:2014" , "title" : "A systematic review of software architecture visualization techniques"},
#9: { "id" : "Yang:2014" , "title" : "A Systematic Literature Review of Requirements Modeling and Analysis for Self-adaptive Systems"},
#10: { "id" : "Cavalcanti:2014" , "title" : "Challenges and Opportunities for Software Change Request Repositories: A Systematic Mapping Study"},
#11: { "id" : "Lavallee:2014" , "title" : "Performing Systematic Literature Reviews With Novices: An Iterative Approach"},
#12: { "id" : "Ali:2014" , "title" : "A Systematic Literature Review on the Industrial Use of Software Process Simulation"}
#}


# Alzubidy 2018 for 2015

#corpus= {
#1: { "id" : "Al-DAllal:2015" , "title" : "Identifying refactoring opportunities in object-oriented code: A systematic literature review"},
#2: { "id" : "Bakar:2015" , "title" : "Feature extraction approaches from natural language requirements for reuse in software product lines: A systematic literature review"},
#3: { "id" : "Bano:2015" , "title" : "A systematic review on the relationship between user involvement and system success"},
#4: { "id" : "Calderon:2015" , "title" : "A systematic literature review on serious games evaluation: An application to software project management"},
#5: { "id" : "Pitangueira:2015" , "title" : "Software requirements selection and prioritization using SBSE approaches: A systematic review and mapping of the literature"},
#6: { "id" : "Tosi:2015" , "title" : "Supporting the semi-automatic semantic annotation of web services: A systematic literature review"},
#7: { "id" : "Zarour:2015" , "title" : "An investigation into the best practices for the successful design and implementation of lightweight software process assessment methods: A systematic literature review"},
#8: { "id" : "Lopez-Herrejon:2015" , "title" : "A Systematic Mapping Study of Search-based Software Engineering for Software Product Lines"},
#9: { "id" : "Inayat:2015" , "title" : "A Systematic Literature Review on Agile Requirements Engineering Practices and Challenges"},
#10: { "id" : "Sharafi:2015" , "title" : "A Systematic Literature Review on the Usage of Eye-tracking in Software Engineering"}
#}



# Alzubidy 2018 for 2016

#corpus= {
#1: { "id" : "Hassler:2016" , "title" : "Identification of SLR tool needs - results of a community workshop"},
#2: { "id" : "Singh:2016" , "title" : "A Systematic Review of IP Traceback Schemes for Denial of Service Attacks"}
#}

# Alzubidy 2018

#corpus= {
#1: { "id" : "Staples:2007" , "title" : "Experiences using systematic review guidelines"},
#2: { "id" : "Malheiros:2007" , "title" : "A Visual Text Mining Approach for Systematic Reviews"},
#3: { "id" : "Brereton:2007" , "title" : "Lessons from Applying the Systematic Literature Review Process Within the Software Engineering Domain"},
#4: { "id" : "De-Almeida-Biolchini:2007" , "title" : "Scientific Research Ontology to Support Systematic Review in Software Engineering"},
#5: { "id" : "Beecham:2008" , "title" : "Motivation in Software Engineering: A systematic literature review"},
#6: { "id" : "Staples:2008" , "title" : "Systematic review of organizational motivations for adopting CMM-based SP"},
#7: { "id" : "Dieste:2009" , "title" : "Developing Search Strategies for Detecting Relevant Experiments"},
#9: { "id" : "Kitchenham:2009" , "title" : "The impact of limited search procedures for systematic literature reviews — A participant-observer case study"},
#10: { "id" : "Liu:2009" , "title" : "The Role of Software Process Simulation Modeling in Software Risk Management: A Systematic Review"},
#11: { "id" : "Fernandez-Saez:2010" , "title" : "SLR-Tool - A Tool for Performing Systematic Literature Reviews"},
#12: { "id" : "Kitchenham:2010" , "title" : "The Educational Value of Mapping Studies of Software Engineering Literature"},
#13: { "id" : "Zhang:2010" , "title" : "Software Process Simulation Modeling: An Extended Systematic Review"},
#14: { "id" : "Rabiser:2010" , "title" : "Requirements for Product Derivation Support: Results from a Systematic Literature Review and an Expert Survey"},
#15: { "id" : "Turner:2010" , "title" : "Does the Technology Acceptance Model Predict Actual Use? A Systematic Literature Review"},
#16: { "id" : "Alves:2010" , "title" : "Requirements Engineering for Software Product Lines: A Systematic Literature Review"},
#17: { "id" : "Da-Silva:2010" , "title" : "Challenges and solutions in distributed software development project management: A systematic literature review"},
#18: { "id" : "Kitchenham:2010b" , "title" : "Systematic literature reviews in software engineering - A tertiary study"},
#19: { "id" : "Prikladnicki:2010" , "title" : "Process Models in the Practice of Distributed Software Development: A Systematic Review of the Literature"},
#20: { "id" : "Ali:2010" , "title" : "A Systematic Review of Comparative Evidence of Aspect-oriented Programming"},
#21: { "id" : "Ramampiaro:2010" , "title" : "Supporting evidence-based Software Engineering with collaborative information retrieval"},
#22: { "id" : "Ali:2010a" , "title" : "A Systematic Review of the Application and Empirical Investigation of Search-Based Test Case Generation"},
#23: { "id" : "Kitchenham:2010a" , "title" : "Refining the systematic literature review process—two participant-observer case studies"},
#24: { "id" : "Lane:2011" , "title" : "Process models for service-based applications"},
#25: { "id" : "Petersen:2011" , "title" : "Measuring and predicting software productivity: A systematic map and review"},
#26: { "id" : "Chen:2011" , "title" : "A Systematic Review of Evaluation of Variability Management Approaches in Software Product Lines"},
#27: { "id" : "Zhang:2011" , "title" : "Identifying Relevant Studies in Software Engineering"},
#28: { "id" : "Khan:2011" , "title" : "Barriers in the Selection of Offshore Software Development Outsourcing Vendors: An Exploratory Study Using a Systematic Literature Review"},
#29: { "id" : "Fernandez:2011" , "title" : "Usability Evaluation Methods for the Web: A Systematic Mapping Study"},
#30: { "id" : "Da-Silva:2011" , "title" : "Six Years of Systematic Literature Reviews in Software Engineering: An Updated Tertiary Study"},
#31: { "id" : "Martinez-Ruiz:2012" , "title" : "Requirements and Constructors for Tailoring Software Processes: A Systematic Literature Review"},
#32: { "id" : "Savolainen:2012" , "title" : "Software development project success and failure from the supplier ' s perspective : A systematic literature review"},
#33: { "id" : "Fernandez:2013" , "title" : "Empirical studies concerning the maintenance of UML diagrams and their use in the maintenance of code: A systematic mapping study"},
#34: { "id" : "Mehmood:2013" , "title" : "Aspect-oriented model-driven code generation: A systematic mapping study"},
#35: { "id" : "Nidhra:2013" , "title" : "Knowledge transfer challenges and mitigation strategies in global software development - A systematic literature review and industrial validation"},
#36: { "id" : "Radjenovic:2013" , "title" : "Software fault prediction metrics"},
#37: { "id" : "Ruiz-Rube:2013" , "title" : "Uses and applications of Software & Systems Process Engineering Meta-Model process models. A systematic mapping study"},
#38: { "id" : "Santos-Rocha:2013" , "title" : "The use of software product lines for business"},
#39: { "id" : "Zhang:2013" , "title" : "Systematic reviews in software engineering: An empirical investigation"},
#40: { "id" : "Mahdavi-Hezavehi:2013" , "title" : "Variability in Quality Attributes of Service-based Software Systems: A Systematic Literature Review"},
#41: { "id" : "RievicS:2013" , "title" : "Equality in Cumulative Voting: A Systematic Review with an Improvement Proposal"},
#42: { "id" : "Li:2013" , "title" : "Application of Knowledge-based Approaches in Software Architecture: A Systematic Mapping Study"},
#43: { "id" : "Razas:2013" , "title" : "Topics and Treatments in Global Software Engineering Research - A Systematic Snapshot"},
#44: { "id" : "Carver:2013" , "title" : "Identifying Barriers to the Systematic Literature Review Process"},
#45: { "id" : "Marshall:2013" , "title" : "Tools to Support Systematic Literature Reviews in Software Engineering: A Mapping Study"},
#46: { "id" : "Niazi:2013" , "title" : "Establishing trust in offshore software outsourcing relationships: an exploratory study using a systematic literature review"},
#47: { "id" : "Tahir:2013" , "title" : "A Systematic Review on the Functional Testing of Semantic Web Services"},
#48: { "id" : "Kitchenham:2013" , "title" : "A Systematic Review of Systematic Review Process Research in Software Engineering"},
#49: { "id" : "Chagas:2014" , "title" : "Systematic Literature Review on the Characteristics of Agile Project Management in the Context of Maturity Models"},
#50: { "id" : "Gonzalez:2014" , "title" : "Formal verification of static software models in MDE: A systematic review"},
#51: { "id" : "Hassler:2014" , "title" : "Outcomes of a Community Workshop to Identify and Rank Barriers to the Systematic Literature Review Process"},
#52: { "id" : "Luna:2014" , "title" : "State of the Art of Agile Governance: A Systematic Review"},
#53: { "id" : "Manuel:2014" , "title" : "An Approach and a Tool for Systematic Review Research"},
#54: { "id" : "Marshall:2014" , "title" : "Tools to Support Systematic Reviews in Software Engineering: A Feature Analysis"},
#55: { "id" : "Seriai:2014" , "title" : "Validation of Software Visualization Tools: A Systematic Mapping Study"},
#56: { "id" : "Shahin:2014" , "title" : "A systematic review of software architecture visualization techniques"},
#57: { "id" : "Yang:2014" , "title" : "A Systematic Literature Review of Requirements Modeling and Analysis for Self-adaptive Systems"},
#58: { "id" : "Cavalcanti:2014" , "title" : "Challenges and Opportunities for Software Change Request Repositories: A Systematic Mapping Study"},
#59: { "id" : "Lavallee:2014" , "title" : "Performing Systematic Literature Reviews With Novices: An Iterative Approach"},
#60: { "id" : "Ali:2014" , "title" : "A Systematic Literature Review on the Industrial Use of Software Process Simulation"},
#61: { "id" : "Al-DAllal:2015" , "title" : "Identifying refactoring opportunities in object-oriented code: A systematic literature review"},
#62: { "id" : "Bakar:2015" , "title" : "Feature extraction approaches from natural language requirements for reuse in software product lines: A systematic literature review"},
#63: { "id" : "Bano:2015" , "title" : "A systematic review on the relationship between user involvement and system success"},
#64: { "id" : "Calderon:2015" , "title" : "A systematic literature review on serious games evaluation: An application to software project management"},
#65: { "id" : "Pitangueira:2015" , "title" : "Software requirements selection and prioritization using SBSE approaches: A systematic review and mapping of the literature"},
#66: { "id" : "Tosi:2015" , "title" : "Supporting the semi-automatic semantic annotation of web services: A systematic literature review"},
#67: { "id" : "Zarour:2015" , "title" : "An investigation into the best practices for the successful design and implementation of lightweight software process assessment methods: A systematic literature review"},
#68: { "id" : "Lopez-Herrejon:2015" , "title" : "A Systematic Mapping Study of Search-based Software Engineering for Software Product Lines"},
#69: { "id" : "Inayat:2015" , "title" : "A Systematic Literature Review on Agile Requirements Engineering Practices and Challenges"},
#70: { "id" : "Sharafi:2015" , "title" : "A Systematic Literature Review on the Usage of Eye-tracking in Software Engineering"},
#71: { "id" : "Hassler:2016" , "title" : "Identification of SLR tool needs - results of a community workshop"},
#72: { "id" : "Singh:2016" , "title" : "A Systematic Review of IP Traceback Schemes for Denial of Service Attacks"}
#}

# Missed peper test 

#corpus = {
#          1: {'id': 'Von_Krogh:2003', 'title': "Community, Joining, and Specialization in Open Source Software Innovation: A Case Study", 'year': 2003, 'doi': '10.2139/ssrn.387500'},
#          2: {'id': 'West:2003', 'title': 'How Open is Open Enough? Melding Proprietary and Open Source Platform Strategies', 'year': 2003, 'doi': ''},
#          3: {'id': 'Henkel:2014', 'title': 'The Emergence of Openness: How and Why Firms Adopt Selective Revealing in Open Innovation','year': 2014, 'doi': '10.2139/ssrn.2261328'},
#          4: {'id': 'Rahman:2019', 'title': 'A systematic mapping study of infrastructure as code research', 'doi': '10.1016/j.infsof.2018.12.004'},
#          5: {'id': 'Hickey:2007', 'title': 'An Ontological Approach to Requirements Elicitation Technique Selection', 'doi': '10.1007/978-0-387-37022-4_14'},
#          6: {'id': 'Kitamura:2007', 'title': 'A Supporting Tool for Requirements Elicitation Using a Domain Ontology', 'doi': '10.1007/978-3-540-88655-6_10'},
#          7: {'id': 'Kossmann:2010', 'title': '7.4.3 Ontology‐driven Requirements Engineering —A case study of OntoREM in the aerospace context', 'doi': '10.1002/j.2334-5837.2010.tb01120.x'},
#          8: {'id': 'Lasheras:2009', 'title': "Modeling Reusable Security Requirements Based on an Ontology Framework", 'doi': '10.1.1.462.6396'},
#          9: {'id': 'Manuel:2014', 'title': 'An Approach and a Tool for Systematic Review Research', 'doi': ''},
#          10: {'id': 'Savolainen:2012', 'title': "Software development project success and failure from the supplier's perspective: A systematic literature review", 'doi': '10.1016/j.ijproman.2011.07.002'},
#          11: {'id': 'Kheirkhahzadeh:2016', 'title': 'Practice makes perfect – Gamification of a competitive learning experience', 'doi': ''},
#          12: {'id': 'Thomas:2013', 'title': 'Redesign of a Gamified Software Engineering Course Step 2 Scaffolding: Bridging the Motivation Gap', 'doi': ''},
#          13: {'id': 'Mahnic:2015', 'title': 'From Scrum to Kanban: Introducing Lean Principles to a Software Engineering Capstone Course', 'doi': ''},
#          14: {'id': 'Younas:2016', 'title': 'A Framework for Agile Development in Cloud Computing Environment', 'doi': '10.7472/jksii.2016.17.5.67'},
#          15: {'id': 'Haig_Smith:2016', 'title': 'Cloud Computing as an Enabler of Agile Global Software Development', 'doi': '10.28945/3476'},
#      }


#print(generate_corpus_from_bibtex('data/Raatikainen-2019.bib',2016))
#corpus = generate_corpus_from_bibtex('data/output/Razzaq-2018/Razzaq-2018.bib',2019)
#corpus = generate_all_corpus_from_bibtex('data/output/Hannousse-2019/Hannousse-2019.bib')
#print(corpus[1]['year'])
#nb = len(corpus)
#print(nb)
#search_in_corpus("Munir-2015/Munir2015",corpus,2014)
#search_in_original_corpus("Munir-2015/Munir2015",corpus)
#search_in_corpus("Mariani-2016/Mariani2016",corpus,2011)
#search_in_corpus_file("Kitchenham2010",corpus,"s2-corpus-09",'dblp',2006)
missed = get_missed_info('data/output/Younas-2018/Younas2018')
print('missed abstracts = ',missed[0]) 
print('missed entities = ',missed[1]) 

#update_paper_info('data/output/Pedreira-2015/Pedreira2015','data/output/Pedreira-2015/uPedreira2015')