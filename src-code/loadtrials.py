import xml.etree.ElementTree as ET
import matplotlib as plt
import pandas as pd
import numpy as np
import tarfile
from lxml import etree


import trec
import pprint
import json

import json,re
import trec
import xml.etree.ElementTree as ET

from os import path

# https://wiki.python.org/moin/UsingPickle
import pickle
Qrels = "qrels-clinical_trials.txt" # cvs file (?) with relevante documents

# Queries = "topics-2014_2015-summary.topics" # xml file with queries
# with open(Queries, 'r') as queries_reader:
#     txt = queries_reader.read()

class Trial:
    _nct_id : str
    _brief_title : str
    _detailed_description : str
    _brief_summary : str
    _criteria : str
    _phase : str
    _study_type : str
    _study_design : str
    _condition : str
    _intervention : {}
    _gender : str
    _min_age : int
    _max_age : int
    _healthy_volunteers : str
    _mesh_terms : []

    def __init__(self):
        self._nct_id = ""
        self._intervention = {}
        self._mesh_terms = []

    def show(self):
        print(json.dumps(self.__dict__, indent=4))


def load_trials(eval : trec.TrecEvaluation) -> tuple[ list[str], list[Trial] ]:

    tar = tarfile.open("clinicaltrials.gov-16_dec_2015.tgz", "r:gz")
    i = 0
    ids = []
    full_docs = []

    for tarinfo in tar:
        if tarinfo.size > 500:
            txt = tar.extractfile(tarinfo).read().decode("utf-8", "strict")
            root = ET.fromstring(txt)

            judged = False
            for doc_id in root.iter('nct_id'):
                if doc_id.text in eval.judged_docs:
                    judged = True

            if judged is False:
                continue

            i = i + 1

            trial = Trial()
            
            for brief_title in root.iter('brief_title'):
                ids.append(doc_id.text)
                trial._nct_id = cleanstr(doc_id.text)
                trial._brief_title = cleanstr(brief_title.text)

            trial._detailed_description = trial._brief_title
            for detailed_description in root.iter('detailed_description'):
                for child in detailed_description:
                    trial._detailed_description = cleanstr(child.text)

            trial._brief_summary = trial._brief_title
            for brief_summary in root.iter('brief_summary'):
                for child in brief_summary:
                    trial._brief_summary = cleanstr(child.text)

            trial._criteria = trial._brief_title
            for criteria in root.iter('criteria'):
                for child in criteria:
                    trial._criteria = cleanstr(child.text)
                    
            trial._phase = trial._brief_title
            for phase in root.iter('phase'):
                trial._phase = cleanstr(phase.text)

            for study_type in root.iter('study_type'):
                trial._study_type = cleanstr(study_type.text)
                
            for study_design in root.iter('study_design'):
                trial._study_design = cleanstr(study_design.text)
                
            trial._condition = trial._brief_title
            for condition in root.iter('condition'):
                trial._condition = cleanstr(condition.text)

            for interventions in root.iter('intervention'):
                for child in interventions:
                    trial._intervention[cleanstr(child.tag)] = cleanstr(child.text)

            trial._gender = "both"
            for gender in root.iter('gender'):
                trial._gender = cleanstr(gender.text)
                
            trial._minimum_age = 0
            for minimum_age in root.iter('minimum_age'):
                age = re.findall('[0-9]+', cleanstr(minimum_age.text))
                if age:
                    trial._minimum_age = int(age[0])
                else:
                    trial._minimum_age = 0
                
            trial._maximum_age = 150
            for maximum_age in root.iter('maximum_age'):
                age = re.findall('[0-9]+', cleanstr(maximum_age.text))
                if age:
                    trial._maximum_age = int(age[0])
                else:
                    trial._maximum_age = 150
                
                
            trial._healthy_volunteers = trial._brief_title
            for healthy_volunteers in root.iter('healthy_volunteers'):
                trial._healthy_volunteers = cleanstr(healthy_volunteers.text)
                
            for mesh_term in root.iter('mesh_term'):
                trial._mesh_terms.append(cleanstr(mesh_term.text))
            
            full_docs.append(trial)
            
    tar.close()
    return ids, full_docs

SHORT_QUERIES="topics-2014_2015-summary.topics"
LONG_QUERIES="topics-2014_2015-description.topics"

# Queries = "topics-2014_2015-summary.topics" # xml file with queries
Qrels = "qrels-clinical_trials.txt" # cvs file (?) with relevante documents

# TODO: change later
# def load_queries() -> trec.TrecEvaluation:
def load_queries(filename=SHORT_QUERIES) -> dict[str, str]:
    with open(filename, 'r') as queries_reader:
        txt = queries_reader.read()

    parser = etree.XMLParser(encoding="utf-8", recover=True)
    root = ET.fromstring(txt, parser=parser) # reads and parses the xml file
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