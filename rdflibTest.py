from rdflib import Graph, RDF, RDFS
from rdflib import URIRef
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS
import os
import requests
import json

from gql import gql, Client
#from gql.transport.aiohttp import AIOHTTPTransport

from graphqlclient import GraphQLClient

g = Graph()
g.parse("urn_webprotege_ontology_27ee4c66-215c-4563-b64a-83d728653396.owl")

#for s, p, o in g.triples((None,  RDF.type, None)):
    #print(f"{s}   =    {g.value(s, RDFS.label)} is a {o}")
#name = g.value(action, RDFS.label)
#print(name)
#mbox = g.value(hasRequirement, RDFS.label)
#print(mbox)

processes = URIRef("http://webprotege.stanford.edu/R9rhFHtwjxynjFMQdRdjICi")
actions = URIRef("http://webprotege.stanford.edu/RBZhgoK8Qeirs0YZu2ad2Kh")
action1 = URIRef("http://webprotege.stanford.edu/R9kYwMAmH3FSMhlDOlEeLOs") #checkup while standing
action2 = URIRef("http://webprotege.stanford.edu/RCYsCDkpJ7XlNNgN93swd6C") #review medication and consider referral to specialist
action3 = URIRef("http://webprotege.stanford.edu/RDpsnjoBFoSXZH9EhPMvMPh") #use automated device
action4 = URIRef("http://webprotege.stanford.edu/RY2zFMWhCpW2dBbQ9cQwlw")#checkup while lying down
hasRequirement = URIRef("http://webprotege.stanford.edu/RC7Wq1yEcljB1N9YPUStQZg")
next = URIRef("http://webprotege.stanford.edu/R7rMKTUfG8K7ryhfq0xDPyk")
first = URIRef("http://webprotege.stanford.edu/RZElLi8R8mkRSGGDLlahA9")
process = URIRef("http://webprotege.stanford.edu/R7WEa3ShvTpTuqsAhGYqvHT")
hasSnippet = URIRef("http://webprotege.stanford.edu/RDM9hbbAS4IdgwRvUbCKiMa")
snomed = URIRef("http://webprotege.stanford.edu/R9MPy28obbWUhRYlvQ03Y4e")
babylonCode = URIRef("http://webprotege.stanford.edu/R5ZIuf9q1yLqSWjrbrh2AH")

def generate_service_token():
    url = 'https://services-uk.dev.babylontech.co.uk/ai-auth/v1/internal'
    header = {'Content-Type': 'application/json'}

    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    client_id = "1M1m7EKIyUg6e3xdDWJQEFBt4a3F3uyE"
    client_secret = "42drt7aEQTfWLnThhsJ5woWJmYkFJwN0bmKXz38rKjGmseW3d31aavY4q7ZLMiSN"
    print(client_id)
    print(client_secret)
    data = {'client_id': client_id, 'client_secret': client_secret}
    r = requests.post(url, headers=header, data=json.dumps(data))
    print(r)
    return json.loads(r.text)['access_token']


def execute_HG_query(query):
    token = generate_service_token()
    url = 'https://services-uk.dev.babylontech.co.uk/chr/graphql'
    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(query))
    return json.loads(r.text)


def generate_reportedcondition_query(patient_uuid, codes):
    query_string = """query {
        getMedicalRecord(member_uuid: \"""" + patient_uuid + """\") {
          condition(search: {
            code: {
              oneOf: 
              ["""+codes+"""]  
            }
          }) {
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





def getUriFromLabel(label):
    for subj, pred, obj in g:
        #print(g.value(subj, RDFS.label))
        if str(g.value(subj, RDFS.label)) == str(label):
            uri = subj
    return uri

def getAllLabels(g):
    allLabels = []
    for subj, pred, obj in g:
        #print(g.value(subj, RDFS.label))
        if g.value(subj, RDFS.subClassOf) == actions or g.value(subj, RDFS.subClassOf) == processes:
            print(g.value(subj, RDFS.subClassOf))
            if str(g.value(subj, RDFS.label)) not in ['None', 'next', 'first', 'hasRequirement']:
                allLabels.append(str(g.value(subj, RDFS.label)))
    return allLabels

def printRequrementsList(action):
    # hasRequirements list
    hasRequirementObject = g.query("""
        SELECT ?x ?o
            WHERE { 
            <"""+str(action)+"""> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?x .
            ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction> .
            ?x <http://www.w3.org/2002/07/owl#onProperty> <""" +str(hasRequirement) +"""> .
            ?x <http://www.w3.org/2002/07/owl#someValuesFrom> ?o .
            }
    """)
    RequirementsAction = g.value(action, RDFS.label)
    print("Requirements necessary for "+ RequirementsAction + " action to be advised!")
    reqs = []
    codes = ""
    system = "https://bbl.health"
    for row in hasRequirementObject:
        print(f"{row.o}")
        print(g.value(row.o, RDFS.label))
        co = str(g.value(row.o, babylonCode))
        print(co)
        reqs.append(str(g.value(row.o, RDFS.label)))
        codeString = "{system:\""+system+"\", code:\""+str(co).rstrip()+"\"}, "
        codes = codes + codeString

    print(str(codes))
    print("-------------------------------------------------------------")
    return(reqs,str(codes))

def requrementsList(action):
    # hasRequirements list
    hasRequirementObject = g.query("""
        SELECT ?x ?o
            WHERE { 
            <"""+str(action)+"""> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?x .
            ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction> .
            ?x <http://www.w3.org/2002/07/owl#onProperty> <""" +str(hasRequirement) +"""> .
            ?x <http://www.w3.org/2002/07/owl#someValuesFrom> ?o .
            }
    """)
    RequirementsAction = g.value(action, RDFS.label)
    #print("Requirements necessary for "+ RequirementsAction + " action to be advised!")
    reqs = []
    for row in hasRequirementObject:
        #print(f"{row.o}")
        #print(g.value(row.o, RDFS.label))
        reqs.append(str(g.value(row.o, RDFS.label)))

    #print("-------------------------------------------------------------")
    return(reqs)

def printNextAction(action):
    # next action
    hasNextObject = g.query("""
        SELECT ?x ?o
            WHERE { 
            <"""+str(action)+"""> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?x .
            ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction> .
            ?x <http://www.w3.org/2002/07/owl#onProperty> <""" +str(next) +"""> .
            ?x <http://www.w3.org/2002/07/owl#someValuesFrom> ?o .
            }
    """)
    NextAction = g.value(action, RDFS.label)
    print("Next action following the "+ NextAction + " action is: ")
    for row in hasNextObject:
         print(f"{row.o}")
         print(g.value(row.o, RDFS.label))
    print("-------------------------------------------------------------")

def printAllActionsInProcess(action):
    # all next actions in process
    hasNextObject = g.query("""
        SELECT ?x ?o
            WHERE { 
            <"""+str(action)+"""> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?x .
            ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction> .
            ?x <http://www.w3.org/2002/07/owl#onProperty> <""" +str(next) +"""> .
            ?x <http://www.w3.org/2002/07/owl#someValuesFrom> ?o .
            }
    """)
    NextAction = g.value(action, RDFS.label)
    for row in hasNextObject:
        label = g.value(row.o, RDFS.label)
        type = g.value(row.o, RDFS.subClassOf)
        labelType = g.value(type, RDFS.label)
        snippet = g.value(row.o, hasSnippet)
        code = g.value(row.o, snomed)
        requirements = requrementsList(row.o)
        print("Next "+ labelType +" following the " + NextAction + " action is: " + f"{row.o}" + " - " + label)
        #print("     Action extended info: " + str(snippet))
        #print("     Action requirements: " + str(requirements))
        if row.o:
            printAllActionsInProcess(row.o)
        else:
            print("No more actions in this branch!")

def printFirstActionInProcess(process):
    #all actions in a process
    hasFirstAction = g.query("""
        SELECT ?x ?o
            WHERE { 
            <"""+str(process)+"""> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?x .
            ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction> .
            ?x <http://www.w3.org/2002/07/owl#onProperty> <""" +str(first) +"""> .
            ?x <http://www.w3.org/2002/07/owl#someValuesFrom> ?o .
            }
    """)
    processLabel = g.value(process, RDFS.label)
    print("First action in "+ processLabel + " process is: ")
    for row in hasFirstAction:
        print(f"{row.o}")
        print(g.value(row.o, RDFS.label))
        printAllActionsInProcess(row.o)
    print("-------------------------------------------------------------")

def printNextProcess(process):
    # next action
    hasNextObject = g.query("""
        SELECT ?x ?o
            WHERE { 
            <"""+str(process)+"""> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?x .
            ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction> .
            ?x <http://www.w3.org/2002/07/owl#onProperty> <""" +str(next) +"""> .
            ?x <http://www.w3.org/2002/07/owl#someValuesFrom> ?o .
            }
    """)
    NextAction = g.value(process, RDFS.label)
    print("Next process following the "+ NextAction + " process is: ")
    for row in hasNextObject:
         print(f"{row.o}")
         print(g.value(row.o, RDFS.label))
    print("-------------------------------------------------------------")

def printActionInfo(action):
    label = str(g.value(action, RDFS.label))
    requirements = printRequrementsList(action)
    snippet = g.value(action, hasSnippet)
    code = g.value(action, snomed)
    return (label, requirements, snippet, code)


#printRequrementsList(action1)
#printNextAction(action1)
#printFirstActionInProcess(process)
#printAllActionsInProcess(action3)
#printNextProcess(process)
#infos = printActionInfo(action2)
#for el in infos:
    #print(el)
    
#print(getUriFromLabel("checkup while standing"))
#queryHealthGraph2()
#hg()

#print(getAllLabels(g))
reqs, codes = printRequrementsList(action4)
query = generate_reportedcondition_query("235173f5-1866-4de6-9c53-8b82de10c347", str(codes))
result = execute_HG_query(query)
print(result)