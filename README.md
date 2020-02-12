# Semantic-Scholar-Evaluation
This project investigate the coverage and the role of Semantic Scholar (S2) search engine in condunting secondary studies in software engineering.

The project contains 4 main folders:

## data:
This folder includes the used data for the elaboration of the project:

 1. cso : Computer Science Ontology described in json file 
 2. swebok: Software Engineering Body of Knowledge described in json file 
 3. sscholardump: this where the dump needs to be saved for proper execution of scripts
 
## results:
This folder includes the set of obtained results:

1. Findings.xlsx : includes final and intermediate results of the project
2. Studies.bib: includes the metadata of included studies in the elaborated review
3. Metadata.bib: includes the metadata of all the included papers in the selected studies (Stduies.bib)

## scripts:
This folder includes python scripts used for the automatic elaboration of the project:

1. bibtexloader.py: enabels loading bibtex files and get needed information to be searched in the S2 dump
2. onto_handler.py: enabels cleaning cso.owl and tronsform it into appropriate json file
3. locate_papers_in_corpus.py: implement the preliminary searches where papers are located in the corpus
4. semantic_scholar_search.py: implement function to search in corpus within provided queries; it also imlement the snowballing process
5. query_analyzer.py: implement search query construction and expansion using ontology terms
6. main.py: is the main file used to launch the execution of the script.

## studies:
This folder gives for each selected review in the study:

1. All.bib: list of all the included papers by the review
2. -Query.bib: list of papers not identified by the original query. References highlighted in red are missing from Semantic Scholar; those highlighted in yellow are found by the query but under a different research field than computer science; those highlighted in orange are also identified by the query but out oyear ranges specified in the review.
3. -Snowballing.bib: list of papers not identified after snowballing
4. -Ontology.bib: list of papers not identified after searching with refined queries
