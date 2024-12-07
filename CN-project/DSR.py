import random
import matplotlib.pyplot as plt
import time
import itertools
import networkx as nx

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
            self.network.found_paths.append(path.copy())  # Save path for evaluation
        elif self.node_id not in path[:-1]:  # Avoid cycles
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
        # self.network.send_rrep(self, source, path)

    def receive_rrep(self, path):
        """
        Receives an RREP and updates the routing table with the path to the destination.

        Args:
            path (list of int): The path from the source to the destination.
        """
        destination = path[-1]
        self.routing_table[destination] = path
        print(f"Node {self.node_id} updated routing table for destination Node {destination}: {path}")


    def maintain_routes(self):
        """
        Periodically checks routes and initiates new RREQ if needed.
        """
        for destination, path in list(self.routing_table.items()):
            if not self.network.is_route_active(path):
                print(f"Node {self.node_id} detected broken route to Node {destination}. Initiating new RREQ.")
                self.send_rreq(destination)
                
                
class Network:
    """
    Represents a network of nodes with a randomly generated topology.
    Handles broadcasting of RREQs and sending of RREPs.
    """
    def __init__(self, num_nodes):
        self.nodes = []
        self.connections = {node_id: set() for node_id in range(num_nodes)}
        self.info_packet_delivered = 0
        self.confirmation_packet_delivered =0
        self.total_packets = 0
        self.total_latency = 0
        # self.connections = {0: {2, 6}, 1: {3, 5}, 2: {0, 3, 6}, 3: {1, 2},
        #                     4: {8, 9, 7}, 5: {1, 6}, 6: {0, 2, 5, 7, 9},
        #                     7: {4, 6}, 8: {4}, 9: {4, 6}}
        
        self.found_paths = []
        
        # Assign IPs to each node after initializing the network
        self.assign_ips(num_nodes)
        self.create_random_topology(num_nodes)
        
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

    def create_random_topology(self, num_nodes):
        """
        Creates a random network topology by connecting nodes with a given probability.

        Args:
            num_nodes (int): The number of nodes in the network.
        """
         # Ensure a connected "backbone" by creating a linear path
        for i in range(num_nodes - 1):
            self.connections[i].add(i + 1)
            self.connections[i + 1].add(i)
        
        # Add random connections with a 30% probability
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if random.random() < 0.3:
                    self.connections[i].add(j)
                    self.connections[j].add(i)
        
        print("Network topology created with connections:")
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
            neighbor = self.nodes[neighbor_id]
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
            path.pop()  # Move to the next hop in the reverse path
            print(f"RREP forwarded from Node {sender.node_id} to Node {next_hop_id} with path: {path}")
            self.nodes[next_hop_id].receive_rrep(path)
            
    def send_packet(self, shortest_path):
        """
        Sends 5 packets from the source to the destination along the shortest path.
        Each packet contains a unique message, sent one second apart. 
        Calculates and stores metrics for each packet to enable plotting.
        """
        source = shortest_path[0]
        destination = shortest_path[-1]
        
        print("\nStarting packet transmission...\n")
        self.total_packets = 5  # Set total packets to 5

        # Lists to store metrics for each packet
        pdr_values = []
        conf_values = []
        avg_latency_values = []
        throughput_values = []

        for i in range(1, 6):  # Send 5 packets
            start_time = time.time()  # Start timestamp for latency measurement
            packet_message = f"Msg of packet {i}"
            print(f"\nSource {source} sending: '{packet_message}'")

            # Simulate packet traversing each node in the shortest path
            for node in shortest_path:
                time.sleep(0.2)  # Delay to simulate packet transmission time
                print(f"Packet '{packet_message}' is at Node {node}")

            # Destination receives the packet
            end_time = time.time()  # End timestamp for latency measurement
            latency = end_time - start_time
            self.total_latency += latency  # Add to total latency
            self.info_packet_delivered += 1  # Increment delivered packets count

            print(f"Destination {destination} received: '{packet_message}' with latency: {latency:.4f} seconds")
            time.sleep(1)  # Delay of 1 second between packets

            # Send confirmation back to the source
            confirmation_msg = f"Confirmation from {destination}: Packet {i} received."
            print(confirmation_msg)

            self.confirmation_packet_delivered += 1
            self.total_latency += time.time() - start_time  # Update total latency
            #self.plot_metrics(pdr_values, avg_latency_values, throughput_values)
        
    def disconnect_node(self, disconnected_node):
        """
        Disconnects a specified node from the network by removing it and its connections.

        Args:
            disconnected_node (int): The node to disconnect from the network.
        """
        if disconnected_node in self.connections:
            # Remove connections to this node from all of its neighbors
            for neighbor in list(self.connections[disconnected_node]):
                self.connections[neighbor].discard(disconnected_node)
            # Remove the node itself from the connections
            del self.connections[disconnected_node]

            print(f"Node {disconnected_node} and its links have been removed from the network.")
            self.plot_network()
            
            
    def reconnect_node(self, reconnected_node, neighbors):
        """
        Reconnects a specified node to the network with the provided neighbors.

        Args:
            reconnected_node (int): The node to reconnect to the network.
            neighbors (list): List of neighbors to connect the reconnected node with.
        """
        # Ensure the node is not already in the network
        if reconnected_node in self.connections:
            print(f"Node {reconnected_node} already exists in the network.")
            return

        # Initialize the node in the network
        self.connections[reconnected_node] = set()

        # Connect the node to each specified neighbor
        for neighbor in neighbors:
            if neighbor in self.connections:
                self.connections[reconnected_node].add(neighbor)
                self.connections[neighbor].add(reconnected_node)
            else:
                print(f"Neighbor {neighbor} does not exist in the network. Skipping connection.")
        print(self.connections)
        print(f"Node {reconnected_node} has been added back to the network with connections: {neighbors}")
        self.plot_network()
        
    def reconnect_node_with_user_input(self, reconnected_node):
        """
        Prompts the user to enter neighbors for a disconnected node and then reconnects it.

        Args:
            reconnected_node (int): The node to reconnect to the network.
        """
        if reconnected_node is None:
            print("Error: Invalid node ID provided.")
            return
        # Prompt the user to enter neighbors as a comma-separated list
        neighbors_input = input(f"Enter the neighbors of node {reconnected_node} (comma-separated): ")
        
        # Convert the input string to a list of integers
        try:
            neighbors = [int(n) for n in neighbors_input.split(',')]
        except ValueError:
            print("Invalid input. Please enter a comma-separated list of integer node IDs.")
            return

        # Call the reconnect_node function to reconnect the node with specified neighbors
        self.reconnect_node(reconnected_node, neighbors)
        
    def resend_packets(self):
        """
        Resends packets from Node 0 to Node 9 by initiating a route request (RREQ),
        displaying all possible paths found, calculating the shortest path, and
        sending packets along the shortest path.
        """
        # Step 1: Initiate RREQ from Node 0 to Node 9
        print("Initiating RREQ from Node 0 to Node 9...")
        self.nodes[0].send_rreq(destination=9)

        # Step 2: Display all possible paths found
        print("\nAll possible paths from Node 0 to Node 9:")
        for i, path in enumerate(self.found_paths, start=1):
            print(f"Path {i} : {path}")

        # Step 3: Calculate the shortest path
        shortest_path = self.calculate_shortest_path(self.found_paths)
        print(f"\nShortest path from Node 0 to Node 9: {shortest_path}")

        # Step 4: Send packets along the shortest path
        if shortest_path:
            print("Sending packets along the shortest path...")
            self.send_packet(shortest_path)
        else:
            print("No valid path found from Node 0 to Node 9.")



    def run_simulation(self, source, destination):
        # Step 1: Find the shortest path
        shortest_path = self.calculate_shortest_path(self.found_paths)
        print(f"Initial shortest path: {shortest_path}")

        # Step 2: Ask the user if they want to disconnect a node
        disconnect_choice = input("Do you want to disconnect any node? [Y/n]: ").strip().lower()
        if disconnect_choice == 'y':
            node_to_disconnect = int(input("Which node do you want to disconnect? ").strip())
            print(f"Disconnecting node: {node_to_disconnect}")
            self.disconnect_node(node_to_disconnect)
            # Call the new function to handle the disconnection and pathfinding
            self.find_new_shortest_path(node_to_disconnect)
        else:
            # If no disconnection, send packets using the original shortest path
            self.send_packet(shortest_path)

        # Calculate metrics and print
        info_pdr, conf_pdr,  avg_latency, throughput = self.calculate_metrics()
        print(f"Information Packet Delivery Ratio: {info_pdr:.2f}%")
        print(f"Confirmation Packet Delivery Ratio: {conf_pdr:.2f}%")
        print(f"Average Latency: {avg_latency:.2f}s")
        print(f"Throughput: {throughput:.2f} packets/second")
        return node_to_disconnect
        
        

    def find_new_shortest_path(self, node_to_disconnect):
        # Step 3: Copy paths without the disconnected node
        paths_after_disc = []
        for path in self.found_paths:
            # Check if the node_to_disconnect is in the current path
            if node_to_disconnect not in path:
                paths_after_disc.append(path)
            
        
        #print(f"Paths after disconnecting node {node_to_disconnect}: {len(paths_after_disc)}")  # Should show the number of valid paths
        #print("Valid paths:", paths_after_disc)  # Should list only valid paths

        # Step 4: Find the new shortest path after disconnection
        shortest_path_after_disc = self.calculate_shortest_path(paths_after_disc)
        print(f"Shortest path after disconnection: {shortest_path_after_disc}")

        # If no valid paths exist after disconnection, exit
        if not shortest_path_after_disc:
            print("No valid paths available after disconnection.")
            return

        # Send packets using the new shortest path
        self.send_packet(shortest_path_after_disc)
        
        
    def calculate_metrics(self):
        
        info_pdr = (self.info_packet_delivered / self.total_packets) * 100 if self.total_packets > 0 else 0
        conf_pdr = (self.confirmation_packet_delivered / self.total_packets) * 100 if self.total_packets > 0 else 0
        avg_latency = self.total_latency / self.info_packet_delivered if self.info_packet_delivered > 0 else 0
        throughput = self.info_packet_delivered / self.total_latency if self.total_latency > 0 else 0
        return info_pdr,conf_pdr,  avg_latency, throughput
        
    def calculate_shortest_path(self, paths):
        if paths:  # Check if the provided paths list is not empty
            shortest_path = min(paths, key=len)  # Calculate the shortest path by length
            print(f"\nShortest path selected for RREP: {shortest_path}")
            self.nodes[shortest_path[-1]].send_rrep(shortest_path[0], shortest_path)  # Send the RREP
            return shortest_path
    
    def plot_metrics(self, pdr_values, conf_values,  avg_latency_values, throughput_values):
        """
        Plot each metric (PDR, Average Latency, Throughput) over the transmission of 5 packets.
        """
        packets = range(1, 6)  # X-axis for packet numbers

        # Plot Packet Delivery Ratio (PDR)
        plt.figure(figsize=(8, 5))
        plt.plot(packets, pdr_values, marker='o', color='blue', label='PDR (%)')
        plt.xlabel("Packet Number")
        plt.ylabel("PDR (%)")
        plt.title("Packet Delivery Ratio Over Time")
        plt.legend()
        plt.grid()
        plt.show()

        # Plot Average Latency
        plt.figure(figsize=(8, 5))
        plt.plot(packets, avg_latency_values, marker='o', color='orange', label='Average Latency (s)')
        plt.xlabel("Packet Number")
        plt.ylabel("Average Latency (seconds)")
        plt.title("Average Latency Over Time")
        plt.legend()
        plt.grid()
        plt.show()

        # Plot Throughput
        plt.figure(figsize=(8, 5))
        plt.plot(packets, throughput_values, marker='o', color='green', label='Throughput (packets/sec)')
        plt.xlabel("Packet Number")
        plt.ylabel("Throughput (packets/sec)")
        plt.title("Throughput Over Time")
        plt.legend()
        plt.grid()
        plt.show()

    
    def plot_network(self):
        """
        Plots the network topology using NetworkX and Matplotlib.
        Highlights the source and destination nodes in yellow.
        """
        G = nx.Graph()  # Create an empty graph

        # Add nodes and edges to the graph based on network connections
        for node_id in self.connections:
            if node_id is not None:
                G.add_node(node_id)
            for neighbor in self.connections[node_id]:
                if neighbor is not None and node_id is not None:
                    G.add_edge(node_id, neighbor)

        # Define positions for each node
        pos = nx.spring_layout(G, seed=42)  # Seed for consistent layout
        plt.figure(figsize=(12, 8))

        # Customize node colors: yellow for source and destination, skyblue for others
        node_colors = []
        for node in G.nodes:
            if node == 0 or node == 9:
                node_colors.append("yellow")
            else:
                node_colors.append("skyblue")

        # Customize edge styling
        edge_styles = {
            "width": 2,
            "alpha": 0.5,
            "edge_color": "gray",
        }
        
        # Draw nodes with specified colors and add labels
        nx.draw_networkx_nodes(G, pos, node_size=800, node_color=node_colors, edgecolors="black", linewidths=1.5)
        nx.draw_networkx_edges(G, pos, **edge_styles)
        nx.draw_networkx_labels(G, pos, font_size=10, font_color="black", font_weight="bold")
        
        # Highlight source and destination labels
        # if source is not None:
        #     nx.draw_networkx_labels(G, pos, labels={source: f"Source ({source})"}, font_color="darkorange", font_weight="bold")
        # if destination is not None:
        #     nx.draw_networkx_labels(G, pos, labels={destination: f"Destination ({destination})"}, font_color="darkorange", font_weight="bold")

        # Add a title and show the plot
        plt.title("Enhanced Network Topology", fontsize=16, fontweight="bold")
        plt.axis("off")  # Hide axes
        plt.show()
            
    def is_route_active(self, path):
        """
        Simulates random link failures by checking if a route is active.
        """
        active_status = all(random.random() > 0.1 for _ in path)  # 10% chance each link fails
        return active_status

    def initiate_route_maintenance(self):
        """
        Triggers route maintenance on each node.
        """
        for node in self.nodes:
            node.maintain_routes()

# Simulation
print("-------------------DYNAMIC SOURCE ROUTING PROTOCOL---------------------------------")
print()

network = Network(num_nodes=10)


# Initiate RREQ from Node 0 to Node 9
network.nodes[0].send_rreq(destination=9)

# Display all paths found
print("\nAll possible paths from Node 0 to Node 9:")
for i, path in enumerate(network.found_paths, start=1):
    print(f"Path {i} : {path}")

shortest_path = network.calculate_shortest_path(network.found_paths)
print(shortest_path)
network.plot_network() 
# print(network.found_paths)
# Run the simulation with source node 0 and destination node 9
node_to_disconnect = network.run_simulation(source=0, destination=9)
print(f"Attempting to reconnect node: {node_to_disconnect}")
network.reconnect_node_with_user_input(node_to_disconnect)
network.resend_packets()

# Route Maintenance
# print("\n--- Route Maintenance ---")
# network.initiate_route_maintenance()
