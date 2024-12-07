import networkx as nx
import random
import matplotlib.pyplot as plt
import time

# Initialize the network with 10 nodes, edges with weight 1
nodes = [
    '192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4', 
    '192.168.1.5', '192.168.1.6', '192.168.1.7', '192.168.1.8', 
    '192.168.1.9', '192.168.1.10'
]

# Create a new networkx graph object
graph = nx.Graph()

# Add nodes to the graph
graph.add_nodes_from(nodes)

# Define the edges between the nodes
edges = [
    ('192.168.1.1', '192.168.1.2'), ('192.168.1.1', '192.168.1.5'), ('192.168.1.1', '192.168.1.6'),
    ('192.168.1.2', '192.168.1.1'), ('192.168.1.2', '192.168.1.3'), ('192.168.1.2', '192.168.1.5'),
    ('192.168.1.3', '192.168.1.2'), ('192.168.1.3', '192.168.1.4'), ('192.168.1.3', '192.168.1.7'),
    ('192.168.1.4', '192.168.1.3'), ('192.168.1.4', '192.168.1.7'), ('192.168.1.4', '192.168.1.10'),
    ('192.168.1.5', '192.168.1.1'), ('192.168.1.5', '192.168.1.6'), ('192.168.1.5', '192.168.1.2'),
    ('192.168.1.6', '192.168.1.5'), ('192.168.1.6', '192.168.1.8'), ('192.168.1.6', '192.168.1.1'),
    ('192.168.1.7', '192.168.1.4'), ('192.168.1.7', '192.168.1.9'), ('192.168.1.7', '192.168.1.3'),
    ('192.168.1.8', '192.168.1.6'), ('192.168.1.8', '192.168.1.9'), ('192.168.1.8', '192.168.1.2'),
    ('192.168.1.9', '192.168.1.7'), ('192.168.1.9', '192.168.1.8'), ('192.168.1.9', '192.168.1.10'),
    ('192.168.1.10', '192.168.1.9'), ('192.168.1.10', '192.168.1.4'), ('192.168.1.10', '192.168.1.7')
]

# Add edges to the graph
graph.add_edges_from(edges)

# Step 1: Neighbor Discovery with Hello Packets
def discover_neighbors(graph):
    neighbors = {}
    for node in graph.nodes():
        # 1-hop neighbors
        one_hop_neighbors = set(graph.neighbors(node))
        
        # 2-hop neighbors
        two_hop_neighbors = set()
        for nbr in one_hop_neighbors:
            two_hop_neighbors.update(graph.neighbors(nbr))
        two_hop_neighbors.discard(node)  # Remove self
        two_hop_neighbors -= one_hop_neighbors  # Exclude 1-hop neighbors

        neighbors[node] = {'1-hop': one_hop_neighbors, '2-hop': two_hop_neighbors}
    return neighbors

# Display neighbor table for all nodes
def display_neighbor_table(neighbor_table):
    print("\nNeighbor Table:")
    for node, nbrs in neighbor_table.items():
        print(f"Node {node}: 1-hop -> {nbrs['1-hop']}, 2-hop -> {nbrs['2-hop']}")

# Function to delete a node and update tables
def delete_node(graph, node_to_delete):
    if node_to_delete in graph:
        graph.remove_node(node_to_delete)
        print(f"Node {node_to_delete} has been deleted.")
    else:
        print(f"Node {node_to_delete} does not exist.")

    # Update neighbor table
    updated_neighbor_table = discover_neighbors(graph)

    # Update MPR table
    updated_mpr_table = select_mprs(graph, updated_neighbor_table)

    # Update topology table
    updated_topology_table = {}
    sequence_number = 0
    for node, mprs in updated_mpr_table.items():
        for mpr in mprs:
            updated_topology_table[node] = {
                'Dest Addr': mpr,
                'Dest MPR': node,
                'MOR Selector Seq. No.': sequence_number
            }
            sequence_number += 1

    # Update routing tables
    updated_routing_tables = calculate_routing_table(graph, updated_topology_table)

    return updated_neighbor_table, updated_mpr_table, updated_topology_table, updated_routing_tables

# Function to add a new node and its neighbors
def add_node(graph, new_node, neighbors):
    if new_node in graph:
        print(f"Node {new_node} already exists.")
        return

    graph.add_node(new_node)
    for nbr in neighbors:
        if nbr in graph:
            graph.add_edge(new_node, nbr, weight=1)
    print(f"Node {new_node} has been added with neighbors {neighbors}.")

    # Update neighbor table
    updated_neighbor_table = discover_neighbors(graph)

    # Update MPR table
    updated_mpr_table = select_mprs(graph, updated_neighbor_table)

    # Update topology table
    updated_topology_table = {}
    sequence_number = 0
    for node, mprs in updated_mpr_table.items():
        for mpr in mprs:
            updated_topology_table[node] = {
                'Dest Addr': mpr,
                'Dest MPR': node,
                'MOR Selector Seq. No.': sequence_number
            }
            sequence_number += 1

    # Update routing tables
    updated_routing_tables = calculate_routing_table(graph, updated_topology_table)

    return updated_neighbor_table, updated_mpr_table, updated_topology_table, updated_routing_tables

# Step 2: MPR Selection
def select_mprs(graph, neighbors):
    mpr_selection = {}
    for node in graph.nodes():
        one_hop_neighbors = neighbors[node]['1-hop']
        two_hop_neighbors = neighbors[node]['2-hop']
        
        # Simulated willingness (higher willingness means more likely to be selected)
        willingness = {nbr: random.random() for nbr in one_hop_neighbors}
        
        # MPR selection algorithm
        mprs = set()
        covered = set()
        
        # Step 1: Select 1-hop neighbors covering isolated 2-hop neighbors
        for nbr in one_hop_neighbors:
            reachability = set(neighbors[nbr]['1-hop']) & two_hop_neighbors
            if reachability - covered:
                mprs.add(nbr)
                covered.update(reachability)
        
        # Step 2: Select additional 1-hop neighbors for maximum coverage until all 2-hop neighbors are covered
        while covered != two_hop_neighbors:
            best_mpr = max(
                one_hop_neighbors - mprs,
                key=lambda x: (len(set(neighbors[x]['1-hop']) & two_hop_neighbors - covered), willingness[x]),
                default=None
            )
            if best_mpr is None:
                break  # Exit if no more candidates
            mprs.add(best_mpr)
            covered.update(set(neighbors[best_mpr]['1-hop']) & two_hop_neighbors)
        
        mpr_selection[node] = mprs
    return mpr_selection

mpr_table = select_mprs(graph, discover_neighbors(graph))
print("\nInitial MPR Table:")
for node, mprs in mpr_table.items():
    print(f"Node {node}: MPRs -> {mprs}")

# Step 3: Topology Control (TC) Message Propagation
topology_table = {}
sequence_number = 0

for node, mprs in mpr_table.items():
    for mpr in mprs:
        topology_table[node] = {
            'Dest Addr': mpr,
            'Dest MPR': node,
            'MOR Selector Seq. No.': sequence_number
        }
        sequence_number += 1

# Step 4: Routing Table Calculation
def calculate_routing_table(graph, topology_table):
    routing_tables = {}
    for source in graph.nodes():
        routing_table = {}
        for target in graph.nodes():
            if source == target:
                routing_table[target] = [source]
            else:
                try:
                    path = nx.shortest_path(graph, source, target)
                    routing_table[target] = path
                except nx.NetworkXNoPath:
                    routing_table[target] = None
        routing_tables[source] = routing_table
    return routing_tables

routing_tables = calculate_routing_table(graph, topology_table)

# Step 5: Display updated routing tables
def display_routing_tables(routing_tables):
    for source, routing_table in routing_tables.items():
        print(f"\nRouting Table for Node {source}:")
        for target, path in routing_table.items():
            print(f"  Target {target}: {path if path else 'No path'}")

# Graph Visualization
def display_graph():
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(graph)  # Positioning of nodes
    nx.draw(graph, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold')
    plt.title("Network Topology")
    plt.show()

# Function to update and display tables
def update_and_display_tables():
    neighbor_table = discover_neighbors(graph)
    display_neighbor_table(neighbor_table)

    # Display MPR Table
    mpr_table = select_mprs(graph, neighbor_table)
    print("\nMPR Table:")
    for node, mprs in mpr_table.items():
        print(f"Node {node}: MPRs -> {mprs}")

    # Display Routing Tables
    display_routing_tables(routing_tables)
    
    # Display the network graph
    display_graph()

# Example actions
# Add a new node and update
new_node = '192.168.1.11'
neighbors_of_new_node = ['192.168.1.3', '192.168.1.5']
updated_neighbor_table, updated_mpr_table, updated_topology_table, updated_routing_tables = add_node(graph, new_node, neighbors_of_new_node)

# Display the updated network and tables
update_and_display_tables()

# After deleting a node
node_to_delete = '192.168.1.10'
updated_neighbor_table, updated_mpr_table, updated_topology_table, updated_routing_tables = delete_node(graph, node_to_delete)

# Display the updated network and tables
update_and_display_tables()
