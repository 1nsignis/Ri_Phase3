import json,re
import trec
import xml.etree.ElementTree as ET


Queries = "topics-2014_2015-summary.topics" # xml file with queries
Qrels = "qrels-clinical_trials.txt" # cvs file (?) with relevante documents

# TODO: change later
# def load_queries() -> trec.TrecEvaluation:
def load_queries() -> dict[str, str]:
    with open(Queries, 'r') as queries_reader:
        txt = queries_reader.read()

    root = ET.fromstring(txt) # reads and parses the xml file
    cases = {} # map with all queries

    # get all the queries
    for query in root.iter('TOP'):
        q_num = query.find('NUM').text
        q_title = query.find('TITLE').text
        cases[q_num] = q_title

    return cases

def get_evaluator(queries):
    return trec.TrecEvaluation(queries, Qrels) 


def cleanstr(txt):
    return re.sub(' +', ' ', txt.strip().replace('\n',''))
