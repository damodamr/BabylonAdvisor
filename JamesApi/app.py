#from flask import Flask
#from .environment import RDF_PATH
from rdflib import Graph

#app = Flask(__name__)

# Set up rdf-lib connection to prototype file.
rdf_graph = Graph()
rdf_graph.parse("/Users/damir.juric/PycharmProjects/BabylonAdvisor/urn_webprotege_ontology_8c5fd0ff-d7ef-4e72-8e06-462eebaba042.owl")


def query_graph(query: str):
    return rdf_graph.query(query)