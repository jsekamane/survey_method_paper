#!/usr/local/bin/python3
#coding=utf-8

import igraph
import louvain
#import matplotlib.pyplot as plt
import numpy as np
import pickle

# Option to ignore warning when divide by zero
#np.seterr(divide='ignore', invalid='ignore')

def sqrt_comm_size(partion):
    s = 0
    for community in partion:
        s = len(community)**2
    return s

def hhi(partion):
    h = 0
    n = 0
    for community in partion:
        l = len(community)
        h += l**2
        n += l
    return h/(n**2)
 
def save_modules(filename, G, partition):  
    csv = ['"ID", "Module", "z"']
    for community_i, community in enumerate(partition):
        for node in community:
            csv.append( '"%s", %s, %s' % (G.vs[node]['id'], community_i, G.vs[node]['z']) )

    with open(filename, 'w') as module_file:
        module_file.write('\n'.join(csv))    
    
#def plot_graph(G, file, partition):
#  igraph.plot(G, target=file, vertex_color=partition.membership,
#        mark_groups=zip(map(list, partition.community.values()), 
#                        partition.community.keys()),
#        vertex_frame_width=0,
#        palette=igraph.RainbowPalette(len(partition.community)))


fd = igraph.read('search03_lc_cnw_f1.graphml')
#u = igraph.read('search03_lc_cnw_ud.graphml')
print('\n')
print(fd.summary())
#print('\n')
#print(u.summary())

#print('\n')
#print('Is d directed? %s ' % d.is_directed() )
#print('Is u directed? %s ' % u.is_directed() )

#print('Is d weigthed? %s ' % d.is_weighted() )
#print('Is u weigthed? %s ' % u.is_weighted() )


print('\n ----- METHOD: MODULARITY -----')
#d_mod = louvain.find_partition(d, method='Modularity') #method='RBConfiguration', resolution_parameter=0.1);
#u_mod = louvain.find_partition(u, method='Modularity') #method='RBConfiguration', resolution_parameter=0.1);
fdw_mod = louvain.find_partition(fd, method='Modularity', weight='weight') #method='RBConfiguration', resolution_parameter=0.1);
#uw_mod = louvain.find_partition(u, method='Modularity', weight='weight') #method='RBConfiguration', resolution_parameter=0.1);

#d_mod.quality_sig = louvain.quality(d, d_mod, method='Significance');
#u_mod.quality_sig = louvain.quality(u, u_mod, method='Significance');


#print('\n\t\t Directed \t Undirected ')
#print('MODULARITY \nUnweighted \t %.4f \t %.4f \nWeighted \t %.4f \t %.4f' % (d_mod.modularity, u_mod.modularity, dw_mod.modularity, uw_mod.modularity) )
#print('\nSIGNIFICANCE \nUnweighted \t %.4f \t %.4f \nWeighted \t - \t\t -' % (d_mod.quality_sig, u_mod.quality_sig) )
#print('\nLENGTH \nUnweighted \t %s \t\t %s \nWeighted \t %s \t\t %s' % (len(d_mod), len(u_mod), len(dw_mod), len(uw_mod)) )
#print('\nHERFINDAHL INDEX \nUnweighted \t %.4f \t %.4f \nWeighted \t %.4f \t %.4f' % (hhi(d_mod), hhi(u_mod), hhi(dw_mod), hhi(uw_mod)) )
#print('\nINTERNAL EDGES \nUnweighted \t %s \t\t %s \nWeighted \t %.f \t\t %.f' % (louvain.total_internal_edges(d_mod), louvain.total_internal_edges(u_mod), louvain.total_internal_edges(dw_mod, weight='weight'), louvain.total_internal_edges(uw_mod, weight='weight')) )
#print('\n')

print('MODULARITY %.4f \t LENGTH %s \t HERFINDAHL INDEX %.4f \t INTERNAL EDGES %s' % (fdw_mod.modularity, len(fdw_mod), hhi(fdw_mod), louvain.total_internal_edges(fdw_mod, weight='weight')) )

#print('\n ----- METHOD: SIGNIFICANCE -----')
#d_sig = louvain.find_partition(d, method='Significance');
#u_sig = louvain.find_partition(u, method='Significance');

#d_sig.quality_mod = louvain.quality(d, d_sig, method='Modularity');
#u_sig.quality_mod = louvain.quality(u, u_sig, method='Modularity');

#print('\n\t\t Directed \t Undirected ')
#print('MODULARITY \nUnweighted \t %.4f \t %.4f' % (d_sig.modularity, u_sig.modularity) )
#print('\nSIGNIFICANCE \nUnweighted \t %.4f \t %.4f' % (d_sig.quality, u_sig.quality) )
#print('\nLENGTH \nUnweighted \t %s \t\t %s' % (len(d_sig), len(u_sig)) )
#print('\nHERFINDAHL INDEX \nUnweighted \t %.4f \t %.4f' % (hhi(d_sig), hhi(u_sig)) )
#print('\nINTERNAL EDGES \nUnweighted \t %s \t\t %s' % (louvain.total_internal_edges(d_sig), louvain.total_internal_edges(u_sig)) )
#print('\n')

#d_mod1 = louvain.find_partition(d, method='Modularity', consider_comms=4) #method='RBConfiguration', resolution_parameter=0.1);
#d_mod2 = louvain.find_partition(d, method='Modularity', consider_comms=4) #method='RBConfiguration', resolution_parameter=0.1);
#d_mod3 = louvain.find_partition(d, method='Modularity', consider_comms=4) #method='RBConfiguration', resolution_parameter=0.1);
#print('Checking to see if `consider_comms=4` (RAND_NEIGH_COMM) works as advertised; %.4f, %.4f, %.4f,' % (d_mod1.modularity, d_mod2.modularity, d_mod3.modularity) )



## Add graph attributes (community, z-score, participation coeffecient)

def z_score(degree, partition):
    # Both 'degree' and 'partition' are matricies with size m x n, 
    # where m is number of communities/modules and n is the number of nodes.
    # Returns an array of length m, with the z-score for each node (for its respective community)
    z = np.sum( (degree - np.mean(degree, axis=0))/np.std(degree, axis=0) * partition, axis=1)
    return z

def participation(degree, num_modules):
    # The 'degree' matrix has size m x n, where m is number of communities/modules and n is the number of nodes.
    # Returns an array of length m, with the participation coeffecient for each node.
    k = np.tile( np.sum(degree, axis=1), (num_modules,1) ).transpose()
    p = 1 - np.sum( np.divide(degree,k)**2, axis=1) 
    return p

## Set the community of each node        
def set_modules(G, partition):
    print('Set the community and degree')
    
    print('Calculate the module degree')
    # Get adjacency matrix
    a = G.get_adjacency()
    adj = np.array(a.data) ##np.save('d_adjacency.npy', adj)
    s = adj.shape
    # Undirected adjacency matrix
    adj_u = np.maximum(adj, adj.transpose())
    
    # Initial with empty matricies
    shape = (s[1], len(partition))
    partition_matrix = np.zeros(shape, dtype=bool)
    module_degree = np.zeros(shape, dtype=int)
    #module_degree_in = np.empty(shape, dtype=int)
    #module_degree_out = np.empty(shape, dtype=int)
    
    # For each community/module in partition calculate the module degree for each note
    for community_i, community in enumerate(partition):
        print('\t... community %s' % community_i)
        
        # Matrix (colomns are communities and rows are nodes). Cell takes value 1 if node in community, zero otherwise.
        partition_matrix[community, community_i] = 1
        # Matrix of same size as adjacency matrix, but where columns corresponding to nodes in community is one (zero otherwise) 
        c = np.zeros(s, dtype=bool)
        c[:,community] = np.ones( (s[1], len(community)) )
        
        # Consider current community (multiply community matrix and adjacency matrix), and sum to create array with value for each node.
        module_degree[:, community_i] = np.sum( np.multiply( adj_u, c ), axis=1)
        #module_degree_in[:, community_i] = np.sum( np.multiply( adj, c ), axis=1)
        #module_degree_out[:, community_i] = np.sum( np.multiply( adj, c.transpose() ), axis=0) #.transpose()
    
    print('Calculate the z-score and participation coeffecient')
    z = z_score(module_degree, partition_matrix)
    p = participation(module_degree, len(partition))
    #z_in = z_score(module_degree_in, partition_matrix)
    #p_in = participation(module_degree_in, len(partition))
    #z_out = z_score(module_degree_out, partition_matrix)
    #p_out = participation(module_degree_out, len(partition))

    print('Set attribute for community and degree')
    for community_i, community in enumerate(partition):
        for node in community:
            G.vs[node]['community'] = '%s' % community_i
            #G.vs[node]['module_degree_in'] = module_degree_in[node,:]
            #G.vs[node]['module_degree_out'] = module_degree_out[node,:]
            G.vs[node]['z'] = z[node]
            G.vs[node]['p'] = p[node]
            #G.vs[node]['z_in'] = z_in[node]
            #G.vs[node]['p_in'] = p_in[node]
            #G.vs[node]['z_out'] = z_out[node]
            #G.vs[node]['p_out'] = p_out[node]


set_modules(fd, fdw_mod)


## SAVE DATA
save_data = True
if save_data: 
    save_modules('Module_louvain_fdw_mod.csv', fd, fdw_mod)
    

#d['partition'] = pickle.dumps(dw_mod)
#print(d.summary())

# Save the graph 
with open('search03_lc_cnw_fdw-mod.partition','wb') as partition_file:
    pickle.dump(fdw_mod, partition_file)
igraph.write(fd, 'search03_lc_cnw_fdw-mod.graphml')


## Set the community of each node        
#def set_modules(G, partition):  
#    for community_i, community in enumerate(partition):
#        for node in community:
#            G.vs[node]['community'] = community_i
#set_modules(d, dw_mod)


##with open('dw_mod.txt', 'w') as partition_file:
##    partition_file.writelines('\t'.join(str(j) for j in i) + '\n' for i in list(dw_mod) )

#a = d.get_adjacency()
#adj = np.array(a.data) 
#np.save('d_adjacency.npy', adj)