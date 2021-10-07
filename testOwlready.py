import kglab

kg = kglab.KnowledgeGraph()
kg.load_rdf("/Users/damir.juric/Downloads/advisor-ontologies-owl-REVISION-HEAD/urn_webprotege_ontology_27ee4c66-215c-4563-b64a-83d728653396.owl", format="xml")

measure = kglab.Measure()
measure.measure_graph(kg)

print("edges: {}\n".format(measure.get_edge_count()))
print("nodes: {}\n".format(measure.get_node_count()))

ttl = kg.save_rdf_text()
print(ttl)



