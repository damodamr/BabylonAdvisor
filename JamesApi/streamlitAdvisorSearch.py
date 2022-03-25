import speech_recognition as sr
from gtts import gTTS
from sentence_transformers import SentenceTransformer, util
import os
import csv
import pickle
import time
import hnswlib
import streamlit as st
import json
from rdflib import Graph, RDF, RDFS
from rdflib import URIRef
import requests
from rdf_uris import(
    PROPERTY_URIS
)
from typing import Dict

from tenYearRisk import (
    compute_ten_year_score
)
from queries import (
    action_requirements_query,
    all_actions_query,
    all_processes_query,
    get_bbln_codes_for_patient,
    next_action_query,
    first_action_query,
    get_patient_info,
    action_age_requirement_query
)
from utils import (
    action_from_uri,
    age_requirement_from_uri,
    bbln_codes_from_requirements,
    check_age_requirement,
    dob_to_age,
    finding_from_uri,
    get_current_process_uri,
    get_first_actions_in_process,
    get_hg_client,
    process_from_uri,
    generate_service_token
)
from app import query_graph, rdf_graph
from graphviz import Digraph

processes = [
URIRef("http://webprotege.stanford.edu/R9BDbRmeRmaRfcu3q6xqeAF"), #anxiety processes
URIRef("http://webprotege.stanford.edu/RC7ZOpCG618ia8SeemEFOcN"), #hypertension processes
URIRef("http://webprotege.stanford.edu/RDnaUto9j5lapcFwhtld1nn"), #low back pain processes
URIRef("http://webprotege.stanford.edu/RBdZ9PjAPQbwHzyQfZFeimJ") #physical activity processes
]

actions = [
URIRef("http://webprotege.stanford.edu/R9UceeCncYQqsBsZKbJG4Io"), #anxiety actions
URIRef("http://webprotege.stanford.edu/RB5g9tutkOpMpP98LCIRsIa"), #hypertension actions
URIRef("http://webprotege.stanford.edu/R8oq6Z2QSPkRqjckE150AZa"), #low back pain actions
URIRef("http://webprotege.stanford.edu/Rk3YLsMnUvjlpQFbHZaOwb") #physical activity actions
]
hasRequirement = URIRef("http://webprotege.stanford.edu/RBKuVxv3Ag9NVQygDL8qwwX")
hasAgeRequirement = URIRef("http://webprotege.stanford.edu/RDuXbIDxtVhZiI5TPwjwXL4")
next = URIRef("http://webprotege.stanford.edu/RBX9yM6PnHMZmCut0ANkwK2")
first = URIRef("http://webprotege.stanford.edu/RCYcJMTsWRUnM4fNdRyRf4S")
snomed = URIRef("http://webprotege.stanford.edu/RCxRbA67sAZNNYGFNDdGHUe")
hasSnippet = URIRef("http://webprotege.stanford.edu/R9DtWPVELKDzTWPxZMDPCZb")
babylonCode = URIRef("http://webprotege.stanford.edu/RBF8Invk9dtsgp4wQD68WeA")
guidelines = URIRef("http://webprotege.stanford.edu/RidmHTIh9sOhg5Caq43scK")
tag = URIRef("http://webprotege.stanford.edu/RBTpM1xSAgAaeYGMGKoh4Kq")

ACTION_URIS = {
    "action": URIRef('http://webprotege.stanford.edu/R8oq6Z2QSPkRqjckE150AZa'),
}

anxietyTriggerProfile = URIRef("http://webprotege.stanford.edu/RCm70q8zZyZruQdPb5TK3Ik")
hypertensionTriggeringProfile = URIRef("http://webprotege.stanford.edu/R9vLo3VL37VAaOxqnqX62si")
lowbackpainTriggeringProfile = URIRef("http://webprotege.stanford.edu/R9vEODY7jVH1IZQWl1sAKGl")
triggeringCodes = URIRef("http://webprotege.stanford.edu/RDpC9Z8hJrtw8hQxEkEs9vz")
entrypoint = URIRef("http://webprotege.stanford.edu/Ra6xj5iTzHitouSDcQ0qPj")
normotensive = URIRef("http://webprotege.stanford.edu/R9hCsTLWQyD01nGM2LXHS82")
preelevated = URIRef("http://webprotege.stanford.edu/R8ipdgO78bakpvgi7d4AE6x")
stage1hypertensionSAP = URIRef("http://webprotege.stanford.edu/R9OpLtWKEwwc1sinhc2CW8E")
stage1hypertensionDAP = URIRef("http://webprotege.stanford.edu/RCmIBfTW2zjwAnBcXqqeLlG")
stage2hypertension = URIRef("http://webprotege.stanford.edu/R8ltOTcZMkncz5nr03KcasI")


@st.cache(allow_output_mutation=True)
def loadModels():
    r = sr.Recognizer()
    mic = sr.Microphone()
    mic = sr.Microphone(device_index=0)

    model_name = 'paraphrase-distilroberta-base-v2'
    #model_name = 'bert-large-nli-stsb-mean-tokens'
    model = SentenceTransformer(model_name)


    dataset_path = "/Users/damir.juric/Downloads/advisor.tsv"
    max_corpus_size = 10000

    embedding_cache_path = 'advisor-embeddings-{}-size-{}.pkl'.format(model_name.replace('/', '_'), max_corpus_size)


    embedding_size = 768    #Size of embeddings
    top_k_hits = 3         #Output k hits

    #Check if embedding cache path exists
    if not os.path.exists(embedding_cache_path):

        # Get all unique sentences from the file
        corpus_sentences = set()
        with open(dataset_path, encoding='utf8') as fIn:
            reader = csv.DictReader(fIn, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                corpus_sentences.add(str(row['label']).lower())
                if len(corpus_sentences) >= max_corpus_size:
                    break

        corpus_sentences = list(corpus_sentences)
        print("Encode the corpus. This might take a while")
        corpus_embeddings = model.encode(corpus_sentences, show_progress_bar=True, convert_to_numpy=True)

        print("Store file on disc")
        with open(embedding_cache_path, "wb") as fOut:
            pickle.dump({'sentences': corpus_sentences, 'embeddings': corpus_embeddings}, fOut)
    else:
        print("Load pre-computed embeddings from disc")
        with open(embedding_cache_path, "rb") as fIn:
            cache_data = pickle.load(fIn)
            corpus_sentences = cache_data['sentences']
            corpus_embeddings = cache_data['embeddings']

    #Defining our hnswlib index
    index_path = "./hnswlibAdvisor.index"
    #We use Inner Product (dot-product) as Index. We will normalize our vectors to unit length, then is Inner Product equal to cosine similarity
    index = hnswlib.Index(space = 'cosine', dim = embedding_size)

    if os.path.exists(index_path):
        print("Loading index...")
        index.load_index(index_path)
    else:
        ### Create the HNSWLIB index
        print("Start creating HNSWLIB index")
        index.init_index(max_elements = len(corpus_embeddings), ef_construction = 400, M = 64)

        # Then we train the index to find a suitable clustering
        index.add_items(corpus_embeddings, list(range(len(corpus_embeddings))))

        print("Saving index to:", index_path)
        index.save_index(index_path)

    # Controlling the recall by setting ef:
    index.set_ef(50)  # ef should always be > top_k_hits
    print("Corpus loaded with {} sentences / embeddings".format(len(corpus_sentences)))
    return r, mic, model, index, top_k_hits, corpus_sentences, corpus_embeddings

def query_graph(query: str):
    return rdf_graph.query(query)


def showRequirements(furi):
    urimetadata = action_from_uri(furi)
    rows = query_graph(action_requirements_query(furi))
    requirements = [finding_from_uri(row.o) for row in rows]
    st.write("Required datapoints for action " + str(urimetadata['label']) + ":")
    for req in requirements:
        print("             Requirement: " + req['label'])
        st.write(str(req['label']))


def printNextAction(furi):
    clinicianAdvices = []
    patientAdvices = []
    print(str(furi))
    rows = query_graph(next_action_query(furi))

    next_actions = [action_from_uri(row.o) for row in rows]
    st.write(next_actions)
    for na in next_actions:
        print("     Next action: " + str(na['label']))
        print("     uri: " + str(na['uri']))
        cladvice = str(na['hasSnippet'])
        clinicianAdvices.append(cladvice)
        patadvice = str(na['hasPatientFacingSnippet'])
        patientAdvices.append(patadvice)
        with st.expander("See required datapoints"):
            showRequirements(na['uri'])

    with st.expander("See clinician facing recommendation"):
        st.write(clinicianAdvices)
    with st.expander("See member facing recommendation"):
        st.write(patientAdvices)

def reqs(entryLink):
    st.session_state.entryLink = entryLink
    showRequirements(entryLink[0])

def nextAct(entryLink):
    st.session_state.entryLink = entryLink
    printNextAction(entryLink[0])


######### Search in the index ###########

def lookup(lab):
    with open("/Users/damir.juric/Downloads/advisor.tsv",'r') as f:
        reader = csv.reader(f)
        code = 'none'
        for row in reader:
            rows = row[0].split('\t')
            #print(rows)
            if str(rows[0]).lower() == str(lab).lower():
                code = rows[1]
    return code

def searchIndex(r, mic, model, index, top_k_hits, corpus_sentences, corpus_embeddings):
    r, mic, model, index, top_k_hits, corpus_sentences, corpus_embeddings = loadModels()
    st.write("Say your query:")
    with mic as source:
        audio = r.listen(source)
        text = r.recognize_google(audio)
        inp_question = text


    start_time = time.time()
    question_embedding = model.encode(inp_question)

    #We use hnswlib knn_query method to find the top_k_hits
    corpus_ids, distances = index.knn_query(question_embedding, k=top_k_hits)

    # We extract corpus ids and scores for the first query
    hits = [{'corpus_id': id, 'score': 1-score} for id, score in zip(corpus_ids[0], distances[0])]
    hits = sorted(hits, key=lambda x: x['score'], reverse=True)
    end_time = time.time()

    print("Input query:", inp_question)
    st.write("Input query:", inp_question)
    print("Results (after {:.3f} seconds):".format(end_time-start_time))
    for hit in hits[0:top_k_hits]:
        lab = lookup(corpus_sentences[hit['corpus_id']])
        print("\t{:.3f}\t{}\t{}".format(hit['score'], corpus_sentences[hit['corpus_id']], str(lab)))
        st.write("\t{:.3f}\t{}\t{}".format(hit['score'], corpus_sentences[hit['corpus_id']], str(lab)))
        myobj = gTTS(text=corpus_sentences[hit['corpus_id']] , lang='en', slow=False)
        myobj.save("query.mp3")
        os.system("afplay " + "query.mp3")

    # Approximate Nearest Neighbor (ANN) is not exact, it might miss entries with high cosine similarity
    # Here, we compute the recall of ANN compared to the exact results
    correct_hits = util.semantic_search(question_embedding, corpus_embeddings, top_k=top_k_hits)[0]
    correct_hits_ids = set([hit['corpus_id'] for hit in correct_hits])

    ann_corpus_ids = set([hit['corpus_id'] for hit in hits])
    if len(ann_corpus_ids) != len(correct_hits_ids):
        print("Approximate Nearest Neighbor returned a different number of results than expected")

    recall = len(ann_corpus_ids.intersection(correct_hits_ids)) / len(correct_hits_ids)
    print("\nApproximate Nearest Neighbor Recall@{}: {:.2f}".format(top_k_hits, recall * 100))

    if recall < 1:
        print("Missing results:")
        for hit in correct_hits[0:top_k_hits]:
            if hit['corpus_id'] not in ann_corpus_ids:
                print("\t{:.3f}\t{}".format(hit['score'], corpus_sentences[hit['corpus_id']]))
    print("\n\n========\n")

def searchIndexByTyping(query, model, index, top_k_hits, corpus_sentences, corpus_embeddings):

    inp_question = query

    start_time = time.time()
    question_embedding = model.encode(inp_question)

    # We use hnswlib knn_query method to find the top_k_hits
    corpus_ids, distances = index.knn_query(question_embedding, k=top_k_hits)

    # We extract corpus ids and scores for the first query
    hits = [{'corpus_id': id, 'score': 1 - score} for id, score in zip(corpus_ids[0], distances[0])]
    hits = sorted(hits, key=lambda x: x['score'], reverse=True)
    end_time = time.time()

    print("Input query:", inp_question)
    print("Results (after {:.3f} seconds):".format(end_time - start_time))

    for hit in hits[0:top_k_hits]:
        lab = lookup(corpus_sentences[hit['corpus_id']])
        print("\t{:.3f}\t{}\t{}".format(hit['score'], corpus_sentences[hit['corpus_id']], str(lab)))

    # Approximate Nearest Neighbor (ANN) is not exact, it might miss entries with high cosine similarity
    # Here, we compute the recall of ANN compared to the exact results
    correct_hits = util.semantic_search(question_embedding, corpus_embeddings, top_k=top_k_hits)[0]
    correct_hits_ids = set([hit['corpus_id'] for hit in correct_hits])

    ann_corpus_ids = set([hit['corpus_id'] for hit in hits])
    if len(ann_corpus_ids) != len(correct_hits_ids):
        print("Approximate Nearest Neighbor returned a different number of results than expected")

    recall = len(ann_corpus_ids.intersection(correct_hits_ids)) / len(correct_hits_ids)
    print("\nApproximate Nearest Neighbor Recall@{}: {:.2f}".format(top_k_hits, recall * 100))

    if recall < 1:
        print("Missing results:")
        for hit in correct_hits[0:top_k_hits]:
            if hit['corpus_id'] not in ann_corpus_ids:
                print("\t{:.3f}\t{}".format(hit['score'], corpus_sentences[hit['corpus_id']]))
    print("\n\n========\n")




def main():
    r, mic, model, index, top_k_hits, corpus_sentences, corpus_embeddings = loadModels()
    st.sidebar.title('Speak to the Advisor')
    st.sidebar.markdown("""Use the dropdown to select the guideline""")
    st.markdown("")
    patient = []
    patient_selection = st.sidebar.selectbox(
        'Load guideline ontology',
        ('Hypertension', 'All'),
        index=0
    )

    st.markdown("")
    if st.sidebar.button('Search the Advisor'):
        searchIndex(r, mic, model, index, top_k_hits, corpus_sentences, corpus_embeddings)
    st.sidebar.markdown("-----------")
    query = st.text_input(
        'Type your query',
        value=''
    )
    if st.sidebar.button('Type your query'):
        searchIndexByTyping(query, model, index, top_k_hits, corpus_sentences, corpus_embeddings)

    uriLink = st.sidebar.text_input('Paste URI here')
    uriLink = str(uriLink).replace("\"", "")
    if st.sidebar.button('Recommend next best action'):
        printNextAction(uriLink)
        #with st.expander("See critical datapoints"):
            #showRequirements(uriLink)


if __name__ == "__main__":
  main()