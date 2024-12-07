import networkx as nx
import matplotlib.pyplot as plt
import time
import random
import matplotlib.animation as animation
from collections import deque
# Define the network graph
graph = {
    'A': ['B', 'E', 'F'],
    'B': ['A', 'C', 'E', 'H'],
    'C': ['B', 'D', 'G'],
    'D': ['C', 'G','J'],
    'E': ['A', 'B','F'],
    'F': ['A', 'E', 'H'],
    'G': ['C','D','I', 'J'],
    'H': ['B','I', 'F'],
    'I': ['H', 'G', 'J'],
    'J': ['I', 'G', 'D']
}

# Global variable to track if a path has been found
path_found = False
final_path = [] 

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.sequence_num = 0
        self.broadcast_id = 0
        self.routing_table = {}  # Format: {destination_id: [next_hop, hop_count, sequence_num]}
    
    def increment_sequence_num(self):
        self.sequence_num += 1
    
    def increment_broadcast_id(self):
        self.broadcast_id += 1
    
    def update_routing_table(self, destination, next_hop, hop_count, seq_num):
        if (destination not in self.routing_table or
            self.routing_table[destination][1] > hop_count or
            (self.routing_table[destination][1] == hop_count and 
             self.routing_table[destination][2] < seq_num)):
            self.routing_table[destination] = [next_hop, hop_count, seq_num]
            

class RREQ:
    def __init__(self, source_id, source_seq_num, broadcast_id, dest_addr, dest_seq_num, hop_count=0, latest_sender=None):
        self.source_id = source_id                  #source_node_id
        self.source_seq_num = source_seq_num        #source_node_sequence_number          
        self.broadcast_id = broadcast_id            #source_node_broadcast_id
        self.dest_addr = dest_addr                  #destination_node_address
        self.dest_seq_num = dest_seq_num            #destination_node_sequence_number
        self.hop_count = hop_count                  #current distance from the source nodes
        self.latest_sender = latest_sender          #latest sender node for backtracking the path 

class RREP:
    def __init__(self, source_id, dest_id, dest_seq_num, hop_count,latest_sender=None):
        self.source_id = source_id                  #RREP soruce id == RREQ destination id
        self.dest_id = dest_id                      #RREP Destination id == RREQ source id
        self.dest_seq_num = dest_seq_num            #Destination node sequence number
        self.hop_count = hop_count                  #current distance from the destination node
        self.latest_sender=latest_sender            #latest sender node for backtracking the path 


#Function to send RREP from the destination node
#when destination node receives the RREQ.
def send_rrep(node, rreq):
    #declare the global variables in the functions so that we can edit them inside the function.
    #if not declared, we can just access the variable not edit it
    global path_found                    
    global final_path
    #insert the node into the final path list.
    #insertion done at the front of the list because rrep starts from the destination node,
    #so insertion at the front of the list ensures path is stored in the right direction
    final_path.insert(0,node.node_id)
    #create a rrep packet with node's attributes
    rrep_packet = RREP(
        source_id=node.node_id,  
        dest_id=rreq.source_id,
        dest_seq_num=node.sequence_num,  
        hop_count=0, #initialize hop_count=0
        latest_sender=node.node_id
    )
    print(f"{node.node_id} sends RREP to {rreq.source_id}")
    #start finding the reverse path by using the source_id of received RREQ.
    next_hop = node.routing_table[rreq.source_id][0]

    #if next hop is not null, it will receive the RREP.
    if next_hop is not None:
        receive_rrep(nodes[next_hop], rrep_packet) 
    #set the path_found flag to true so that no further RREQs are sent
    path_found = True  


#Function to send RREP from intermediate node having the destination node in its routing table.
#process is a bit different.
def send_rrep2(node, rreq):
    #declare the global variables in the functions so that we can edit them inside the function.
    #if not declared, we can just access the variable not edit it
    global path_found  
    global final_path
    #here we are moving from the intermediate node to the destination node so 
    #we are appending to the end of the list so that the path order is maintained.
    final_path.append(node.node_id)
    #find the next hop from the routing table
    next_hop_node_id = node.routing_table[rreq.dest_addr][0]

    #this loop will execute till we reach the destination.
    while next_hop_node_id != rreq.dest_addr:
        #append all the intermediate nodes in the order of visit
        final_path.append(next_hop_node_id)
        #if next_hop is not in graph(may happen due to random disconnection of nodes) 
        #or routing table does not have entry for destination node then return as there is no valid path
        if next_hop_node_id not in nodes or rreq.dest_addr not in nodes[next_hop_node_id].routing_table:
            print(f"Routing error: No path to destination {rreq.dest_addr} from {next_hop_node_id}")
            return
        #otherwise, the find the next hop from the routing table
        next_hop_node_id = nodes[next_hop_node_id].routing_table[rreq.dest_addr][0]
    #finally, append the destination node to the final path
    final_path.append(rreq.dest_addr)

    #the below part of the funcion deals with sending the rrep from intermediate 
    #to the source node along the reverse path.
    rrep_packet = RREP(
        source_id=rreq.dest_addr,                 #source of rrep = destination of rreq
        dest_id=rreq.source_id,                   #destination of rrep = source of rreq
        dest_seq_num=node.sequence_num,           #current sequence number of node
        #initialize the hop count to the distance from the intermediate node to the destination node
        #so that the total distance gets added.
        hop_count=node.routing_table[rreq.dest_addr][1],    
        latest_sender=node.node_id                # latest sender is current node
    )

    print(f"{node.node_id} sends RREP to {rreq.source_id}")
    #if source id is present in the routing table(due to reverse entries f=done while rreq processing),
    #only then get the next hop
    if rreq.source_id in node.routing_table:
        next_hop = node.routing_table[rreq.source_id][0]
    else: 
        next_hop=None

    #if there is a valid next hop, then the recursive function of receiving RREP will be called
    # for the next hop in the reverse path with the RREP packet
    if next_hop is not None:
        receive_rrep(nodes[next_hop], rrep_packet) 
    #fianlly, mark the path_found flag as true to stop further processing of RREQs
    path_found = True


#Recursive function to send the RREP from destination node to source node
#This is a Unicast function
def receive_rrep(node, rrep):
    #declare the global variables in the functions so that we can edit them inside the function.
    #if not declared, we can just access the variable not edit it
    global path_found  
    global final_path  
    
    print(f"{node.node_id} received RREP from {rrep.source_id} to {rrep.dest_id}, seq_num: {rrep.dest_seq_num}, hop_count: {rrep.hop_count}")
    #since this is the reverse path, insert at the beginning of the list to 
    #maintain the correct path order (source->intermediate nodes...->destination)
    final_path.insert(0,node.node_id)
    
    #if current node is the source node, uodate its routing table with the RREP packet and return
    if rrep.dest_id == node.node_id:
        node.update_routing_table(rrep.source_id, rrep.latest_sender, rrep.hop_count + 1, rrep.dest_seq_num)
        # print("Path found between source and destination")
        return
    
    #else, update the routing table and follow the recursive procedure of 
    #finding the next hop and sending the RREP to it along the reverse path.
    node.update_routing_table(rrep.source_id, rrep.latest_sender, rrep.hop_count + 1, rrep.dest_seq_num)
    next_hop = node.routing_table[rrep.dest_id][0]
    if next_hop is not None:
        receive_rrep(nodes[next_hop], RREP(
            source_id=rrep.source_id,  
            dest_id=rrep.dest_id,
            dest_seq_num=rrep.dest_seq_num,  
            hop_count=rrep.hop_count + 1,  #incrementing the hop count
            latest_sender=node.node_id
        ))


#global hashset to keep track of the visited nodes during a Particular RREQ route discovery  
visited = set()

#Recursive function to receive the RREQ from the source node and find path to the destination node
def receive_rreq(node, rreq):
    #declare the global variables in the functions so that we can edit them inside the function.
    #if not declared, we can just access the variable not edit it
    global path_found
    global visited
    #if path is already found or current hop count is greater than the graph size, stop
    if path_found or rreq.hop_count>10:
        return
    
    # Initialize the queue for BFS and add the starting node
    queue = deque([(node, rreq)])  # Each element is a tuple (current_node, current_rreq)
    #if node is visited, stop
    if (node.node_id in visited):
        return
    #add the node to visited set
    visited.add(node.node_id)
    #the below loop will run till the queue is not empty and the path is not found
    #even if one of the above happens, iterations will stop.
    while queue and not path_found:
        #get current node from queue
        current_node, current_rreq = queue.popleft()
        
        # If the current node is the destination, send RREP and stop further propagation
        if current_rreq.dest_addr == current_node.node_id:
            current_node.update_routing_table(current_rreq.source_id, current_rreq.latest_sender, current_rreq.hop_count, current_rreq.source_seq_num)
            path_found = True
            queue.clear()
            send_rrep(current_node, current_rreq)
            return

        # Update routing table for the source node if it's not the source itself
        if current_node.node_id != current_rreq.source_id:
            current_node.update_routing_table(current_rreq.source_id, current_rreq.latest_sender, current_rreq.hop_count, current_rreq.source_seq_num)
        else:
            current_rreq.hop_count = 0

        #if the destination node is in the neighbors of the graph, add it first to the queue 
        # before other neighbors so that it gets more priority and lesser number of iterations are made
        if current_rreq.dest_addr in graph[current_node.node_id]:
            rreq_forward = RREQ(
                        current_rreq.source_id,
                        current_rreq.source_seq_num,
                        current_rreq.broadcast_id,
                        current_rreq.dest_addr,
                        current_rreq.dest_seq_num,
                        current_rreq.hop_count + 1,
                        latest_sender=current_node.node_id
                    )
            print(f"{current_node.node_id} forwards RREQ to {current_rreq.dest_addr}")
            queue.append((nodes[current_rreq.dest_addr], rreq_forward))
            

        # Forward RREQ to neighbors if the destination is not in the routing table
        #braodcasting process to all neighbors of the current node
        if current_rreq.dest_addr not in current_node.routing_table:
            for neighbor_id in graph[current_node.node_id]:
                # if (rreq.source_id in nodes[neighbor_id].routing_table and nodes[neighbor_id].routing_table[rreq.source_id][0] is not None):
                #     continue
                #if neighbor is already visited then dont forward the RREQ to that neighbor
                if (neighbor_id in visited):
                    continue
                if neighbor_id != current_rreq.latest_sender and neighbor_id != current_rreq.source_id:
                    # Create a new RREQ with incremented hop count
                    rreq_forward = RREQ(
                        current_rreq.source_id,
                        current_rreq.source_seq_num,
                        current_rreq.broadcast_id,
                        current_rreq.dest_addr,
                        current_rreq.dest_seq_num,
                        current_rreq.hop_count + 1,
                        latest_sender=current_node.node_id
                    )
                    print(f"{current_node.node_id} forwards RREQ to {neighbor_id}")
                    #append the tuple(next_hop,rreq) to the queue if its not already present in the queue
                    if (nodes[neighbor_id], rreq_forward) not in queue:
                        queue.append((nodes[neighbor_id], rreq_forward))
                        #mark it as visited
                        visited.add(neighbor_id)

        else:

            # If destination is in routing table, send RREP along the path
            path_found=True
            #initiate the second version of RREP, which orginates from the intermediate node
            send_rrep2(current_node, current_rreq)
            #get next hop from the routing table
            next_hop_node_id = current_node.routing_table[current_rreq.dest_addr][0]
            
            # Traverse the path to update routing tables for intermediate nodes
            while next_hop_node_id != current_rreq.dest_addr and next_hop_node_id in nodes:
                current_rreq.hop_count += 1
                #update the routing table
                nodes[next_hop_node_id].update_routing_table(current_rreq.source_id, current_node.node_id, current_rreq.hop_count, current_rreq.source_seq_num)
                #update the current node for recursive calls
                current_node = nodes[next_hop_node_id]
                #if destination node entry is present in the routing table then continue by chosing the next hop
                if (current_rreq.dest_addr in current_node.routing_table):
                    next_hop_node_id = current_node.routing_table[current_rreq.dest_addr][0]
                else:
                    return
            #if next hop is destination node, update its routing table for source node's entry
            if next_hop_node_id == current_rreq.dest_addr:
                current_rreq.hop_count += 1
                nodes[next_hop_node_id].update_routing_table(current_rreq.source_id, current_node.node_id, current_rreq.hop_count, current_rreq.source_seq_num)
        


# RERR handling
def send_rerr(node, dest):
    # print(f"Node {node.node_id} detected broken route to {dest}. Sending RERR messages.")
    #for all neighbors of the current node, check if the routing tbale has any paths that will be affected 
    # by the link breakage, if yes, then delete them from the routing tables and propage the 
    # RERR recursively to neighbors
    for neighbor_id in graph[node.node_id]:
        neighbor = nodes[neighbor_id]
        for path_dest, path_info in list(neighbor.routing_table.items()):
            if path_info[0] == node.node_id and path_dest == dest:
                remove_from_routing_table(neighbor, path_dest)

                # print(f"{neighbor_id} removes route to {dest} due to broken link with {node.node_id}")
                
                send_rerr(neighbor,dest)

def remove_from_routing_table(node, dest):
    if dest in node.routing_table:
        del node.routing_table[dest]

def delete_node(node_id):
    if node_id in nodes:
        node = nodes[node_id]
        
        for dest in list(node.routing_table.keys()):
            send_rerr(node, dest)
        
        if node_id in graph:
            
            for neighbor in graph[node_id]:
                graph[neighbor].remove(node_id)
          
            del graph[node_id]

        del nodes[node_id]
        
        print(f"Node {node_id} has been removed from the network.")

def reconnect_node(node_id,connections):
    connections.sort()
    if node_id not in nodes:
        graph[node_id] = connections
        for conn in connections:
            graph[conn].insert(0,node_id)  
        
        nodes[node_id] = Node(node_id)
        print(f"Node {node_id} has been reconnected to the network with connections to: {connections}")
    else:
        print(f"Node {node_id} is already in the network.")


# Initialize nodes
nodes = {node_id: Node(node_id) for node_id in graph.keys()}

def find_path(start, destination):
    global path_found  
    global final_path
    global visited  
    path_found = False  
    final_path = []
    visited.clear()  
    
    source_node = nodes[start]
    source_node.increment_sequence_num()
    source_node.increment_broadcast_id()
   
    rreq_packet = RREQ(start, source_node.sequence_num, source_node.broadcast_id, destination, nodes[destination].sequence_num,0, latest_sender=start)
    
    print(f"\nStarting RREQ from {start} to {destination}")
    receive_rreq(source_node, rreq_packet)
    # for node_id, node in nodes.items():
    #     print(f"\nRouting table for node {node_id}:")
    #     for dest, info in node.routing_table.items():
    #         print(f"  Destination: {dest}, Next hop: {info[0]}, Hop count: {info[1]}, Sequence number: {info[2]}")



def animate_graph(graph, highlighted_path):
    # Define the graph structure
    G = nx.Graph(graph)  # Assuming 'graph' is your adjacency dictionary
    pos = nx.spring_layout(G)  # Position for nodes

    # Create figure and axis
    fig, ax = plt.subplots()
    nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', ax=ax)
    plt.title("AODV Network Graph")

    # Function to update the graph for each step in the path
    def update(num):
        ax.clear()  # Clear previous frame

        # Draw the main graph
        nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', ax=ax)

        # Draw the highlighted part of the path up to the current step
        current_path = highlighted_path[:num+1]
        edges_in_path = [(current_path[i], current_path[i+1]) for i in range(len(current_path) - 1)]
        
        # Highlight the current nodes and edges in the path
        nx.draw_networkx_nodes(G, pos, nodelist=current_path, node_color='orange', node_size=500, ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=edges_in_path, edge_color='red', width=2, ax=ax)

        # Add packet progression info
        ax.set_title(f"AODV Network Graph - Packet Progress to {highlighted_path[num] if num < len(highlighted_path) else 'Destination'}")

    # Create animation
    ani = animation.FuncAnimation(fig, update, frames=len(highlighted_path), interval=10, repeat=False)

    # Display the animation
    plt.show()



def plot_metrics(packet_latencies, delivered_packets, total_packets, throughput):
    # Calculate average latency
    avg_latency = sum(packet_latencies) / len(packet_latencies) if packet_latencies else 0
    
    # Calculate packet delivery ratio (PDR)
    pdr = (delivered_packets / total_packets) * 100 if total_packets > 0 else 0
    
    # Calculate throughput
    throughput = throughput

    # Plotting metrics
    plt.figure(figsize=(15, 5))
    
    # Latency plot
    plt.subplot(1, 3, 1)
    plt.plot(packet_latencies, marker='o', color='b', label='Latency per packet (ms)')
    plt.axhline(y=avg_latency, color='r', linestyle='--', label=f'Avg Latency: {avg_latency:.2f} ms')
    plt.xlabel('Packet Number')
    plt.ylabel('Latency (ms)')
    plt.title('Packet Latency')
    plt.legend()

    # PDR plot
    plt.subplot(1, 3, 2)
    plt.bar(['Packet Delivery Ratio'], [pdr], color='g')
    plt.ylabel('PDR (%)')
    plt.ylim(0, 100)
    plt.title(f'Packet Delivery Ratio: {pdr:.2f}%')

    # Throughput plot
    plt.subplot(1, 3, 3)
    plt.bar(['Throughput'], [throughput], color='purple')
    plt.ylabel('Throughput (packets/sec)')
    plt.title(f'Throughput: {throughput:.2f} packets/sec')

    plt.tight_layout()
    plt.show()


disconnect_history = []
moving_nodes = []
def generate_prob():
    # Generate a probability (return True for disconnect, False otherwise)
    return random.random() < 0.4  # Adjust probability threshold as needed

def generate_reconnect_prob(node,source,destination):
    # Generate a probability (return True for reconnect, False otherwise)
    if (node==source or node==destination):
        return True
    return random.random() < 0.8  # Adjust probability threshold as needed

def run_network_changes(num_changes,source,destination):

    global moving_nodes
    for _ in range(num_changes):
        # Randomly select a node for possible disconnection
        node = random.choice(list(nodes.keys()))
        
        # Decide to disconnect with some probability
        if generate_prob() and node not in disconnect_history:
            delete_node(node)  # Disconnect the node in the graph
            disconnect_history.append(node)  # Add to disconnect history
            moving_nodes.append(node)

        # Decide to reconnect with some probability
        if generate_reconnect_prob(node,source,destination) and node in disconnect_history:
            # Randomly select 2-4 neighbors to reconnect
            potential_neighbors = [n for n in nodes if n != node and n not in disconnect_history]
            # new_neighbors = random.sample(potential_neighbors, random.randint(2, 4))
            num_samples = random.randint(2, 4)

# Prevent ValueError by checking the length
            if len(potential_neighbors) >= num_samples:
                new_neighbors = random.sample(potential_neighbors, num_samples)
            else:
                new_neighbors = potential_neighbors 
            reconnect_node(node, new_neighbors)  # Reconnect node in the graph
            disconnect_history.remove(node)  # Remove from disconnect history




# Define the send_packets function with node deletion/reconnection functionality



def send_packets(source, destination, total_packets):
    global moving_nodes
    if source not in graph or destination not in graph:
        print(f"Error: Either source '{source}' or destination '{destination}' is not present in the graph.")
        return
    start_time_1 = time.time()
    
    find_path(source, destination)
    if not final_path:
        print("No valid path from", source, "to", destination)
        return
    # animate_graph(graph, final_path)
    
    packets_sent = 0
    packets_delivered = 0
    total_latency = 0
    packet_latencies = []

    while packets_sent < total_packets:
        print(f"Sending packet {packets_sent + 1} from {source} to {destination} via path:", ' -> '.join(final_path))
        packets_sent += 1
        start_time=time.time()
        # Automate network changes (disconnection/reconnection)

        run_network_changes(3,source,destination)

        if source not in graph or destination not in graph:
            print(f"Error: Either source '{source}' or destination '{destination}' is not present in the graph.")
            continue
        # Recompute path if needed
        flag=False
        for node in final_path:
            if node in moving_nodes:
                flag=True
        if flag:
            find_path(source, destination)
        else:
            time.sleep(0.00000001)
        moving_nodes.clear()
        graph_start = time.time() 
        animate_graph(graph, final_path)
        graph_time=time.time()-graph_start
        if not final_path:
            print("No valid path from", source, "to", destination, "after node disconnection.")
            print(f"Packet {packets_sent} failed to deliver due to network changes.")
            continue

        # Calculate packet latency
        
        # start_time = current_time  # Reset start time for next packet

        # Check if packet successfully delivered
        packets_delivered += 1
        # print(packets_delivered)
        current_time = time.time()
        latency = current_time - start_time - graph_time
        packet_latencies.append(latency)
        total_latency += latency
        print(f"Packet {packets_sent} delivered successfully with latency: {latency:} seconds")
        
            

    # Calculate metrics
    
    avg_latency = total_latency / packets_delivered if packets_delivered > 0 else 0
    throughput = packets_delivered / total_latency if total_latency > 0 else 1
    # packet_delivery_ratio = packets_delivered / packets_sent if packets_sent > 0 else 0
    total_time = time.time() - start_time_1
    print("\nPacket transmission summary:")
    # print(f"Total packets sent: {packets_sent}/{total_packets}")
    # print(f"Packets successfully delivered: {packets_delivered}")
    # print(f"Packet Delivery Ratio (PDR): {packet_delivery_ratio:}")
    # print(f"Average latency per packet: {avg_latency:} seconds")
    # print(f"Throughput: {throughput:} packets/second")
    print(f"[RESULT] throughput: {throughput}")
    print(f"[RESULT] avg_latency: {avg_latency}")
    print(f"[RESULT] PDR: {packets_delivered/packets_sent}")
    print(f"[RESULT] total_time: {total_time}")
    plot_metrics(packet_latencies, packets_delivered, total_packets, throughput)

# Example usage:
send_packets('A', 'J', total_packets=10)



# Plotting the graph
# G = nx.Graph(graph)
# pos = nx.spring_layout(G)
# nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue')
# plt.title("AODV Network Graph")
# plt.show()
