import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# Initialize 10 nodes and random distances between them with sparsity
num_nodes = 10
edge_probability = 0.7 # Probability of an edge between any two nodes
distances = np.random.randint(1, 10, size=(num_nodes, num_nodes))

# Apply edge probability to make it sparse
for i in range(num_nodes):
    for j in range(i + 1, num_nodes):
        if np.random.rand() > edge_probability:  # Only keep edge with probability
            distances[i][j] = 0
        distances[j][i] = distances[i][j]  # Symmetric for undirected graph

np.fill_diagonal(distances, 0)  # No self-loops

# Graph setup
G = nx.Graph()
for i in range(num_nodes):
    for j in range(i + 1, num_nodes):
        if distances[i][j] > 0:  # Only add edges with non-zero distances
            G.add_edge(i, j, weight=distances[i][j])

# Display the adjacency matrix for visualization
print("Adjacency matrix (distances between nodes):")
print(distances)

# Step 1: Node discovery using Hello packets (finding direct neighbors)
neighbors = {}
for node in G.nodes():
    neighbors[node] = list(G.neighbors(node))

# Step 2: MPR Selection (Nodes select MPRs from neighbors to reduce broadcasts)
mpr_selection = {}
selected_mprs = set()
for node in G.nodes():
    max_degree_nbr = max(neighbors[node], key=lambda x: G.degree(x), default=None)
    if max_degree_nbr and max_degree_nbr not in selected_mprs:
        mpr_selection[node] = max_degree_nbr
        selected_mprs.add(max_degree_nbr)

# Step 3: Custom Dijkstra's algorithm for shortest paths
def custom_dijkstra(graph, source):
    unvisited = set(graph.nodes())
    shortest_paths = {node: float('inf') for node in graph.nodes()}
    shortest_paths[source] = 0
    prev_nodes = {}

    while unvisited:
        current = min((node for node in unvisited), key=lambda node: shortest_paths[node])
        unvisited.remove(current)

        for neighbor in graph.neighbors(current):
            distance = graph[current][neighbor]['weight']
            new_path = shortest_paths[current] + distance
            if new_path < shortest_paths[neighbor]:
                shortest_paths[neighbor] = new_path
                prev_nodes[neighbor] = current

    return shortest_paths, prev_nodes

source_node = 0
shortest_distances, previous_nodes = custom_dijkstra(G, source_node)

# Recreate paths from previous nodes
shortest_paths_full = {}
for target in G.nodes():
    path = []
    current = target
    while current != source_node:
        path.insert(0, current)
        current = previous_nodes.get(current, source_node)
    path.insert(0, source_node)
    shortest_paths_full[target] = path

# Visualization setup
pos = nx.spring_layout(G)
plt.figure(figsize=(10, 8))

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_size=700, node_color="lightblue", label="Nodes")

# Draw MPR nodes in a different color
mpr_nodes = [mpr for mpr in mpr_selection.values() if mpr is not None]
nx.draw_networkx_nodes(G, pos, nodelist=mpr_nodes, node_size=700, node_color="orange", label="MPR Nodes")

# Draw edges with weights
nx.draw_networkx_edges(G, pos, width=1, alpha=0.7, edge_color="gray")
nx.draw_networkx_edge_labels(G, pos, edge_labels={(i, j): f"{distances[i][j]}" for i, j in G.edges()}, font_size=10)

# Draw shortest path edges in a different color
for node in shortest_paths_full:
    path = shortest_paths_full[node]
    path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=2, alpha=0.7, edge_color="blue")

# Draw node labels
nx.draw_networkx_labels(G, pos, font_size=12, font_color="black")

# Adding legend and title
plt.legend(scatterpoints=1, loc="upper left")
plt.title("OLSR Protocol Simulation Visualization with Single-Edge, Sparse Graph and Shortest Paths")
plt.show()
