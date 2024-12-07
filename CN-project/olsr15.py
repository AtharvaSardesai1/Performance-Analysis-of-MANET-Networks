import networkx as nx
import random
import time

# Define Node class with IP addresses
class Node:
    def __init__(self, ip):
        self.ip = ip

    def __str__(self):
        return self.ip

    def __repr__(self):
        return f"Node({self.ip})"

# Initialize Network
def initialize_network(graph):
    G = nx.Graph()
    for node, neighbors in graph.items():
        G.add_node(node)
        for neighbor in neighbors:
            G.add_edge(node, neighbor, weight=1)
    return G

# Neighbor Discovery
def discover_neighbors(graph):
    neighbors = {}
    for node in graph.nodes():
        one_hop_neighbors = set(graph.neighbors(node))
        two_hop_neighbors = set(nbr for nbr in one_hop_neighbors for nbr in graph.neighbors(nbr))
        two_hop_neighbors.discard(node)
        two_hop_neighbors -= one_hop_neighbors
        neighbors[node] = {'1-hop': one_hop_neighbors, '2-hop': two_hop_neighbors}
    return neighbors

# MPR Selection
def select_mprs(graph, neighbors):
    mpr_selection = {}
    for node in graph.nodes():
        one_hop_neighbors = neighbors[node]['1-hop']
        two_hop_neighbors = neighbors[node]['2-hop']
        willingness = {nbr: random.random() for nbr in one_hop_neighbors}
        
        mprs, covered = set(), set()
        for nbr in one_hop_neighbors:
            reachability = set(neighbors[nbr]['1-hop']) & two_hop_neighbors
            if reachability - covered:
                mprs.add(nbr)
                covered.update(reachability)
        
        while covered != two_hop_neighbors:
            best_mpr = max(
                one_hop_neighbors - mprs,
                key=lambda x: (len(set(neighbors[x]['1-hop']) & two_hop_neighbors - covered), willingness[x]),
                default=None
            )
            if best_mpr is None:
                break
            mprs.add(best_mpr)
            covered.update(set(neighbors[best_mpr]['1-hop']) & two_hop_neighbors)
        
        mpr_selection[node] = mprs
    return mpr_selection

# Topology Table Creation
def create_topology_table(mpr_table):
    topology_table, sequence_number = {}, 0
    for node, mprs in mpr_table.items():
        for mpr in mprs:
            topology_table[node] = {
                'Dest Addr': mpr,
                'Dest MPR': node,
                'MOR Selector Seq. No.': sequence_number
            }
            sequence_number += 1
    return topology_table

# Routing Table Calculation
def calculate_routing_table(graph, topology_table):
    routing_tables = {}
    for source in graph.nodes():
        routing_table = {}
        for target in graph.nodes():
            if target != source:
                try:
                    path = nx.shortest_path(graph, source=source, target=target, weight='weight')
                    routing_table[target] = path
                except nx.NetworkXNoPath:
                    routing_table[target] = None
        routing_tables[source] = routing_table
    return routing_tables

# Packet Delivery Simulation
# Packet Delivery Simulation
def simulate_packet_delivery(graph, source, destination, num_packets=10):
    total_latency, successful_deliveries = 0, 0
    overall_start_time = time.time()

    # Calculate the routing table once for the entire graph
    neighbors = discover_neighbors(graph)
    mpr_table = select_mprs(graph, neighbors)
    topology_table = create_topology_table(mpr_table)
    routing_tables = calculate_routing_table(graph, topology_table)

    for i in range(num_packets):
        if source not in graph or destination not in graph:
            continue

        # Randomly delete and reconnect up to 4 nodes with probability
        if random.random() < 0.3:
            deletable_nodes = [node for node in graph.nodes() if node != source and node != destination]
            nodes_to_delete = random.sample(deletable_nodes, min(4, len(deletable_nodes)))
            deleted_node_neighbors = {node: list(graph.neighbors(node)) for node in nodes_to_delete}

            # Delete nodes from the graph
            for node in nodes_to_delete:
                graph.remove_node(node)

            # Reconnect deleted nodes with a probability of 0.8
            if random.random() < 0.8:
                for node, neighbors in deleted_node_neighbors.items():
                    graph.add_node(node)
                    for neighbor in neighbors:
                        graph.add_edge(neighbor, node, weight=1)

        # Start the packet delivery process using the precomputed routing table
        start_time = time.time()

        # Check if the path exists in the routing table
        path = routing_tables.get(source, {}).get(destination)

        if path:
            latency = time.time() - start_time
            total_latency += latency
            successful_deliveries += 1
        else:
            print(f"Packet {i+1} could not be delivered.")

    overall_duration = time.time() - overall_start_time
    pdr = successful_deliveries / num_packets
    avg_latency = total_latency / successful_deliveries if successful_deliveries > 0 else 0
    throughput = successful_deliveries / total_latency if total_latency > 0 else 0

    print("\n--- Simulation Results ---")
    print(f"Average Latency: {avg_latency:.4f} seconds")
    print(f"Throughput: {throughput:.4f} packets/second")
    print(f"Packet Delivery Ratio (PDR): {pdr:.2f}")

# Main Execution Flow remains the same

# Main Execution Flow
def main():
    node_ips = [f"192.168.1.{i}" for i in range(1, 11)]
    nodes = [Node(ip) for ip in node_ips]
    graph = {
        nodes[0]: [nodes[1], nodes[4], nodes[5]],  
        nodes[1]: [nodes[0], nodes[2], nodes[4]],  
        nodes[2]: [nodes[1], nodes[3], nodes[6]],  
        nodes[3]: [nodes[2], nodes[6], nodes[9]],  
        nodes[4]: [nodes[0], nodes[5], nodes[1]],  
        nodes[5]: [nodes[4], nodes[7], nodes[0]],  
        nodes[6]: [nodes[3], nodes[8], nodes[2]],  
        nodes[7]: [nodes[5], nodes[8], nodes[1]],  
        nodes[8]: [nodes[6], nodes[7], nodes[9]],  
        nodes[9]: [nodes[8], nodes[3], nodes[6]]   
    }
    
    G = initialize_network(graph)
    source, destination = nodes[0], nodes[9]
    simulate_packet_delivery(G, source, destination)

if __name__ == "__main__":
    main()
