from rdflib import Graph
from rdflib import URIRef
from rdflib.namespace import RDFS

g = Graph()
g.parse("urn_webprotege_ontology_8c5fd0ff-d7ef-4e72-8e06-462eebaba042.owl")#lifestyle

anxietyTriggerProfile = URIRef("http://webprotege.stanford.edu/RCm70q8zZyZruQdPb5TK3Ik")
hypertensionTriggeringProfile = URIRef("http://webprotege.stanford.edu/R9vLo3VL37VAaOxqnqX62si")
lowbackpainTriggeringProfile = URIRef("http://webprotege.stanford.edu/R9vEODY7jVH1IZQWl1sAKGl")
triggeringRangesProperty = URIRef("http://webprotege.stanford.edu/R5UVQTXdirkwKclfJoxuSx")
triggeringCodesProperty = URIRef("http://webprotege.stanford.edu/RDpC9Z8hJrtw8hQxEkEs9vz")
evaluatorExpressionProperty = URIRef("http://webprotege.stanford.edu/RCvPUrBTx0JEvyAgo2Xf9Yh")
entrypointProperty = URIRef("http://webprotege.stanford.edu/Ra6xj5iTzHitouSDcQ0qPj")
babylonCodeProperty = URIRef("http://webprotege.stanford.edu/RBF8Invk9dtsgp4wQD68WeA")

def getTriggeringProfile(g, TriggeringProfile):

    for s, p, o in g.triples((None, RDFS.subClassOf, TriggeringProfile)):
        print("---------------------------")
        print(g.value(s, RDFS.label))
        print(f"{s}")
        for ss, pp, oo in g.triples((s, triggeringRangesProperty, None )):
            print(g.value(oo, RDFS.label))
            print("Range formula that goes into evaluator:")
            print("       " + str(g.value(oo, evaluatorExpressionProperty)))
        for ss, pp, oo in g.triples((s, triggeringCodesProperty, None )):
            print(g.value(oo, RDFS.label))
            print("Code formula that goes into evaluator:")
            print('REP_COND("' + str(g.value(oo, babylonCodeProperty)) + '")=TRUE')
        for ss, pp, oo in g.triples((s, entrypointProperty, None )):
            print(g.value(oo, RDFS.label))

getTriggeringProfile(g, hypertensionTriggeringProfile)

# triggeringProfiles = [hypertensionTriggeringProfile, anxietyTriggerProfile, lowbackpainTriggeringProfile]
# for el in triggeringProfiles:
#     getTriggeringProfile(g, el)


