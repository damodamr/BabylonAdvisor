from rdflib import Graph, RDF, RDFS
from rdflib import URIRef
from rdf_uris import(
    PROPERTY_URIS
)
from typing import Dict
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

def query_graph(query: str):
    return rdf_graph.query(query)

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


# for el in list(getAllActionLabels(rdf_graph)):
#     rows = query_graph(all_actions_query(el))
#     print(rows)
#     actions = [action_from_uri(row.x) for row in rows]
#     for a in actions:
#         print(a)


def printAll(rdf_graph):
    for el in list(getAllProcessLabels(rdf_graph)):
        rows = query_graph(all_processes_query(el))
        #print(rows)
        processes = [process_from_uri(row.x) for row in rows]
        for p in processes:
            print("----------------------------")
            faq = get_first_actions_in_process(p['uri'])
            for f in faq:
                print("Process: " + str(p['label']))
                print(" First: " + f['label'])
                furi = f['uri']

                next_actions = []
                rows = query_graph(next_action_query(furi))
                next_actions = [action_from_uri(row.o) for row in rows]
                for na in next_actions:
                    print("     Next action: " + str(na['label']) )

                    rows = query_graph(action_requirements_query(na['uri']))
                    requirements = [finding_from_uri(row.o) for row in rows]
                    for req in requirements:
                        print("             Requirement: " + req['label'])

def _graph_action_tree(action, graph, patient, hg_client):
    # Get requirements, as these will inform what color we paint the node.
    bbln_codes = bbln_codes_from_requirements(_get_action_code_requirements(action))
    age_requirement = _get_action_age_requirement(action)

    # Get fulfilled Babylon Codes from healthgraph.
    hg_codes = get_bbln_codes_for_patient(patient["id"], bbln_codes, hg_client)

    # Check if requirements are met, or not.
    bbln_codes_matched = len(hg_codes) == len(bbln_codes)
    if age_requirement is not None:
        age_requirement_met = check_age_requirement(
            dob_to_age(patient["birthDate"]), age_requirement["label"]
        )
    else:
        age_requirement_met = True

    # If all requirements are met, we paint the graph node green.
    # If some requirements are met, we paint the graph node yellow.
    # If no requirements are met, we paint the graph node red.
    if bbln_codes_matched and age_requirement_met:
        color = "green"
    elif len(hg_codes) > 0 and age_requirement_met:
        color = "yellow"
    else:
        color = "red"

    graph.node(action["label"], style="radial", fillcolor=color)

    rows = query_graph(next_action_query(action["uri"]))
    next_actions = [action_from_uri(row.o) for row in rows]
    for next_action in next_actions:
        graph.edge(action["label"], next_action["label"])
        _graph_action_tree(
            action=next_action,
            graph=graph,
            patient=patient,
            hg_client=hg_client,
        )

def _get_action_code_requirements(action):
    rows = query_graph(action_requirements_query(action["uri"]))
    return [finding_from_uri(row.o) for row in rows]


def _get_action_age_requirement(action):
    rows = query_graph(action_age_requirement_query(action["uri"]))
    # NOTE: We assume there are either 0 or 1 age requirements
    # for this prototype.
    age_requirements = [age_requirement_from_uri(row.o) for row in rows]
    return age_requirements[0] if len(age_requirements) > 0 else None

#def _tmp_dir():
    #return str(Path(app.root_path).parent / "tmp")

def showRequirements(furi):

    rows = query_graph(action_requirements_query(furi))
    requirements = [finding_from_uri(row.o) for row in rows]
    print(requirements)
    for req in requirements:
        print("Requirement: " + req['label'])


def processes_visualize(patient_uuid, process_uri):
    #patient_uuid = request.get_json().get("patient_uuid", None)
    if patient_uuid is None:
        raise ValueError("Need a Patient UUID to find action requirements")
    graph = Digraph(format="json")
    #hg_client = get_hg_client()
    patient = get_patient_info(patient_uuid, generate_service_token())
    print(patient)
    # Get process label and put as first node on graph.
    process = process_from_uri(process_uri)
    #graph.node(process["label"], style="radial", fillcolor="white")

    # Get starting actions. From these starting actions
    # recurisvely go through those actions' "next" actions until entire
    # process tree is traversed (and graphed via graphviz)
    first_actions = get_first_actions_in_process(process_uri)
    print(first_actions)
    for action in first_actions:
        graph.edge(process["label"], action["label"])
        _graph_action_tree(action=action, graph=graph, patient=patient, hg_client=hg_client)

    print("here")
    #print(graph)
    # Save graph to temporary PNG, which is then immediately returned
    # as part of the request.
    #graph_name = f"graph_{uuid4()}"
    #graph.render(directory="tmp", filename=graph_name)
    #return send_file(f"{_tmp_dir()}/{graph_name}.png", mimetype="image/png")


def printNextAction(furi):
    next_actions = []
    rows = query_graph(next_action_query(furi))
    next_actions = [action_from_uri(row.o) for row in rows]
    print(next_actions)
    for na in next_actions:
        print("     Next action: " + str(na['label']))
        print("     uri: " + str(na['uri']))

        rows = query_graph(action_requirements_query(na['uri']))
        requirements = [finding_from_uri(row.o) for row in rows]
        for req in requirements:
            print("             Requirement: " + req['label'])

#processes_visualize("fc8e6d65-d226-4137-b5bf-bb6705f905c4","http://webprotege.stanford.edu/R8Pqdnsyusj5wk5nsgTmXqR")
#printAll("rdf_graph")
# printNextAction("http://webprotege.stanford.edu/RBnpTLhXECm9IfihPoFtaJ3")
# print("------")
# printNextAction("http://webprotege.stanford.edu/R1qsXMzI0nW5FRXguTTAar")
# print("------")
#printNextAction("http://webprotege.stanford.edu/RDz31Ag7jUltg7hVmhu4yo3")
showRequirements("http://webprotege.stanford.edu/R8ipdgO78bakpvgi7d4AE6x")

