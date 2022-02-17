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

environment = "dev"
def generate_service_token():
    url = 'https://auth.global1.' + environment + '.babylontech.co.uk/oauth/token'
    header = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    client_id = "1M1m7EKIyUg6e3xdDWJQEFBt4a3F3uyE"
    client_secret = "42drt7aEQTfWLnThhsJ5woWJmYkFJwN0bmKXz38rKjGmseW3d31aavY4q7ZLMiSN"
    data = {'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'client_credentials',
            'audience': 'https://babylonhealth.com'}
    r = requests.post(url, headers=header, data=json.dumps(data))
    return json.loads(r.text)['access_token']

def execute_HG_query(query):
    token = generate_service_token()
    url = 'https://services-uk.dev.babylontech.co.uk/chr/graphql'
    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(query))
    return json.loads(r.text)

def generate_reportedcondition_query(patient_uuid):
    query_string = """query {
            getMedicalRecord(member_uuid: \"""" + patient_uuid + """\") {
              condition {
                id
                code{
                  coding{
                    system
                    code
                    display
                  }
                }
                verificationStatus {
                  coding{
                    system
                    code
                    display
                  }
                }
          convertedCode {
            display
            system
            }
          }
      }
    }"""
    return {"query": query_string}

def generate_vitalsigns_query(patient_uuid):
    query_string = """query { 
  getMedicalRecord(member_uuid: \"""" + patient_uuid + """\") { 
    observation { 
      effectiveDateTime
      code {
        coding {
          system
          code
          display
        }
      }
      valueQuantity {
        unit
        code
        value
        system
      }
      component {
        code {
            coding {
                code
                display
            }
        }
        valueQuantity {
            value
            code
        }
      }
     }  
  } 
}"""
    return {"query": query_string}

def generate_patient_query(patient_uuid):
    query_string = """query{
  getMedicalRecord(member_uuid: \"""" + patient_uuid + """\") {
    patient{
      name {
        family
        given
      }
      gender
      birthDate
    }
  }
}"""
    return {"query": query_string}

def parseHGResults(results):
    foundList = []
   # bd = calculate_age(birthDate['data']['getMedicalRecord']['patient']['birthDate'])
    found = results['data']['getMedicalRecord']['condition']
    for el in found:
        foundList.append(el['code']['coding'][0]['code'])
    return foundList

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




def matchCodes(codes, entrypointLink, patientCodes, patientUUID, numberOfSharedCodes):
    codes = codes.split(", ")
    #print(codes)
    intersection = list(set(patientCodes).intersection(codes))
    print(intersection)
    if len(intersection) > numberOfSharedCodes:
        print("---------------------------")
        print("Triggering endpoint output:")
        print('Matched!!!')
        print("For patient: "+ str(patientUUID) + " guideline entry point found: " + str(entrypointLink) + " " + str(rdf_graph.value(URIRef(entrypointLink), RDFS.label)))
        print("Explanation: patient codes " + str(patientCodes) + " contained in guideline trigger profile " + str(codes))
        scOutput = "Yes"
    else:
        print("Triggering endpoint output:")
        print("Not matched for patient: " + str(patientUUID) )
        scOutput = "No"

    return scOutput

def matchRanges(ranges, entrypointLink, patientValue, patientUUID):
    intersection = list(set(patientValue).intersection(ranges))
    print(intersection)
    if len(intersection) > 1:
        print("---------------------------")
        print("Triggering endpoint output:")
        print('Matched!!!')
        print("For patient: "+ str(patientUUID) + " guideline entry point found: " + str(entrypointLink) + " " + str(rdf_graph.value(URIRef(entrypointLink), RDFS.label)))
        print("Explanation: patient codes " + str(patientValue) + " contained in guideline trigger profile " + str(ranges))
        scOutput = "Yes"
    else:
        print("Triggering endpoint output:")
        print("Not matched for patient: " + str(patientUUID) )
        scOutput = "No"

    return scOutput

def matchBPRanges(patientValueSAP,patientValueDAP, patientUUID):
    print(patientValueSAP)
    entry = []

    if (patientValueSAP < 120) and (patientValueDAP < 80):
        print("---------------------------")
        print("Triggering endpoint output:")
        print('Matched!!!')
        print("For member: "+ str(patientUUID) + " guideline entry point found: " + str(normotensive) + " " + str(rdf_graph.value(URIRef(normotensive), RDFS.label)))
        print("Explanation: patient codes " + str(patientValueSAP) + " contained in guideline trigger profile ")
        scOutput = "Yes"
        entry.append(normotensive)
        st.write("For member: "+ str(patientUUID) + " guideline entry point found: " + str(normotensive) + " " + str(rdf_graph.value(URIRef(normotensive), RDFS.label)))
    if (129 > patientValueSAP > 120) and (patientValueDAP < 80):
        print("---------------------------")
        print("Triggering endpoint output:")
        print('Matched!!!')
        print("For member: "+ str(patientUUID) + " guideline entry point found: " + str(preelevated) + " " + str(rdf_graph.value(URIRef(preelevated), RDFS.label)))
        print("Explanation: patient codes " + str(patientValueSAP) + " contained in guideline trigger profile ")
        scOutput = "Yes"
        entry.append(preelevated)
        st.write("For member: " + str(patientUUID) + " guideline entry point found")
        with st.expander("Show entrypoint"):
            st.write('URI: ' + str(preelevated))
            st.write('Label: ' + str(rdf_graph.value(URIRef(preelevated), RDFS.label)))
    if (139 > patientValueSAP > 130):
        print("---------------------------")
        print("Triggering endpoint output:")
        print('Matched!!!')
        print("For patient: "+ str(patientUUID) + " guideline entry point found: " + str(stage1hypertensionSAP) + " " + str(rdf_graph.value(URIRef(stage1hypertensionSAP), RDFS.label)))
        print("Explanation: patient codes " + str(patientValueSAP) + " contained in guideline trigger profile ")
        scOutput = "Yes"
        entry.append(stage1hypertensionSAP)
        st.write("For member: " + str(patientUUID) + " guideline entry point found")
        with st.expander("Show entrypoint"):
            st.write('URI: ' + str(stage1hypertensionSAP))
            st.write('Label: ' + str(rdf_graph.value(URIRef(stage1hypertensionSAP), RDFS.label)))
    if (80 < patientValueDAP < 89):
        print("---------------------------")
        print("Triggering endpoint output:")
        print('Matched!!!')
        print("For patient: "+ str(patientUUID) + " guideline entry point found: " + str(stage1hypertensionDAP) + " " + str(rdf_graph.value(URIRef(stage1hypertensionDAP), RDFS.label)))
        print("Explanation: patient codes " + str(patientValueSAP) + " contained in guideline trigger profile ")
        scOutput = "Yes"
        entry.append(stage1hypertensionDAP)
        st.write("For member: " + str(patientUUID) + " guideline entry point found")
        with st.expander("Show entrypoint"):
            st.write('URI: ' + str(stage1hypertensionDAP))
            st.write('Label: ' + str(rdf_graph.value(URIRef(stage1hypertensionDAP), RDFS.label)))
    if (patientValueSAP > 139) and (patientValueDAP > 89):
        print("---------------------------")
        print("Triggering endpoint output:")
        print('Matched!!!')
        print("For patient: "+ str(patientUUID) + " guideline entry point found: " + str(stage2hypertension) + " " + str(rdf_graph.value(URIRef(stage2hypertension), RDFS.label)))
        print("Explanation: patient codes " + str(patientValueSAP) + " contained in guideline trigger profile ")
        scOutput = "Yes"
        entry.append(stage2hypertension)
        st.write("For member: " + str(patientUUID) + " guideline entry point found: " + str(stage2hypertension) + " " + str(
            rdf_graph.value(URIRef(stage2hypertension), RDFS.label)))
    return entry

def getTriggeringProfile(g, patientCodes, patient, numberOfSharedCodes, patientValueSAP, patientValueDAP):
    entryLink = matchBPRanges(patientValueSAP, patientValueDAP, patient[0])
    st.write(entryLink)
    # for s, p, o in g.triples((None, RDFS.subClassOf, anxietyTriggerProfile)):
    #     ensembleOutput = ""
    #     print("---------------------------")
    #     print("Trigger rule found!")
    #     print(g.value(s, RDFS.label))
    #     print(f"{s}")
    #
    #     codes = g.value(s, triggeringCodes)
    #     print(codes)
        #entrypointLink = g.value(s, entrypoint)
        #print(entrypointLink)
        #scOutput = matchCodes(codes, entrypointLink, patientCodes, patientUUID, numberOfSharedCodes)
        #entryLink = matchBPRanges(patientValueSAP,patientValueDAP, patientUUID)
        #evOutput = getEvaluatorOutput()
        #evOutput = "Red"
        # print("Shared codes output: " + str(scOutput))
        # print("Evaluator output: " + str(evOutput))
        # if scOutput == "Yes" and evOutput == "Green":
        #     ensembleOutput = True
        # if scOutput == "Yes" and evOutput == "Yellow":
        #     ensembleOutput = True
        # if scOutput == "Yes" and evOutput == "Red":
        #     ensembleOutput = True
        # if scOutput == "No" and evOutput == "Green":
        #     ensembleOutput = False
        # if scOutput == "No" and evOutput == "Yellow":
        #     ensembleOutput = False
        # if scOutput == "No" and evOutput == "Red":
        #     ensembleOutput = True

    return entryLink


def reqs(entryLink):
    st.session_state.entryLink = entryLink
    showRequirements(entryLink[0])

def nextAct(entryLink):
    st.session_state.entryLink = entryLink
    printNextAction(entryLink[0])

def loadPatientData(name):
    patientdata = []
    if name == 'Layla Dunn':
        patientUUID = "fc8e6d65-d226-4137-b5bf-bb6705f905c4"
        age = 41
        sex = 'female'
        ethnicity = ''
        SAP = 125
        DAP = 78
        #query = generate_reportedcondition_query(patientUUID)
        #result = execute_HG_query(query)
        #foundInHG = parseHGResults(result)
        #print("Found in HG: " + str(foundInHG))
        patientdata.append(name)
        patientdata.append(patientUUID)
        patientdata.append(age)
        patientdata.append(sex)
        patientdata.append(ethnicity)
        patientdata.append(SAP)
        patientdata.append(DAP)
    if name == 'Alex Marshal':
        patientUUID = "cf8e7d44-d226-2430-t4bb-bt6705f905c5"
        age = 51
        sex = 'male'
        ethnicity = ''
        SAP = 138
        DAP = 88
        #query = generate_reportedcondition_query(patientUUID)
        #result = execute_HG_query(query)
        #foundInHG = parseHGResults(result)
        #print("Found in HG: " + str(foundInHG))
        patientdata.append(name)
        patientdata.append(patientUUID)
        patientdata.append(age)
        patientdata.append(sex)
        patientdata.append(ethnicity)
        patientdata.append(SAP)
        patientdata.append(DAP)
    return patientdata

def main():
    st.sidebar.title('Advisor Testing Interface')
    st.sidebar.markdown("""Use the dropdown to select the member""")
    st.markdown("")
    patient = []
    patient_selection = st.sidebar.selectbox(
        'Load member data',
        ('Layla Dunn', 'Alex Marshal'),
        index=1
    )
    if patient_selection == "Layla Dunn":
        patient = loadPatientData("Layla Dunn")
        with st.expander("See member data"):
            st.write(patient)
    if patient_selection == "Alex Marshal":
        patient = loadPatientData("Alex Marshal")
        with st.expander("See member data"):
            st.write(patient)

    st.markdown("")

    entryLink = ""
    if 'entryLink' not in st.session_state:
        st.session_state.entryLink = ""

    foundInHG = ['xran8miGiv', 'sU0MCUcM0L']

    if st.sidebar.button("Start member journey for: " + patient[0]):
        entryLink = getTriggeringProfile(rdf_graph, foundInHG, patient, 1, patient[5], patient[6])

        reqsbutton = st.sidebar.button('Show critical data points', on_click=reqs,args=(entryLink,))
        nextbutton = st.sidebar.button('Recommend next best action for: ' + patient[0], on_click=nextAct,args=(entryLink,))

    st.sidebar.markdown("-----------")

    uriLink = st.sidebar.text_input('Paste URI here')
    uriLink = str(uriLink).replace("\"", "")
    if st.sidebar.button('Recommend next best action'):
        printNextAction(uriLink)
        #with st.expander("See critical datapoints"):
            #showRequirements(uriLink)


    st.sidebar.markdown("-----------")
    if patient_selection == "Layla Dunn":
        st.sidebar.write("Calculate 10 year risk for: " + patient[0])
        isMale = st.sidebar.checkbox('male', value=False)
        isFemale = st.sidebar.checkbox('female', value=True)
        isBlack = st.sidebar.checkbox('African American', value=False)
        isWhite = st.sidebar.checkbox('White', value=False)
        isOther = st.sidebar.checkbox('Other', value=False)
        smoker = st.sidebar.checkbox('smoker', value=False)
        hypertensive = st.sidebar.checkbox('On hypertensive treatment', value=False)
        diabetic = st.sidebar.checkbox('Diabetic', value=False)
        age = st.sidebar.number_input('Age', value=patient[2])
        systolicBloodPressure = st.sidebar.number_input('SystolicBloodPressure', value=patient[5])
        totalCholesterol = st.sidebar.number_input('Total cholesterol (mg/dL)', value=175)
        hdl = st.sidebar.number_input('HDL-Cholesterol (mg/dL)', value=25)
        if st.sidebar.button('Calculate'):
            risk = compute_ten_year_score(isMale, isBlack, smoker, hypertensive, diabetic, age, systolicBloodPressure, totalCholesterol, hdl)
            st.sidebar.write('Risk: ' + str(risk) + '%')
    if patient_selection == "Alex Marshal":
        st.sidebar.write("Calculate 10 year risk for: " + patient[0])
        isMale = st.sidebar.checkbox('male', value=True)
        isFemale = st.sidebar.checkbox('female', value=False)
        isBlack = st.sidebar.checkbox('African American', value=False)
        isWhite = st.sidebar.checkbox('White', value=False)
        isOther = st.sidebar.checkbox('Other', value=False)
        smoker = st.sidebar.checkbox('smoker', value=False)
        hypertensive = st.sidebar.checkbox('On hypertensive treatment', value=False)
        diabetic = st.sidebar.checkbox('Diabetic', value=False)
        age = st.sidebar.number_input('Age', value=patient[2])
        systolicBloodPressure = st.sidebar.number_input('SystolicBloodPressure', value=patient[5])
        totalCholesterol = st.sidebar.number_input('Total cholesterol (mg/dL)', value=189)
        hdl = st.sidebar.number_input('HDL-Cholesterol (mg/dL)', value=31)
        if st.sidebar.button('Calculate'):
            risk = compute_ten_year_score(isMale, isBlack, smoker, hypertensive, diabetic, age, systolicBloodPressure, totalCholesterol, hdl)
            st.sidebar.write('Risk: ' + str(risk) + '%')


if __name__ == "__main__":
  main()