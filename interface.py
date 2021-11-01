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
#babylonCode = URIRef("http://webprotege.stanford.edu/R5ZIuf9q1yLqSWjrbrh2AH")

processes = URIRef("http://webprotege.stanford.edu/RBdZ9PjAPQbwHzyQfZFeimJ")
actions = URIRef("http://webprotege.stanford.edu/Rk3YLsMnUvjlpQFbHZaOwb")
hasRequirement = URIRef("http://webprotege.stanford.edu/RBKuVxv3Ag9NVQygDL8qwwX")
next = URIRef("http://webprotege.stanford.edu/RBX9yM6PnHMZmCut0ANkwK2")
first = URIRef("http://webprotege.stanford.edu/RCYcJMTsWRUnM4fNdRyRf4S")
snomed = URIRef("http://webprotege.stanford.edu/RCxRbA67sAZNNYGFNDdGHUe")
hasSnippet = URIRef("http://webprotege.stanford.edu/R9DtWPVELKDzTWPxZMDPCZb")
babylonCode = URIRef("http://webprotege.stanford.edu/RBF8Invk9dtsgp4wQD68WeA")

graph = graphviz.Digraph()

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

def parseHGResults(results):
    foundList = []
    found = results['data']['getMedicalRecord']['condition']
    for el in found:
        print(el)
        foundList.append(el['code']['coding'][0]['code'])
    return foundList

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

def getAllActionLabels(g):
    allActionLabels = set()
    for subj, pred, obj in g:
        #print(g.value(subj, RDFS.label))
        if g.value(subj, RDFS.subClassOf) == actions:
            #print(g.value(subj, RDFS.subClassOf))
            if str(g.value(subj, RDFS.label)) not in ['None', 'next', 'first', 'hasRequirement']:
                allActionLabels.add(str(g.value(subj, RDFS.label)))
    return allActionLabels

def getAllProcessLabels(g):
    allProcessLabels = set()
    for subj, pred, obj in g:
        #print(g.value(subj, RDFS.label))
        if g.value(subj, RDFS.subClassOf) == processes:
            #print(g.value(subj, RDFS.subClassOf))
            if str(g.value(subj, RDFS.label)) not in ['None', 'next', 'first', 'hasRequirement']:
                allProcessLabels.add(str(g.value(subj, RDFS.label)))
    return allProcessLabels

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
    RequirementsAction = g.value(action, RDFS.label)
    print("Requirements necessary for "+ str(RequirementsAction) + " action to be advised!")
    reqs = []
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


    print("-------------------------------------------------------------")
    return(reqs, codes)

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



def printAllActionsInProcess(action, allActionsInProcessList):
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
        graph.edge(str(NextAction), str(label))
        if row.o:
            printAllActionsInProcess(row.o, allActionsInProcessList)
        else:
            print("No more actions in this branch!")
            st.write("No more actions in this branch!")
            allActionsInProcessList.append("No more actions in this branch!")
    return allActionsInProcessList

def printFirstActionInProcess(process):
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
        printAllActionsInProcess(row.o, allActionsInProcessList)
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
        ('','Mo', 'Layla', 'Alex'),
        index=1
    )

    st.markdown("")

    actionList =getAllActionLabels(g)
    patient_contextAction = st.sidebar.selectbox(
        'Choose the current patient context (action)', actionList
    )

    uri = getUriFromLabel(patient_contextAction)

    reqs, codes = printRequrementsList(uri)
    if reqs:
        if patient_type == "Alex":
            patient_type = "235173f5-1866-4de6-9c53-8b82de10c347"
        query = generate_reportedcondition_query(patient_type, str(codes))
        result = execute_HG_query(query)
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
        allActionsAfterAction = printAllActionsInProcess(uri, allActionsInProcess)
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
        allActionsInProcess = printFirstActionInProcess(uri)
        st.write(allActionsInProcess)
        drawGraph()


main()