#!/usr/local/bin/python3
#coding=utf-8

import graph_tool.all as gt



## FUNCTIONS

# Function from NetworkX
def common_neighbors(u, v):
    return (w for w in u.all_neighbours() if w in v.all_neighbours() and w not in (u,v) )
    #return (w for w in G[u] if w in G[v] and w not in (u, v))
    
# Count number of common neighbors
def num_common_neighbors(u, v):
    return len(list( common_neighbors(u, v) ))



## PROCESS GRAPH

# Load data
h = gt.load_graph('search03_GraphML.graphml')
# Remove self loops
gt.remove_self_loops(h)
# Filter graph and maintain only the largest component
h = gt.GraphView(h, vfilt=gt.label_largest_component(h, directed=False))
# Copy only the filtered graph.
g = gt.Graph(h, prune=True)


# Initialise the edge weights
g.edge_properties.weight = g.new_edge_property('int')
# Set the weight of each edge equal to the number of common neighbours of the nodes associated with the edge plus one (such that the weights are strictly positive).
for e in g.edges():
    g.edge_properties.weight[e] = 1 + num_common_neighbors(e.source(), e.target())



## SAVE GRAPH

# Save graph in plain text
txt = []
txt2 = []
for e in g.edges():
    txt.append('%s %s %s' % (e.source(), e.target(), g.edge_properties.weight[e]) )
    txt2.append('%s %s' % (e.source(), e.target()) )
with open('search03_lc_cnw.txt', 'w') as txt_file:
    txt_file.write('\n'.join(txt))    
with open('search03_lc.txt', 'w') as txt2_file:
    txt2_file.write('\n'.join(txt2))
# Save Scorpus ID and internal Graph-tool ID lookup table
lookup = []
for v in g.vertices():
    lookup.append('%s %s' % (v, g.vertex_properties._graphml_vertex_id[v]) )
with open('search03_lc_cnw.txt', 'w') as lookup_file:
    lookup_file.write('\n'.join(lookup))

# Save graph in GraphML format
g.save('search03_lc_cnw.graphml')
