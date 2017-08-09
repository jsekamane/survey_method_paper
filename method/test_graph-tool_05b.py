#!/usr/local/bin/python3
#coding=utf-8

import graph_tool.all as gt

# Load data
h = gt.load_graph('search03_lc_cnw.graphml')
#print(h)
# Remove directions
h.set_directed(False)
#print(h)

# Save undirected graph in GraphML format
h.save('search03_lc_cnw_ud.graphml')
