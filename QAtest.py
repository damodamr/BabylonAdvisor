import streamlit as st
import os
import pandas as pd
import pickle
import csv
from sentence_transformers import SentenceTransformer
import scipy.spatial
from rank_bm25 import BM25Okapi
from figures import *

@st.cache(allow_output_mutation=True)
def load_data0():
    embedder = SentenceTransformer('bert-large-nli-stsb-mean-tokens')
    return embedder

@st.cache(allow_output_mutation=True)
def load_data1(pathModel):
    with open (pathModel, 'rb') as fp:
        corpus_embeddings = pickle.load(fp)
    return corpus_embeddings

@st.cache(allow_output_mutation=True)
def load_data_medQuad(pathmedQuad):
    defList = []
    medQuadLabels = pickle.load(open(pathmedQuad, "rb"))
    for el in medQuadLabels:
        for ell in el:
            defList.append(ell['text'])
    return defList


embedder = load_data0()


def noComboTransformermedQuad(anchor, listX, corpus_embedds, numbCand):

    df2 = pd.read_pickle('/Users/damir.juric/PycharmProjects/machine-reading-ask33/NLPTeam/Streamlit/medQuadDict.pkl')

    tupList = []
    query_embeddings = embedder.encode(anchor)

    closest_n = numbCand
    for query, query_embedding in zip(anchor, query_embeddings):
        distances = scipy.spatial.distance.cdist([query_embedding], corpus_embedds, "cosine")[0]

        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1])

        for idx, distance in results[0:closest_n]:
            tupListSmall = []
            #stri1 = listX[idx].strip()
            stri1 = df2[listX[idx].strip()].strip()
            stri2 = "%.4f" % (1 - distance)
            tupListSmall.append(stri1)
            tupListSmall.append(float(stri2))
            tupList.append(tupListSmall)

    return tupList


# ---------------------
# Common part
# ---------------------
st.sidebar.title('Fuzzli - semantic search')
st.sidebar.markdown("""
Search for coding systems concepts by typing a query. Coding system labels were encoded with sentence-transformer (https://github.com/UKPLab/sentence-transformers).
""")

model_type = st.sidebar.selectbox(
    'Choose the model',
    ('questionsmedQuad', 'coronaKB' ,'coming soon'),
    index=0
)
# load the model

pathModel = '/Users/damir.juric/PycharmProjects/machine-reading-ask33/NLPTeam/SentenceTransformers/pickling/' + model_type
#pathNHSChoices = '/Users/damir.juric/PycharmProjects/machine-reading-ask33/NLPTeam/SentenceTransformers/pickling/' + model_type


pathDict = '/Users/damir.juric/Documents/' + model_type + '.txt'
defListy = load_data_medQuad(pathDict)


corpus_embedds = load_data1(pathModel)

# -------------------------
# Choose option
# -------------------------
option = st.sidebar.selectbox(
    'Task type',
    ('Most similar','use BM25'),
    index=0
)

if option == 'Most similar':

    st.title('Most similar')

    word = st.text_input(
        'Type your query',
        value='cant read'
    )
    numbCand = st.number_input(
        'Number of candidates',
        value=20
    )

    if st.button('Create Ali link'):
        st.write('http://calculon.babylontech.co.uk:9000/?sent=' + str(word).replace(' ', '%20'))

    if st.button('Create KBExplorer link'):
        st.write('https://bbl.health/search?query=' + str(word).replace(' ', '%20') + '&searchType=match')



    title = 'Most similar to %s' % word.upper()
    # run gensim

    if model_type == 'questionsmedQuad':
        try:
            ret = noComboTransformermedQuad([word], defListy, corpus_embedds, numbCand)

        except Exception as e:
            ret = None
            st.markdown('Ups! The concept **%s** is not in   dictionary.' % word)

    if model_type == 'coronaKB':
        try:
            ret = noComboTransformermedCorona([word], defListy, corpus_embedds, numbCand)

        except Exception as e:
            ret = None
            st.markdown('Ups! The concept **%s** is not in   dictionary.' % word)
    else:

        try:
            ret = noComboTransformer([word], defListy, corpus_embedds, numbCand)

        except Exception as e:
            ret = None
            st.markdown('Ups! The concept **%s** is not in   dictionary.' % word)

    if ret is not None:
        # convert to pandas
        data = pd.DataFrame(ret, columns=['word','distance'])

        #chart = render_most_similar(data, title, numbCand)
        #st.altair_chart(chart)

        tabl = st.table(data)

#-------------------------------
