import streamlit as st
import json
import graphviz as graphviz
import os
import requests

from rdflib import Graph, RDF, RDFS
from rdflib import URIRef
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS

g = Graph()
#g.parse("urn_webprotege_ontology_27ee4c66-215c-4563-b64a-83d728653396.owl")#hypertension
g.parse("urn_webprotege_ontology_8c5fd0ff-d7ef-4e72-8e06-462eebaba042.owl")#lifestyle

#processes = URIRef("http://webprotege.stanford.edu/R9rhFHtwjxynjFMQdRdjICi")
#actions = URIRef("http://webprotege.stanford.edu/RBZhgoK8Qeirs0YZu2ad2Kh")
#action1 = URIRef("http://webprotege.stanford.edu/R9kYwMAmH3FSMhlDOlEeLOs") #checkup while standing
#action2 = URIRef("http://webprotege.stanford.edu/RCYsCDkpJ7XlNNgN93swd6C") #review medication and consider referral to specialist
#hasRequirement = URIRef("http://webprotege.stanford.edu/RC7Wq1yEcljB1N9YPUStQZg")
#next = URIRef("http://webprotege.stanford.edu/R7rMKTUfG8K7ryhfq0xDPyk")
#first = URIRef("http://webprotege.stanford.edu/RZElLi8R8mkRSGGDLlahA9")
#process = URIRef("http://webprotege.stanford.edu/R7WEa3ShvTpTuqsAhGYqvHT")#blood pressure measurement
#hasSnippet = URIRef("http://webprotege.stanford.edu/RDM9hbbAS4IdgwRvUbCKiMa")
#snomed = URIRef("http://webprotege.stanford.edu/R9MPy28obbWUhRYlvQ03Y4e")
babylonCode = URIRef("http://webprotege.stanford.edu/R5ZIuf9q1yLqSWjrbrh2AH")

processes = URIRef("http://webprotege.stanford.edu/RBdZ9PjAPQbwHzyQfZFeimJ")
actions = URIRef("http://webprotege.stanford.edu/Rk3YLsMnUvjlpQFbHZaOwb")
hasRequirement = URIRef("http://webprotege.stanford.edu/RBKuVxv3Ag9NVQygDL8qwwX")
next = URIRef("http://webprotege.stanford.edu/RBX9yM6PnHMZmCut0ANkwK2")
first = URIRef("http://webprotege.stanford.edu/RCYcJMTsWRUnM4fNdRyRf4S")
snomed = URIRef("http://webprotege.stanford.edu/RCxRbA67sAZNNYGFNDdGHUe")
hasSnippet = URIRef("http://webprotege.stanford.edu/R9DtWPVELKDzTWPxZMDPCZb")
#babylonCode = URIRef()

def getAllActionLabels(g):
    allActionLabels = set()
    for subj, pred, obj in g:
        #print(g.value(subj, RDFS.label))
        if g.value(subj, RDFS.subClassOf) == actions:
            print(g.value(subj, RDFS.subClassOf))
            if str(g.value(subj, RDFS.label)) not in ['None', 'next', 'first', 'hasRequirement']:
                allActionLabels.add(str(g.value(subj, RDFS.label)))
    return allActionLabels

def getAllProcessLabels(g):
    allProcessLabels = set()
    for subj, pred, obj in g:
        #print(g.value(subj, RDFS.label))
        if g.value(subj, RDFS.subClassOf) == processes:
            print(g.value(subj, RDFS.subClassOf))
            if str(g.value(subj, RDFS.label)) not in ['None', 'next', 'first', 'hasRequirement']:
                allProcessLabels.add(str(g.value(subj, RDFS.label)))
    return allProcessLabels

print(getAllProcessLabels(g))

#print(getAllActionLabels(g))