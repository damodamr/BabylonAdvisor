from anytree import Node, RenderTree
chkpls = Node("chkpls")
uadomc = Node("uadomc", parent=chkpls)
umc = Node("umc", parent=chkpls)
cwld = Node("cwld", parent=uadomc)
cwld = Node("cwld", parent=umc)
cws = Node("cws", parent=cwld)
rmacrts = Node("rmacrts", parent=cws)

#print(chkpls)
#print(rmacrts)


"chkpls", "uadomc/umc", "cwld", "cws", "rmacrts"

import networkx as nx
G = nx.Graph()

G.add_edge('chkpls', 'uadomc')
G.add_edge('chkpls', 'umc')
G.add_edge('uadomc', 'cwld')
G.add_edge('umc', 'cwld')
G.add_edge('cwld', 'cws')
G.add_edge('cws', 'rmacrts')

print("Nodes in G: ", G.nodes(data=True))
print("Edges in G: ", G.edges(data=True))
print(nx.complete_graph(G))

