import random
import matplotlib.pyplot as plt
import time
import itertools
import networkx as nx
import threading

class Node:
    """
    Represents a node in a network. Responsible for handling route requests (RREQ),
    route replies (RREP), and maintaining a routing table.
    """
    def __init__(self, node_id, network, ip_address):
        self.node_id = node_id
        self.network = network
        self.ip_address = ip_address
        self.routing_table = {}
        

    def send_rreq(self, destination):
        """
        Initiates a Route Request (RREQ) to find a path to the destination node.

        Args:
            destination (int): The ID of the destination node.
        """
        path = [self.node_id]
        print(f"Source: Node {self.node_id} ({self.ip_address})  --> Destination: Node {destination}")
        print()
        print(f"Node {self.node_id} initiating RREQ to Node {destination}")
        print()
        self.network.broadcast_rreq(self, destination, path)   
        
    def receive_rreq(self, source, destination, path):
        """
        Handles an incoming RREQ. If this node is the destination, it replies with an RREP.
        Otherwise, it forwards the RREQ if it hasn't already been in the path.

        Args:
            source (int): The ID of the source node.
            destination (int): The ID of the destination node.
            path (list of int): The path taken by the RREQ so far.
        """
        path.append(self.node_id)
        print(f"Node {self.node_id} received RREQ from Node {source} for destination Node {destination}, Packet: {path}")
        print()
        
        if self.node_id == destination:
            print(f"Node {self.node_id} is the destination.")
            self.network.found_paths.append(path.copy())  
        elif self.node_id not in path[:-1]:  
            print(f"Node {self.node_id} broadcasting packet to its neighbours : {self.network.connections[self.node_id]}")
            self.network.broadcast_rreq(self, destination, path.copy())

    def send_rrep(self, source, path):
        """
        Sends a Route Reply (RREP) back to the source node with the discovered path.

        Args:
            source (int): The ID of the source node.
            path (list of int): The path from the source to the destination.
        """
        print(f"Node {self.node_id} sending RREP to Node {source} with path: {path}")
        self.network.send_rrep(self, source, path)

    def receive_rrep(self, path):
        """
        Receives an RREP and updates the routing table with the path to the destination.

        Args:
            path (list of int): The path from the source to the destination.
        """
        destination = path[-1]
        self.routing_table[destination] = path
        print(f"Node {self.node_id} updated routing table for destination Node {destination}: {path}")
  
class Network:
    """
    Represents a network of nodes with a randomly generated topology.
    Handles broadcasting of RREQs and sending of RREPs.
    """
    def __init__(self, graph, nodes_dict, Node):
        
        self.connections = {node: set(neighbors) for node, neighbors in graph.items()}
        self.nodes = nodes_dict 
        self.node_objects = {node: Node(node, self, nodes_dict[node]) for node in graph.keys()}
        self.info_packet_delivered = 0
        self.confirmation_packet_delivered =0
        self.total_packets = 0
        self.total_latency = 0
        self.found_paths = []
        self.lock = threading.Lock()
        self.disconnected_nodes = set()       
        
    def assign_ips(self, num_nodes):
        """
        Assigns IPs to each node.
        """
        base_ip = itertools.count(start=1)
        for node_id in range(num_nodes):
            ip_address = f"192.168.1.{next(base_ip)}"
            node = Node(node_id, self, ip_address)
            self.nodes.append(node)
        print("Assigned IPs:")
        for node in self.nodes:
            print(f"Node {node.node_id}: IP Address {node.ip_address}")
        print()

    def create_topology_from_graph(self):
        """
        Initializes the network topology using a predefined constant graph.
        """
        print("Network topology created with connections from constant graph:")
        for node_id, neighbors in self.connections.items():
            print(f"Node {node_id}: Connected to {', '.join(map(str, neighbors))}")
        print()

    def broadcast_rreq(self, sender, destination, path):
        """
        Broadcasts an RREQ from the sender to all its connected neighbors.

        Args:
            sender (Node): The node sending the RREQ.
            destination (int): The ID of the destination node.
            path (list of int): The path taken by the RREQ so far.
        """
        
        for neighbor_id in self.connections[sender.node_id]:
            neighbor = self.node_objects[neighbor_id] 
            if neighbor.node_id not in path:
                neighbor.receive_rreq(sender.node_id, destination, path.copy())  
    
    def send_rrep(self, sender, source, path):
        """
        Sends an RREP back along the discovered path to the source node.

        Args:
            sender (Node): The node sending the RREP.
            source (int): The ID of the source node.
            path (list of int): The discovered path from source to destination.
        """
        if len(path) > 1:
            next_hop_id = path[-2]
            path.pop()  
            print(f"RREP forwarded from Node {sender.node_id} to Node {next_hop_id} with path: {path}")
            self.nodes[next_hop_id].receive_rrep(path)

    def send_packet(self, shortest_path, disconnected_nodes, packet_message):
        """
        Sends a single packet from the source to the destination along the shortest path.
        Calculates and displays latency for each packet transmission.
        """
        
        if 0 in disconnected_nodes or 9 in disconnected_nodes:
            print("Packet dropped: Either source (0) or destination (9) is disconnected.")
            return
        
        if shortest_path is None:
            print("No valid path available. Packet cannot be sent.")
            return  

    
        source = shortest_path[0]
        destination = shortest_path[-1]

        print(f"\nSource {source} sending: '{packet_message}'")

        for node in shortest_path:
            print(f"Packet '{packet_message}' is at Node {node}")

        confirmation_msg = f"Confirmation from {destination}: Packet received."
        print(confirmation_msg)
 
        self.info_packet_delivered += 1
        return self.info_packet_delivered

    def disconnect_node(self, disconnected_node):
        """
        Disconnects a specified node from the network by removing it and its connections.

        Args:
            disconnected_node (int): The node to disconnect from the network.
        """
        if disconnected_node in self.connections:
            for neighbor in list(self.connections[disconnected_node]):
                self.connections[neighbor].discard(disconnected_node)
            del self.connections[disconnected_node]

            print(f"Node {disconnected_node} and its links have been removed from the network.")
            shortest_path_after_disc = self.find_new_shortest_path(disconnected_node)
            #network.plot_network()
            return shortest_path_after_disc
            
    def reconnect_node(self, reconnected_node, neighbors, disconnected_nodes):
        """
        Reconnects a specified node to the network with the provided neighbors.

        Args:
            reconnected_node (int): The node to reconnect to the network.
            neighbors (list): List of neighbors to connect the reconnected node with.
            disconnected_nodes (set): Set of currently disconnected nodes.
        """
        if reconnected_node in self.connections:
            print(f"Node {reconnected_node} already exists in the network.")
            return

        self.connections[reconnected_node] = set()

        # Connect the node to each specified neighbor, checking if each neighbor is not in disconnected_nodes
        for neighbor in neighbors:
            if neighbor in self.connections and neighbor not in disconnected_nodes:
                self.connections[reconnected_node].add(neighbor)
                self.connections[neighbor].add(reconnected_node)
            elif neighbor in disconnected_nodes:
                print(f"Neighbor {neighbor} is currently disconnected. Skipping connection.")
            else:
                print(f"Neighbor {neighbor} does not exist in the network. Skipping connection.")

        print(f"Node {reconnected_node} has been added to the network with connections: {neighbors}")
        disconnected_nodes.remove(reconnected_node)
        # Calculate shortest paths only considering nodes that are not in disconnected_nodes
        filtered_connections = {node: nbrs - disconnected_nodes for node, nbrs in self.connections.items() if node not in disconnected_nodes}
        
        # Update `found_paths` by calculating paths with the updated `filtered_connections`
        self.found_paths = self.calculate_paths(filtered_connections, start_node=0, end_node=9)
        shortest_path = self.calculate_shortest_path(self.found_paths)
        #network.plot_network()
        
        if not shortest_path:
            print("No valid path available from Node 0 to Node 9 due to disconnected nodes.")

        return shortest_path
    
    def calculate_paths(self, connections, start_node, end_node, path=None):
        """
        Recursively finds all possible paths from start_node to end_node in the network.
        
        Args:
            connections (dict): The network graph, where each key is a node, and each value is a set of connected nodes.
            start_node (int): The starting node for the path search.
            end_node (int): The destination node for the path search.
            path (list): The current path being constructed. Default is None, which initializes it as an empty list.

        Returns:
            list of lists: A list containing all possible paths from start_node to end_node.
        """
        if path is None:
            path = []

        path = path + [start_node]

        if start_node == end_node:
            return [path]

        if start_node not in connections:
            return []
        paths = []

        for node in connections[start_node]:
            if node not in path:
                new_paths = self.calculate_paths(connections, node, end_node, path)
                for new_path in new_paths:
                    paths.append(new_path)

        return paths


    def find_new_shortest_path(self, node_to_disconnect):
        paths_after_disc = []
        for path in self.found_paths:
            if node_to_disconnect not in path and not any(node in self.disconnected_nodes for node in path):
                paths_after_disc.append(path)
            
        
        print(f"Paths after disconnecting node {node_to_disconnect}: {len(paths_after_disc)}")
        #print("Valid paths:", paths_after_disc) 

        shortest_path_after_disc = self.calculate_shortest_path(paths_after_disc)
        print(f"Shortest path after disconnection: {shortest_path_after_disc}")

        # If no valid paths exist after disconnection, exit
        if not shortest_path_after_disc:
            print("No valid paths available after disconnection.")
            return
        return shortest_path_after_disc
        
              
    def calculate_metrics(self):
        
        info_pdr = (self.info_packet_delivered / self.total_packets) * 100 if self.total_packets > 0 else 0
        conf_pdr = (self.confirmation_packet_delivered / self.total_packets) * 100 if self.total_packets > 0 else 0
        avg_latency = self.total_latency / self.info_packet_delivered if self.info_packet_delivered > 0 else 0
        throughput = self.info_packet_delivered / self.total_latency if self.total_latency > 0 else 0
        return info_pdr,  avg_latency, throughput
        
    def calculate_shortest_path(self, paths):
        if paths:  
            shortest_path = min(paths, key=len)  
            #print(f"\nShortest path selected for RREP: {shortest_path}")
            #self.nodes[shortest_path[-1]].send_rrep(shortest_path[0], shortest_path)  # Send the RREP
            return shortest_path
    
    def plot_network(self):
        """
        Plots the network topology using NetworkX and Matplotlib.
        Highlights the source and destination nodes in yellow.
        """
        G = nx.Graph()  

        for node_id in self.connections:
            if node_id is not None:
                G.add_node(node_id)
            for neighbor in self.connections[node_id]:
                if neighbor is not None and node_id is not None:
                    G.add_edge(node_id, neighbor)

      
        pos = nx.spring_layout(G, seed=42)  
        plt.figure(figsize=(12, 8))

        node_colors = []
        for node in G.nodes:
            if node == 0 or node == 9:
                node_colors.append("yellow")
            else:
                node_colors.append("skyblue")

        edge_styles = {
            "width": 2,
            "alpha": 0.5,
            "edge_color": "gray",
        }
        
        nx.draw_networkx_nodes(G, pos, node_size=800, node_color=node_colors, edgecolors="black", linewidths=1.5)
        nx.draw_networkx_edges(G, pos, **edge_styles)
        nx.draw_networkx_labels(G, pos, font_size=10, font_color="black", font_weight="bold")
        
        plt.title("Enhanced Network Topology", fontsize=16, fontweight="bold")
        plt.axis("off")  
        plt.show() 
        
        
    def select_random_node(self):
        active_nodes = [node for node in self.connections.keys() if node != 0 and node!=9]
        
        if not active_nodes:
            print("No active nodes available to disconnect.")
            return None
        
        probability_threshold = 0.7
        
        selected_nodes = [node for node in active_nodes if random.random() < probability_threshold]

        if not selected_nodes:
            selected_node = random.choice(active_nodes)
        else:
            selected_node = random.choice(selected_nodes)
        
        print(f"Randomly selected node {selected_node} for disconnection.")
        return selected_node
  
    def select_neighbors_for_reconnection(self, node_id, max_neighbors=4, min_neighbors=2):
        possible_neighbors = [node for node in self.connections.keys() if node != node_id]
        
        if len(possible_neighbors) < min_neighbors:
            print("Not enough neighbors available for reconnection.")
            return []

        num_neighbors_to_select = random.randint(min_neighbors, min(max_neighbors, len(possible_neighbors)))

        neighbors = random.sample(possible_neighbors, num_neighbors_to_select)

        print(f"Selected neighbors for node {node_id} reconnection: {neighbors}")
        return neighbors
       
    def menu_driven_program(self):
        while True:
            with self.lock:
                connected_nodes = list(self.connections.keys()) 
                disconnected_nodes = []  
                prob = random.random()
                
                for node in connected_nodes:
                    if prob < 0.4:  
                        if len(connected_nodes) > 3:  
                            success = self.disconnect_and_reconnect_node()  
                            if success:  
                                disconnected_nodes.append(node)  
                                break
                        else:
                            
                            for node in disconnected_nodes:
                                if random.random() < 0.8:  
                                    new_neighbors = self.select_neighbors_for_reconnection(node)
                                    self.reconnect_node(node, new_neighbors)
                                    break
            
            time.sleep(0.1)      
    
    def disconnect_and_reconnect_node(self):
        # Select, disconnect a node based on probability
        node_to_disconnect = self.select_random_node()
        shortest_path_after_disc = self.disconnect_node(node_to_disconnect)
        
        self.disconnected_nodes.add(node_to_disconnect)  
        return shortest_path_after_disc


    def run_simulation(self, num_packets, num_changes, shortest_path):
        """
        Simulates packet transmission over the network with potential disconnections and reconnections.
        Prints latency for each packet, and averages of PDR, latency, and throughput after all packets are sent.
        """
        total_latency = 0  
        total_pdr = 0      
        total_throughput = 0  
        
        # Start time for the total simulation
        simulation_start_time = time.time()

        for i in range(1, num_packets + 1):
            pkt_msg = f"Message of packet {i}"
            packet_start_time = time.time()
            
            self.send_packet(shortest_path, self.disconnected_nodes, pkt_msg)
            
            packet_end_time = time.time()
            
            packet_latency = packet_end_time - packet_start_time
            total_latency += packet_latency  
            
            disc_prob = random.random()
            rec_prob = random.random()

            # Randomly disconnect and reconnect nodes based on probabilities
            if disc_prob < 0.4 and num_changes < 7:
                shortest_path_after_disc = self.disconnect_and_reconnect_node()
                shortest_path = shortest_path_after_disc
                num_changes += 1  
                
                if rec_prob < 0.8:
                    # Make a copy of disconnected_nodes to avoid modifying it while iterating
                    disconnected_nodes_copy = self.disconnected_nodes.copy()
                    for node in disconnected_nodes_copy:
                        neighbours = self.select_neighbors_for_reconnection(node)
                        shortest_path1 = self.reconnect_node(node, neighbours, self.disconnected_nodes)

        simulation_end_time = time.time()
        total_time = (simulation_end_time - simulation_start_time)/1000  # Total simulation time


    # Calculate averages of each metric
        PDR = (self.info_packet_delivered / num_packets) * 100 if num_packets > 0 else 0
        throughput = (self.info_packet_delivered / total_latency)*100 if total_latency > 0 else 0
        avg_latency = (total_latency / self.info_packet_delivered) if self.info_packet_delivered > 0 else 0

        print(f"\nAfter sending all packets:")
        print(f"Average Packet Delivery Ratio (PDR): {PDR:.2f}%")
        print(f"Average Latency: {avg_latency:.5e} ms")  # Scientific notation with 10^-5 precision
        print(f"Average Throughput: {throughput:.2f} packets/second")
        print(f"Simulation Time: {total_time:.5e} s")  # Scientific notation with 10^-5 precision

        return PDR, avg_latency, throughput
                    
# Simulation

print("-------------------DYNAMIC SOURCE ROUTING PROTOCOL---------------------------------")
print()

nodes = [
    "192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", 
    "192.168.1.5", "192.168.1.6", "192.168.1.7", "192.168.1.8", 
    "192.168.1.9", "192.168.1.10"
]

nodes_dict = {i: nodes[i] for i in range(len(nodes))}

graph = {
    0: [1, 4, 5],  
    1: [0, 2, 4],  
    2: [1, 3, 6],  
    3: [2, 6, 9],  
    4: [0, 5, 1], 
    5: [4, 7, 0],  
    6: [3, 8, 2],  
    7: [5, 8, 1],  
    8: [6, 7, 9], 
    9: [8, 3, 6]  
}

network = Network(graph, nodes_dict, Node)
network.create_topology_from_graph()
network.plot_network()

network.node_objects[0].send_rreq(destination=9)

print("\nAll possible paths from Node 0 to Node 9:")
for i, path in enumerate(network.found_paths, start=1):
    print(f"Path {i} : {path}")

shortest_path = network.calculate_shortest_path(network.found_paths)
print(shortest_path)
network.plot_network() 

network.run_simulation(10,0, shortest_path)

