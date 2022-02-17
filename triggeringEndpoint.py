from rdflib import Graph, RDF, RDFS
from rdflib import URIRef
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS
import json
import os
import requests
import random

g = Graph()
g.parse("urn_webprotege_ontology_8c5fd0ff-d7ef-4e72-8e06-462eebaba042.owl")#lifestyle

anxietyTriggerProfile = URIRef("http://webprotege.stanford.edu/RCm70q8zZyZruQdPb5TK3Ik")
hypertensionTriggeringProfile = URIRef("http://webprotege.stanford.edu/R9vLo3VL37VAaOxqnqX62si")
lowbackpainTriggeringProfile = URIRef("http://webprotege.stanford.edu/R9vEODY7jVH1IZQWl1sAKGl")
triggeringCodes = URIRef("http://webprotege.stanford.edu/RDpC9Z8hJrtw8hQxEkEs9vz")
entrypoint = URIRef("http://webprotege.stanford.edu/Ra6xj5iTzHitouSDcQ0qPj")
normotensive = URIRef("http://webprotege.stanford.edu/R9hCsTLWQyD01nGM2LXHS82")
preelevated = URIRef("http://webprotege.stanford.edu/R8ipdgO78bakpvgi7d4AE6x")
stage1hypertension = URIRef("http://webprotege.stanford.edu/R9OpLtWKEwwc1sinhc2CW8E")
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

def parseHGResults(results):
    foundList = []
   # bd = calculate_age(birthDate['data']['getMedicalRecord']['patient']['birthDate'])
    found = results['data']['getMedicalRecord']['condition']
    for el in found:
        foundList.append(el['code']['coding'][0]['code'])
    return foundList


def getEvaluatorOutput():
    evOutputs = ["red", "yellow", "green"]
    return random.choice(evOutputs)

def matchCodes(codes, entrypointLink, patientCodes, patientUUID, numberOfSharedCodes):
    codes = codes.split(", ")
    #print(codes)
    intersection = list(set(patientCodes).intersection(codes))
    print(intersection)
    if len(intersection) > numberOfSharedCodes:
        print("---------------------------")
        print("Triggering endpoint output:")
        print('Matched!!!')
        print("For patient: "+ str(patientUUID) + " guideline entry point found: " + str(entrypointLink) + " " + str(g.value(URIRef(entrypointLink), RDFS.label)))
        print("Explanation: patient codes " + str(patientCodes) + " contained in guideline trigger profile " + str(codes))
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
        print("For patient: "+ str(patientUUID) + " guideline entry point found: " + str(normotensive) + " " + str(g.value(URIRef(normotensive), RDFS.label)))
        print("Explanation: patient codes " + str(patientValueSAP) + " contained in guideline trigger profile ")
        scOutput = "Yes"
        entry.append(normotensive)
    if (129 > patientValueSAP > 120) and (patientValueDAP < 80):
        print("---------------------------")
        print("Triggering endpoint output:")
        print('Matched!!!')
        print("For patient: "+ str(patientUUID) + " guideline entry point found: " + str(preelevated) + " " + str(g.value(URIRef(preelevated), RDFS.label)))
        print("Explanation: patient codes " + str(patientValueSAP) + " contained in guideline trigger profile ")
        scOutput = "Yes"
        entry.append(preelevated)
    if (139 > patientValueSAP > 130) and (80 < patientValueDAP < 89):
        print("---------------------------")
        print("Triggering endpoint output:")
        print('Matched!!!')
        print("For patient: "+ str(patientUUID) + " guideline entry point found: " + str(stage1hypertension) + " " + str(g.value(URIRef(stage1hypertension), RDFS.label)))
        print("Explanation: patient codes " + str(patientValueSAP) + " contained in guideline trigger profile ")
        scOutput = "Yes"
        entry.append(stage1hypertension)
    if (patientValueSAP > 139) and (patientValueDAP > 89):
        print("---------------------------")
        print("Triggering endpoint output:")
        print('Matched!!!')
        print("For patient: "+ str(patientUUID) + " guideline entry point found: " + str(stage2hypertension) + " " + str(g.value(URIRef(stage2hypertension), RDFS.label)))
        print("Explanation: patient codes " + str(patientValueSAP) + " contained in guideline trigger profile ")
        scOutput = "Yes"
        entry.append(stage2hypertension)
    else:
        print("Triggering endpoint output:")
        print("Not matched for patient: " + str(patientUUID) )
        scOutput = "No"

    return scOutput, entry

def getTriggeringProfile(g, patientCodes, patientUUID, numberOfSharedCodes, patientValueSAP, patientValueDAP):
    codes  = ""
    #entrypointLink = ""
    for s, p, o in g.triples((None, RDFS.subClassOf, anxietyTriggerProfile)):
        ensembleOutput = ""
        print("---------------------------")
        print("Trigger rule found!")
        print(g.value(s, RDFS.label))
        print(f"{s}")

        codes = g.value(s, triggeringCodes)
        print(codes)
        entrypointLink = g.value(s, entrypoint)
        #print(entrypointLink)
        #scOutput = matchCodes(codes, entrypointLink, patientCodes, patientUUID, numberOfSharedCodes)
        scOutput, entryLink = matchBPRanges(patientValueSAP,patientValueDAP, patientUUID)
        evOutput = getEvaluatorOutput()
        print("Shared codes output: " + str(scOutput))
        print("Evaluator output: " + str(evOutput))
        if scOutput == "Yes" and evOutput == "Green":
            ensembleOutput = True
        if scOutput == "Yes" and evOutput == "Yellow":
            ensembleOutput = True
        if scOutput == "Yes" and evOutput == "Red":
            ensembleOutput = True
        if scOutput == "No" and evOutput == "Green":
            ensembleOutput = False
        if scOutput == "No" and evOutput == "Yellow":
            ensembleOutput = False
        if scOutput == "No" and evOutput == "Red":
            ensembleOutput = True

    return ensembleOutput


patientUUID = "fc8e6d65-d226-4137-b5bf-bb6705f905c4"
query = generate_reportedcondition_query(patientUUID)
result = execute_HG_query(query)
foundInHG = parseHGResults(result)
print("Found in HG: " + str(foundInHG))
numberOfSharedCodes = 1
foundInHG = ['xran8miGiv', 'sU0MCUcM0L']
if getTriggeringProfile(g, foundInHG, patientUUID, numberOfSharedCodes, 125, 77):
    print("Ensamble match!")
else:
    print("NO ensamble match!")


