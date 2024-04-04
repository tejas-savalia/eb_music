import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import auc, f1_score, euclidean_distances
from sklearn.mixture import GaussianMixture
from scipy.spatial.distance import jensenshannon
import itertools

def create_adjacency_matrix_for_modular_graph(num_nodes, num_modules, module_sizes, inter_module_edges, boundary_nodes,  edges_to_remove = None):
    """
    Creates an adjacency matrix for a graph with modular structure.
    
    Args:
    num_nodes: The total number of nodes in the graph.
    num_modules: The number of modules in the graph.
    module_sizes: A list of the sizes of each module.
    inter_module_edges: A list of edges between modules.
    
    Returns:
    An adjacency matrix for the graph.
    """

  # Create an empty adjacency matrix.
    adj_matrix = np.zeros((num_nodes, num_nodes))

  # Add edges within each module.
    for module_index in range(num_modules):
        module_start_index = sum(module_sizes[:module_index])
        module_end_index = module_start_index + module_sizes[module_index]
    
        for node_index in range(module_start_index, module_end_index):
            for other_node_index in range(module_start_index, module_end_index):
                if node_index != other_node_index:
                    adj_matrix[node_index, other_node_index] = 1
        
    for node_i in boundary_nodes:
        for node_j in boundary_nodes:
            adj_matrix[node_i][node_j] = 0
    
    if edges_to_remove is not None:
        for edge in edges_to_remove:
            node_index_1, node_index_2 = edge
            adj_matrix[node_index_1, node_index_2] = 0
            adj_matrix[node_index_2, node_index_1] = 0

    # Add edges between modules.
    for edge in inter_module_edges:
        node_index_1, node_index_2 = edge
        adj_matrix[node_index_1, node_index_2] = 1
        adj_matrix[node_index_2, node_index_1] = 1
    
    return adj_matrix



def plot_graph(graph, color_node = None, ax = None):
    G = nx.Graph() 
    for i in range(graph.shape[0]):
        for j in range(graph.shape[1]):
            if graph[i][j]:
                G.add_edge(i, j)
    color_map = ['C0']*graph.shape[0]
    if color_node is not None:
        color_map[color_node] = 'C1'
    pos = nx.spring_layout(G, seed=42)
    
    nx.draw(G, with_labels = True, node_color=color_map, pos = pos, ax=ax)
    #plt.show()

def random_walk(graph, hop_step = 1000, path_length = 1000, start_state = None, p = None):
    #Random Walk
    if start_state == None:
        start_state = np.random.choice(range(graph.shape[0]))
        current_state = start_state
    else:
        start_state = start_state
        current_state = start_state
    path = np.zeros(path_length)

    for i in range(path_length):

        if (i+1)%hop_step == 0:
            start_state = np.random.choice(range(graph.shape[0]))
            current_state = start_state

        neighbour_states = np.where(graph[current_state])[0]
        # print(neighbour_states)
        if p == None:
            next_state = np.random.choice(neighbour_states)
        else:
            # print(graph[current_state][neighbour_states])
            next_state = np.random.choice(neighbour_states, p = graph[current_state][neighbour_states])
            
        path[i] = current_state
        current_state = next_state

    return path
