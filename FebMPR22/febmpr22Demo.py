import streamlit as st
import json
import graphviz as graphviz
import os
import requests
from datetime import date, datetime

from rdflib import Graph, RDF, RDFS
from rdflib import URIRef
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS

g = Graph()
g.parse("urn_webprotege_ontology_8c5fd0ff-d7ef-4e72-8e06-462eebaba042.owl")

processes = URIRef("http://webprotege.stanford.edu/RBdZ9PjAPQbwHzyQfZFeimJ")
actions = URIRef("http://webprotege.stanford.edu/Rk3YLsMnUvjlpQFbHZaOwb")
hasRequirement = URIRef("http://webprotege.stanford.edu/RBKuVxv3Ag9NVQygDL8qwwX")
hasAgeRequirement = URIRef("http://webprotege.stanford.edu/RDuXbIDxtVhZiI5TPwjwXL4")
next = URIRef("http://webprotege.stanford.edu/RBX9yM6PnHMZmCut0ANkwK2")
first = URIRef("http://webprotege.stanford.edu/RCYcJMTsWRUnM4fNdRyRf4S")
snomed = URIRef("http://webprotege.stanford.edu/RCxRbA67sAZNNYGFNDdGHUe")
hasSnippet = URIRef("http://webprotege.stanford.edu/R9DtWPVELKDzTWPxZMDPCZb")
babylonCode = URIRef("http://webprotege.stanford.edu/RBF8Invk9dtsgp4wQD68WeA")

# processes = [
# URIRef("http://webprotege.stanford.edu/R9BDbRmeRmaRfcu3q6xqeAF"), #anxiety processes
# URIRef("http://webprotege.stanford.edu/RC7ZOpCG618ia8SeemEFOcN"), #hypertension processes
# URIRef("http://webprotege.stanford.edu/RDnaUto9j5lapcFwhtld1nn"), #low back pain processes
# URIRef("http://webprotege.stanford.edu/RBdZ9PjAPQbwHzyQfZFeimJ") #physical activity processes
# ]
#
# actions = [
# URIRef("http://webprotege.stanford.edu/R9UceeCncYQqsBsZKbJG4Io"), #anxiety actions
# URIRef("http://webprotege.stanford.edu/RB5g9tutkOpMpP98LCIRsIa"), #hypertension actions
# URIRef("http://webprotege.stanford.edu/R8oq6Z2QSPkRqjckE150AZa"), #low back pain actions
# URIRef("http://webprotege.stanford.edu/Rk3YLsMnUvjlpQFbHZaOwb") #physical activity actions
# ]

tag = URIRef("http://webprotege.stanford.edu/RBTpM1xSAgAaeYGMGKoh4Kq")

graph = graphviz.Digraph()

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

#---------------------------------------------------------------------------
def getAllActionLabels(rdf_graph):
    allActionLabels = set()
    for subj, pred, obj in rdf_graph:
        if str(rdf_graph.value(subj,tag)) == "Action":
            allActionLabels.add(subj)
    return allActionLabels

def getAllProcessLabels(rdf_graph):
    allProcessLabels = set()
    for subj, pred, obj in rdf_graph:
        if str(rdf_graph.value(subj,tag)) == "Process":
            allProcessLabels.add(subj)
    return allProcessLabels

def calculate_age(born):
    born = born.split("-")
    born = date(int(born[0]),int(born[1]),int(born[2]))
    today = date.today()
    print(today)
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def getUriFromLabel(label):
    uri = "None"
    for subj, pred, obj in g:
        #print(g.value(subj, RDFS.label))
        if str(g.value(subj, RDFS.label)) == str(label):
            uri = subj
    return uri

def getBabylonCodeFromUri(uri):
    code = g.value(uri,babylonCode)
    return code

# def getAllActionLabels(g):
#     allActionLabels = set()
#     for subj, pred, obj in g:
#         #print(g.value(subj, RDFS.label))
#         if g.value(subj, RDFS.subClassOf) == actions:
#             #print(g.value(subj, RDFS.subClassOf))
#             if str(g.value(subj, RDFS.label)) not in ['None', 'next', 'first', 'hasRequirement']:
#                 allActionLabels.add(str(g.value(subj, RDFS.label)))
#     return allActionLabels
#
# def getAllProcessLabels(g):
#     allProcessLabels = set()
#     for subj, pred, obj in g:
#         #print(g.value(subj, RDFS.label))
#         if g.value(subj, RDFS.subClassOf) == processes:
#             #print(g.value(subj, RDFS.subClassOf))
#             if str(g.value(subj, RDFS.label)) not in ['None', 'next', 'first', 'hasRequirement']:
#                 allProcessLabels.add(str(g.value(subj, RDFS.label)))
#     return allProcessLabels

def drawGraph():
    st.graphviz_chart(graph)

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
    hasAgeRequirementObject = g.query("""
        SELECT ?x ?o
            WHERE { 
            <"""+str(action)+"""> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?x .
            ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction> .
            ?x <http://www.w3.org/2002/07/owl#onProperty> <""" +str(hasAgeRequirement) +"""> .
            ?x <http://www.w3.org/2002/07/owl#someValuesFrom> ?o .
            }
    """)
    RequirementsAction = g.value(action, RDFS.label)
    print("Requirements necessary for "+ str(RequirementsAction) + " action to be advised!")
    reqs = []
    reqsBD = []
    codes = ""
    system = "https://bbl.health"
    for row in hasRequirementObject:
        print(f"{row.o}")
        print(g.value(row.o, RDFS.label))
        reqs.append(str(g.value(row.o, RDFS.label)))
        co = str(g.value(row.o, babylonCode))
        print(co)
        codeString = "{system:\""+system+"\", code:\""+str(co).rstrip()+"\"}, "
        codes = codes + codeString

    for row in hasAgeRequirementObject:
        print(f"{row.o}")
        print(g.value(row.o, RDFS.label))
        reqsBD.append(str(g.value(row.o, RDFS.label)))

    print("-------------------------------------------------------------")
    return(reqs, codes, reqsBD)

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
    # hasAgeRequirementObject = g.query("""
    #     SELECT ?x ?o
    #         WHERE {
    #         <"""+str(action)+"""> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?x .
    #         ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction> .
    #         ?x <http://www.w3.org/2002/07/owl#onProperty> <""" +str(hasAgeRequirement) +"""> .
    #         ?x <http://www.w3.org/2002/07/owl#someValuesFrom> ?o .
    #         }
    # """)
    RequirementsAction = g.value(action, RDFS.label)
    #print("Requirements necessary for "+ RequirementsAction + " action to be advised!")
    reqs = []
    reqsBD = []
    for row in hasRequirementObject:
        #print(f"{row.o}")
        #print(g.value(row.o, RDFS.label))
        reqs.append(str(g.value(row.o, RDFS.label)))

    # for row in hasAgeRequirementObject:
    #     #print(f"{row.o}")
    #     #print(g.value(row.o, RDFS.label))
    #     reqsBD.append(str(g.value(row.o, RDFS.label)))


    #print("-------------------------------------------------------------")
    return(reqs)

def checkRequirements(patient_contextAction, foundInHG):
    uri = getUriFromLabel(patient_contextAction)
    reqs, codes, reqsBD = printRequrementsList(uri)

    reqListYes = []
    reqListNo = []

    for el in reqs:
        uriTemp = getUriFromLabel(el)
        el2 = str(getBabylonCodeFromUri(uriTemp))
        if el2 in foundInHG:
            reqListYes.append(el2)
        else:
            reqListNo.append(el2)
    return reqListYes, reqListNo, reqsBD

def printNextAction(action):
    # next action
    bestActionList = []
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
    print("Next action following the "+ str(NextAction) + " action is: ")
    for row in hasNextObject:
        print(f"{row.o}")
        print(g.value(row.o, RDFS.label))
        bestActionList.append(f"{row.o}")
        bestActionList.append(g.value(row.o, RDFS.label))
    print("-------------------------------------------------------------")
    return bestActionList

def ageCheck(current_age, formula):
    agematch = "no age match"
    if 'X>18' in formula:
        if current_age > 18:
            print("X>18")
            agematch =  "age match"
    if '64>X>18' in formula:
        if 64 > current_age > 18:
            print("64>X>18")
            agematch = "age match"
    if 'X<18' in formula:
        if current_age < 18:
            print("X<18")
            agematch = "age match"
    return agematch

def printAllActionsInProcess(action, allActionsInProcessList, patient_type, foundInHG):
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
        print("Next "+ str(labelType) +" following the " + str(NextAction) + " action is: " + f"{row.o}" + " - " + str(label))
        allActionsInProcessList.append("Next "+ str(labelType) +" following the " + str(NextAction) + " action is: " + f"{row.o}" + " - " + str(label))
        print("     Action extended info: " + str(snippet))
        print("     Action requirements: " + str(requirements))

        yesList, noList, ageReq = checkRequirements(str(NextAction), foundInHG)
        st.write(foundInHG[0])
        st.write("Yes: " + str(yesList))
        st.write("No: " + str(noList))

        agepass = ageCheck(int(foundInHG[0]), ageReq)
        st.write("Age: " + str(ageReq) + "pass: " + agepass)
        if len(noList) > 0 and agepass == "no age match":
            graph.node(str(NextAction), fillcolor = "#ff0000",  style="radial")
        else:
            graph.node(str(NextAction), fillcolor="#ffafa8", style="radial")
        graph.edge(str(NextAction), str(label))

        if row.o:
            printAllActionsInProcess(row.o, allActionsInProcessList, patient_type, foundInHG)
        else:
            print("No more actions in this branch!")
            st.write("No more actions in this branch!")
            allActionsInProcessList.append("No more actions in this branch!")
    return allActionsInProcessList

def printFirstActionInProcess(process, patient_type, foundInHG):
    #all actions in a process
    allActionsInProcessList = []
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
    print("First action in "+ str(processLabel) + " process is: ")
    for row in hasFirstAction:
        print(f"{row.o}")
        print(g.value(row.o, RDFS.label))
        allActionsInProcessList.append("First action in "+ str(processLabel) + " process is: "+str(g.value(row.o, RDFS.label)))
        graph.edge(str(processLabel), str(g.value(row.o, RDFS.label)))

        #allActionsInProcessList.append(g.value(row.o, RDFS.label))
        printAllActionsInProcess(row.o, allActionsInProcessList, patient_type, foundInHG)
    print("-------------------------------------------------------------")
    return allActionsInProcessList

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


def show(reqs, patient_contextAction, patient_type, foundInHG):
    st.write(
        """
        ## ✅ Requirements list for: """ + patient_contextAction + """ for: """ + patient_type +
        """
        You must confirm that following requirements are either true of false! 
        """
    )
    reqList = []
    for el in reqs:
        uriTemp = getUriFromLabel(el)
        el2 = str(getBabylonCodeFromUri(uriTemp))
        if el2 in foundInHG:
            reqEl = {"description": el, "done": True}
            reqList.append(reqEl)
        else:
            reqEl = {"description": el, "done": False}
            reqList.append(reqEl)
    st.write(reqList)
    # Define initial state.
    # if "todos" not in st.session_state:
    #     st.session_state.todos = [
    #         {"description": "Play some Tic Tac Toe", "done": True},
    #         {
    #             "description": "Read the [blog post about session state](https://blog.streamlit.io/session-state-for-streamlit/)",
    #             "done": False,
    #         },
    #     ]

    #if "todos" not in st.session_state:
    todos = reqList

    # Define callback when text_input changed.
    def new_todo_changed():
        #if st.session_state.new_todo:
        todos.append(
            {
                "description": st.new_todo,
                "done": False,
            }
        )
    write_requirement_list(todos, patient_contextAction)

def write_requirement_list(todos, patient_contextAction):
    "Display the todo list (mostly layout stuff, no state)."
    st.write("")
    all_done = True
    for i, todo in enumerate(todos):
        col1, col2, _ = st.columns([0.05, 0.8, 0.15])
        done = col1.checkbox("", todo["done"], key=str(i)+patient_contextAction)
        if done:
            format_str = (
                '<span style="color: grey; text-decoration: line-through;">{}</span>'
            )
        else:
            format_str = "{}"
            all_done = False
        col2.markdown(
            format_str.format(todo["description"]),
            unsafe_allow_html=True,
        )

    if all_done:
        st.success("Since all requirements have been checked we can recommend proceeding with the action! 🎈")



def main():
    """Run this function to display the Streamlit app"""

    st.sidebar.title('Babylon Advisor')
    st.sidebar.markdown("""Use the dropdown to select the guideline and patient data""")
    st.markdown("")
    # guideline_type = st.sidebar.selectbox(
    #     'Select the guideline',
    #     ('','Blood pressure measurement', 'more to come...'),
    #     index=0
    # )

    patient_type = st.sidebar.selectbox(
        'Load patient data from HealthGraph',
        ('','Mo', 'Layla', 'Alex', 'e744b1bc-3a97-4fd1-bf32-508c70345c32', 'c77c14a5-e31d-4686-9500-cec43c25cb6f', '0421b0f4-0adb-40ec-88b7-ff3454bb6abc', 'fcb395ba-758f-4b64-9f10-5c55fcfbf5ac'),
        index=1
    )

    st.markdown("")

    actionList =getAllActionLabels(g)
    patient_contextAction = st.sidebar.selectbox(
        'Choose the current patient context (action)', actionList
    )

    uri = getUriFromLabel(patient_contextAction)

    reqs, codes, reqsBD = printRequrementsList(uri)
    if reqs:
        if patient_type == "Alex":
            patient_type = "235173f5-1866-4de6-9c53-8b82de10c347"
        query = generate_reportedcondition_query(patient_type)
        result = execute_HG_query(query)
        birthDateQuery = generate_patient_query(patient_type)
        birthDate = execute_HG_query(birthDateQuery)
        foundInHG = parseHGResults(result)
        if patient_type == "235173f5-1866-4de6-9c53-8b82de10c347":
            patient_type = "Alex"
        show(reqs,patient_contextAction, patient_type, foundInHG)
        my_expander = st.expander(label='See the query sent to HealthGraph')
        with my_expander:
            query
        st.markdown("")
        #st.write(result)
        my_expander = st.expander(label='See the HealthGraph output')
        with my_expander:
            result


    if st.sidebar.button('Show next best action for selected action for: ' + patient_type):
        nextBestAction = printNextAction(uri)
        st.write(nextBestAction)
        # for i in range(0,len(nextBestAction)):
        #     for x in input[i::2]:
        #         uri = nextBestAction[x]
        #         reqs = printRequrementsList(uri)
        #         if reqs:
        #             show(reqs, nextBestAction[x+1], patient_type)


    if st.sidebar.button('Show all possible actions after current action for: ' + patient_type):
        allActionsInProcess = []
        allActionsAfterAction = printAllActionsInProcess(uri, allActionsInProcess, patient_type, foundInHG)
        st.write(allActionsAfterAction)
        text_contents = str(allActionsAfterAction)
        st.download_button('Download suggested path', text_contents)
        drawGraph()

    st.sidebar.markdown("---")

    processList = getAllProcessLabels(g)
    patient_contextProcess = st.sidebar.selectbox(
        'Choose the current patient context (process)', processList
    )

    uri = getUriFromLabel(patient_contextProcess)

    if st.sidebar.button('Show all actions in a process'):
        if patient_type == "Alex":
            patient_type = "235173f5-1866-4de6-9c53-8b82de10c347"
        query = generate_reportedcondition_query(patient_type)
        birthDateQuery = generate_patient_query(patient_type)
        result = execute_HG_query(query)
        birthDate = execute_HG_query(birthDateQuery)
        foundInHG = parseHGResults(result)
        allActionsInProcess = printFirstActionInProcess(uri, patient_type,foundInHG)
        st.write(allActionsInProcess)
        drawGraph()


main()