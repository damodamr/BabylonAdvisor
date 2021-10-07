from rdflib import Graph, RDF, RDFS
from rdflib import URIRef
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS

g = Graph()
g.parse("urn_webprotege_ontology_27ee4c66-215c-4563-b64a-83d728653396.owl")

#for s, p, o in g.triples((None,  RDF.type, None)):
    #print(f"{s}   =    {g.value(s, RDFS.label)} is a {o}")
#name = g.value(action, RDFS.label)
#print(name)
#mbox = g.value(hasRequirement, RDFS.label)
#print(mbox)

action1 = URIRef("http://webprotege.stanford.edu/R9kYwMAmH3FSMhlDOlEeLOs") #checkup while standing
action2 = URIRef("http://webprotege.stanford.edu/RCYsCDkpJ7XlNNgN93swd6C") #review medication and consider referral to specialist
hasRequirement = URIRef("http://webprotege.stanford.edu/RC7Wq1yEcljB1N9YPUStQZg")
next = URIRef("http://webprotege.stanford.edu/R7rMKTUfG8K7ryhfq0xDPyk")
first = URIRef("http://webprotege.stanford.edu/RZElLi8R8mkRSGGDLlahA9")
process = URIRef("http://webprotege.stanford.edu/R7WEa3ShvTpTuqsAhGYqvHT")
hasSnippet = URIRef("http://webprotege.stanford.edu/RDM9hbbAS4IdgwRvUbCKiMa")
snomed = URIRef("http://webprotege.stanford.edu/R9MPy28obbWUhRYlvQ03Y4e")

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
    for row in hasRequirementObject:
        print(f"{row.o}")
        print(g.value(row.o, RDFS.label))
        reqs.append(str(g.value(row.o, RDFS.label)))

    print("-------------------------------------------------------------")
    return(reqs)

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
        print("     Action extended info: " + str(snippet))
        print("     Action requirements: " + str(requirements))
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


printRequrementsList(action1)
#printNextAction(action1)
printFirstActionInProcess(process)
#printNextProcess(process)
#infos = printActionInfo(action2)
#for el in infos:
    #print(el)