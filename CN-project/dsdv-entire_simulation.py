"""
Documentation:

Working of the DSDV Protocol:

The Destination Sequenced Distance Vector(DSDV) routing protocol is an ad-hoc protocol used for for infrastructureless MANET routing. It has the following characteristics which we shall address in the following points:

1. It is a proactive routing protocol.
2. It is based on the distance vector routing algorithm which used Bellman Ford Algorithm.

We shall now explain its working along with the explanation of the corresponding code segments.
Firstly, we define the classes for Node, Packet and a NetworkSimulator. In DSDV, each node consists of a forwarding table and an advertised table. We have also assumed the node to have one interface for now whose IP address is stored as the Node class variable. 
In the Packet class, we have attributed each packet with its source IP, destination IP, packet sequence number and a timestamp variable to hold the start_time value which will come into picture while calculating latency.

After initialization of a random/ predefined graph with a predefined number of nodes and edges, the forwarding table of each node object of the Node class is prepared by entering the directly connected node entries, with metric as 0, next hop as the node IP itself, and the sequence number also as 0. 
Following this, certain specified number of full dump advertisements are simulated throughout the graph so that the neighboring nodes can gather the information including next hop and metrics corresponding to all the destinations abiding by the distance vector algorithm. Here full dump refers to advertizing the entire routing table to the neighbors in contrast to an incremental dump where only the changed/ updated routes are advertized. 
This characteristic of DSDV to ensure that a fully filled forwarding table to exist for each node makes it a proactive protocol.

A predefined source and destination node is specified followed by a variable which holds the value for number of changes we wish to simulate in the graph.
We then call the run_network_changes(). Now, a Packet is created and the corresponding member variable initialization is done. The next hop IP is checked in the forwarding table of the current node and the packet is sent to that next IP. In this transition, the packet sequence number is also incremented.
Once the packet reaches the destination, we simulate the most important characteristic- dynamic topology change, when it comes to MANET protocols. A random function checks if the probability for the disconnection of a node falls within the range of a predefined value. If yes, a random node is disconnected from the graph. The disconnect_node() function is called which uses a breadth-first search like approach to broadcast and advertize the changed metric which is now set to infinity for all the nodes which have the next hop equal to the now disconnected node. This is done via an incremental dump. Say one node A intially had to go through B on its way to C. Now if B is disconnected, besides setting B's metric as infinity in its forwarding table, A will also set C's metric as infinity since it is currently not reachable. The sequence number is also appropriately incremented. 

After this first round of advertisement, the advertise_method() is called again. Here the nodes which were not disconnected but at the same time not reachable by some nodes become reachable, since the nodes learn about new routes and update their forwarding table accordingly. 

Now, similar to the disconnection probability, we have set a reconnection probability, where if the value lies within a predefined range, the node will be reconnected to a randomly generated new set of neighbors. The forwarding and the advertized tables will be updated accordingly. 

Types of Messages in DSDV:
1. Full dump update: The entire forwarding table is advertized to neighboring nodes (though its periodicity is less)
2. Incremental update: Only the routes which have changed and their sequence number have been incremented are advertized to the neighboring nodes.

Data Structures used
1. Graph: Implemented using Python dictionaries to represent:
	a. The network topology including the nodes and edges between any two nodes.
	b. The forwarding and advertized tables for each node.
2. Lists: Implemented using Python lists to store mutable values corresponding to different variables such as storage of neighboring nodes, or visited nodes in case of BFS.
3. Queue: Implemented using Python lists to perform FIFO approach while sending a triggered incremental dump update corresponding to the disconnection of a node in the BFS method and disconnect_node method()

"""

import random
import time
import threading
import matplotlib.pyplot as plt
from collections import defaultdict
import networkx as nx
from matplotlib.animation import FuncAnimation
global total_time
disconnect=None
disconnect_history=[]
PROB= 0.4
RECONNECT=0.8
class Node:
    def __init__(self, ip):
        self.ip = ip
        self.forwarding_table = {}  
        self.advertised_table = {}  
        self.sent_packets = []
        self.received_packets = []
        self.control_packets = 0
        
    def send_packet(self, packet, next_hop):
        self.sent_packets.append(packet)
        print(f"Node {self.ip} sent packet {packet.sequence_number} to Node {next_hop}")

    def receive_packet(self, packet):
        self.received_packets.append(packet)
        if not packet.is_data:
            self.control_packets += 1
        print(f"Node {self.ip} received packet {packet.sequence_number}")
    def __repr__(self):
        return f"Node({self.ip})"
    def total_packets_received(self):
        print("total_packets_received", len(self.received_packets))

class Packet:
    def __init__(self, source, destination, sequence_number, is_data=True):
        self.source = source
        self.sequence_number = sequence_number
        self.destination= destination
        self.is_data = is_data
        self.timestamp = time.time()



class NetworkSimulator:
    def __init__(self, nodes, node_dict):
        self.nodes = nodes 
        self.sequence_number = 0
        self.total_packets = 10
        self.delivered_packets = 0
        self.total_latency = 0
        self.node_dict = node_dict
    def find_route(self, source, destination):

        if source in self.node_dict:
            source_obj= self.node_dict.get(source) 
        else:
            return None

        if destination in source_obj.forwarding_table and source_obj.forwarding_table[destination]["metric"] != float('inf'):
            return source_obj.forwarding_table[destination]["next_hop"]
        else:
            return None  

    def send_packet(self, source, destination):
        next_hop = self.find_route(source, destination)
        if next_hop is not None:
            packet = Packet(source, destination, self.sequence_number)
            self.sequence_number += 1
            source_obj= self.node_dict.get(source)
            source_obj.send_packet(packet, next_hop)
            self.deliver_packet(packet)
        else:
            print("No route found. Packet dropped.")


 
    def deliver_packet(self, packet):
        destination_node = self.node_dict.get(packet.destination)


        destination_node.receive_packet(packet)
        latency = time.time() - packet.timestamp
        print(f"Packet {packet.sequence_number} successfully delivered to {destination_node.ip} with latency {latency} s")
        self.total_latency += latency
        self.delivered_packets += 1
        

    def simulate(self, num_packets, source, destination):
        for _ in range(num_packets):
            self.send_packet(source, destination)
            time.sleep(0.1)

    def calculate_metrics(self):

        throughput = self.delivered_packets / (self.total_latency if self.total_latency > 0 else 1)


        average_latency = self.total_latency / self.delivered_packets if self.delivered_packets > 0 else 0


        pdr = self.delivered_packets / self.total_packets if self.total_packets > 0 else 0

        
        
        return {
            "throughput": throughput,
            "avg_latency": average_latency,
            "PDR": pdr
            
        }
 
    def totalpackets(self):
        print(" total delivered packets: ", self.delivered_packets)












node_ips = [f"192.168.1.{i}" for i in range(1, 11)]
nodes = [Node(ip) for ip in node_ips]
graph = {
    nodes[0]: [nodes[1], nodes[4], nodes[5]],  # 192.168.1.1 connected to 192.168.1.2, 192.168.1.5, and 192.168.1.6
    nodes[1]: [nodes[0], nodes[2], nodes[4]],  # 192.168.1.2 connected to 192.168.1.1, 192.168.1.3, and 192.168.1.5
    nodes[2]: [nodes[1], nodes[3], nodes[6]],  # 192.168.1.3 connected to 192.168.1.2, 192.168.1.4, and 192.168.1.7
    nodes[3]: [nodes[2], nodes[6], nodes[9]],  # 192.168.1.4 connected to 192.168.1.3, 192.168.1.7, and 192.168.1.10
    nodes[4]: [nodes[0], nodes[5], nodes[1]],  # 192.168.1.5 connected to 192.168.1.1, 192.168.1.6, and 192.168.1.2
    nodes[5]: [nodes[4], nodes[7], nodes[0]],  # 192.168.1.6 connected to 192.168.1.5, 192.168.1.8, and 192.168.1.1
    nodes[6]: [nodes[3], nodes[8], nodes[2]],  # 192.168.1.7 connected to 192.168.1.4, 192.168.1.9, and 192.168.1.3
    nodes[7]: [nodes[5], nodes[8], nodes[1]],  # 192.168.1.8 connected to 192.168.1.6, 192.168.1.9, and 192.168.1.2
    nodes[8]: [nodes[6], nodes[7], nodes[9]],  # 192.168.1.9 connected to 192.168.1.7, 192.168.1.8, and 192.168.1.10
    nodes[9]: [nodes[8], nodes[3], nodes[6]]   # 192.168.1.10 connected to 192.168.1.9, 192.168.1.4, and 192.168.1.7
}
network_topology = defaultdict(list)
for node in nodes:
    """following line applies to randomization of the graph, maybe can be used for testing purpose later
    #neighbors = random.sample([n for n in nodes if n != node], random.randint(2, 3))"""
    neighbors = graph[node]
    for neighbor in neighbors:
        if neighbor not in network_topology[node]: 
            network_topology[node].append(neighbor)
            network_topology[neighbor].append(node)  

G = nx.Graph()


def update_graph():
    G.clear()  
    for node, neighbors in network_topology.items():
        for neighbor in neighbors:
            G.add_edge(node.ip, neighbor.ip)

def generate_prob():
    return random.random() < PROB   
def generate_reconnect_prob():
    return random.random() < RECONNECT   


def disconnect_graph(node):
    if node in disconnect_history:
        return
    if node in network_topology:
        for neighbor in network_topology[node]:
            if node in network_topology[neighbor]:
                network_topology[neighbor].remove(node)
        network_topology[node].clear()
        disconnect_history.append(node)
        print(f"Node {node.ip} disconnected.")


def reconnect_graph(node, new_neighbors):
    for neighbor_ip in new_neighbors:
        neighbor = next((n for n in nodes if n.ip == neighbor_ip), None)
        if neighbor and neighbor != node:
            network_topology[node].append(neighbor)
            network_topology[neighbor].append(node)
    print(f"Node {node.ip} reconnected to {[n for n in new_neighbors]}.")




for node, connections in network_topology.items():
    print(f"{node}: {connections}")

def initialize_routing_tables():
    for node in nodes:
        node.forwarding_table[node.ip]={
        "next_hop": node.ip,
        "metric": 0,
        "sequence_number": 0
        }
        for neighbor in network_topology[node]:
            node.forwarding_table[neighbor.ip] = {
                "next_hop": neighbor.ip,
                "metric": 1,
                "sequence_number": 0
            }
            node.advertised_table[neighbor.ip] = node.forwarding_table[neighbor.ip].copy()

initialize_routing_tables()
node_dict = {node.ip: node for node in nodes}
print("\nInitial Forwarding:")
for node in nodes:
    print(f"\nNode {node.ip} Forwarding Table:")
    for dest, route in node.forwarding_table.items():
        print(f"  {dest} -> Next Hop: {route['next_hop']}, Metric: {route['metric']}, Seq#: {route['sequence_number']}")


def bfs(neighbor, incremental_dump, visited1):
    visited1.append(neighbor)
    visited= visited1.copy()
    #print(incremental_dump)
    for direct in network_topology[neighbor]:
        # now we got that neighboring node
        flag=0
        if direct in visited:
            continue
        for eachip in incremental_dump:
            if direct.forwarding_table[eachip]["metric"] > neighbor.forwarding_table[eachip]["metric"] +1 :
                direct.forwarding_table[eachip] = {
                    "next_hop": neighbor.ip,
                    "metric": neighbor.forwarding_table[eachip]["metric"] +1,
                    "sequence_number": neighbor.forwarding_table[eachip]["sequence_number"]
                }
                flag=1
        if flag==1 and direct not in visited:
            bfs(direct, incremental_dump, visited)            
def advertise_routes(disconnect):
    
    for node in nodes:
        #start time
        if disconnect!=None and node == disconnect :
            continue
        for neighbor in network_topology[node]:
            incremental_dump=[]
            if(disconnect!=None and neighbor.ip == disconnect):
                continue
            for dest, route in node.forwarding_table.items():
                #print((dest == neighbor.ip))
                #print(dest)
                
                if(disconnect!=None and dest == disconnect):
                    continue
                if dest in neighbor.forwarding_table and dest == neighbor.ip :
                    continue
                if dest in neighbor.forwarding_table and dest == node.ip:
                    continue
                if (dest  not in neighbor.forwarding_table and dest != neighbor.ip) or \
                   (dest in neighbor.forwarding_table and neighbor.forwarding_table[dest]["sequence_number"] < route["sequence_number"] and route["metric"]!= float("inf")) or \
                   (dest in neighbor.forwarding_table and neighbor.forwarding_table[dest]["next_hop"]=="#" ) or \
                   ( dest in neighbor.forwarding_table and neighbor.forwarding_table[dest]["sequence_number"] == route["sequence_number"] and route["metric"] !=float("inf") and neighbor.forwarding_table[dest]["metric"] > route["metric"] + 1):
                     
                    if(dest in neighbor.forwarding_table and route["metric"] != float("inf") and neighbor.forwarding_table[dest]["metric"] == float("inf")): #code for reconnection
                        neighbor.forwarding_table[dest] = {
                            "next_hop": node.ip,
                            "metric": route["metric"] +1,
                            "sequence_number": route["sequence_number"]
                        }
                    else:
                        #print("neighbor", neighbor.ip , "and for node", node.ip)
                        neighbor.forwarding_table[dest] = {
                            "next_hop": node.ip,
                            "metric": route["metric"] +1,
                            "sequence_number": route["sequence_number"]
                        }
                    if disconnect!=None:    
                        incremental_dump.append(dest)
                        #print(dest, "for", node.ip , "and neighbor", neighbor.ip)
                    neighbor.advertised_table[dest] = neighbor.forwarding_table[dest].copy()
            if disconnect!=None:
                disconnectednode=node_dict.get(disconnect)
                visited=[node, disconnectednode]
            if len(incremental_dump)!=0:
                bfs(neighbor, incremental_dump, visited) # here incremental_dump consists of all the changes dest ips    
               # elif(dest in neighbor.forwarding_table and neighbor.forwarding_table[dest]["sequence_number"] == route["sequence_number"] and neighbor.forwarding_table[dest]["metric"] == route["metric"] + 1):
                  #  neighbor.forwarding_table[dest]["next_hop"]=node.ip
                   # neighbor.forwarding_table[dest]["sequence_number"]+=2
        #end time        
def disconnect_node(moving_node):
    visited={}
    queue=[]
    target=[]
    node_dict = {node.ip: node for node in nodes}
    visited[moving_node]=True
    for dest, route in moving_node.forwarding_table.items():
        
        if route["metric"]== 1 or route["metric"]==0:
            #if route["metric"]==1:
                #network_topology[node_dict.get(dest)].remove(moving_node)
            queue.append(dest)
            visited[dest]=True
            target.append(moving_node.ip)
        moving_node.forwarding_table[dest]["metric"]= float("inf")
    while(len(queue)!=0):
        node_ip=queue[0]
        visited[node_ip]=True
        targeting=target[0]
        target.pop(0)
        queue.pop(0)
        
        node= node_dict.get(node_ip) 
        prev= node_dict.get(targeting) 
        if node.ip == moving_node.ip:
            node_ip= queue[0]
            queue.pop(0)
            targeting=target[0]
            target.pop(0)
        node= node_dict.get(node_ip)
        prev= node_dict.get(targeting)
        #print(node.ip, prev.ip)
        for dest, route in node.forwarding_table.items():
            if route["next_hop"]== targeting  and dest in prev.forwarding_table and prev.forwarding_table[dest]["metric"]==float("inf"):
                node.forwarding_table[dest]["metric"]=float("inf")
        for each in network_topology[node]:

            if each.ip not in visited or visited[each.ip]==False:
                target.append(node.ip)
                queue.append(each.ip)
                
    moving_node.forwarding_table.clear()
    moving_node.advertised_table.clear()
    """for node in nodes:
        print(f"\nNode {node.ip} Forwarding Table:")
        for dest, route in node.forwarding_table.items():
            print(f"  {dest} -> Next Hop: {route['next_hop']}, Metric: {route['metric']}, Seq#: {route['sequence_number']}")   """            

def reconnect_node(moving_node, new_neighbors_ips):
    moving_node.forwarding_table[moving_node.ip] = {
                "next_hop": moving_node.ip,
                "metric": 0,
                "sequence_number": 0 # look after this
            }
    network_topology[moving_node] = []  
    for new_neighbor_ip in new_neighbors_ips:
        new_neighbor = next((node for node in nodes if node.ip == new_neighbor_ip), None)
        if new_neighbor:
            network_topology[moving_node].append(new_neighbor)
            network_topology[new_neighbor].append(moving_node)  
            
            moving_node.forwarding_table[new_neighbor.ip] = {
                "next_hop": new_neighbor.ip,
                "metric": 1,
                "sequence_number": 0 # look after this
            }
            new_neighbor.forwarding_table[moving_node.ip]={
                "next_hop": moving_node.ip,
                "metric": 1,
                "sequence_number": 0 # look after this
            }
            moving_node.advertised_table[new_neighbor.ip] = moving_node.forwarding_table[new_neighbor.ip].copy()
    disconnect=None
    """for node in nodes:
        print(f"\nNode {node.ip} Forwarding Table:")
        for dest, route in node.forwarding_table.items():
            print(f"  {dest} -> Next Hop: {route['next_hop']}, Metric: {route['metric']}, Seq#: {route['sequence_number']}")
    #advertise_routes(disconnect)"""

            

def advertise_method(disconnect):
    advertise_routes(disconnect)
    """print("\nRouting Tables after Periodic Advertisement:")
    for node in nodes:
        print(f"\nNode {node.ip} Forwarding Table:")
        for dest, route in node.forwarding_table.items():
            print(f"  {dest} -> Next Hop: {route['next_hop']}, Metric: {route['metric']}, Seq#: {route['sequence_number']}")
    #time.sleep(2)"""
    
network_sim = NetworkSimulator(nodes, node_dict)
def run_network_changes(num_changes, source, destination):
    global total_time
    time1 = time.time()
    
    for _ in range(num_changes):
        
        network_sim.send_packet(source, destination)
        #time.sleep(0.1)

        node = random.choice(nodes)
        if generate_prob():
            
        
            disconnect_graph(node)
            disconnect_node(node)
            update_graph()#deletable
            advertise_method(disconnect)
            advertise_method(disconnect)
            time.sleep(0.1) #deletable
            if generate_reconnect_prob():
            

                new_neighbors = random.sample([n.ip for n in nodes if n != node and n not in disconnect_history], random.randint(2, 3))
                reconnect_graph(node, new_neighbors)
                reconnect_node(node, new_neighbors)
                update_graph()#deletable
                if node in disconnect_history:
                    disconnect_history.remove(node)
                advertise_method(disconnect)
                advertise_method(disconnect)
                time.sleep(0.1) #deletable
    time2= time.time()
    total_time =time2-time1


def draw(_):
    plt.clf()
    pos = nx.spring_layout(G, seed=42)

    nx.draw(G, pos={node: pos[node] for node in G.nodes if node in pos},
        with_labels=True, node_color='skyblue', edge_color='gray', node_size=500, font_size=10, font_weight='bold')
    plt.title("Random Bidirectional Network Topology")
    #plt.pause(1)
    #plt.close()

def send_packets():
    time1 = time.time()
    network_sim.simulate(num_packets=10, source='192.168.1.1', destination='192.168.1.10')
    time2= time.time()
    print("time taken for all packets : ", time2-time1)


fig = plt.figure(figsize=(10, 8))
update_graph() 

for _ in range(5):    
    advertise_method(disconnect)
     
print("\nRouting Tables after Periodic Advertisement:")
for node in nodes:
    print(f"\nNode {node.ip} Forwarding Table:")
    for dest, route in node.forwarding_table.items():
        print(f"  {dest} -> Next Hop: {route['next_hop']}, Metric: {route['metric']}, Seq#: {route['sequence_number']}")
    #time.sleep(2)

network_sim = NetworkSimulator(nodes, node_dict)
run_network_changes(10,'192.168.1.1', '192.168.1.10')

  

ani = FuncAnimation(fig, draw, interval=500)

plt.show()

for node in nodes:
        print(f"\nNode {node.ip} Forwarding Table:")
        for dest, route in node.forwarding_table.items():
            print(f"  {dest} -> Next Hop: {route['next_hop']}, Metric: {route['metric']}, Seq#: {route['sequence_number']}")


metrics = network_sim.calculate_metrics()
print(network_sim.totalpackets())

print(f"[RESULT] throughput: {metrics['throughput']}")
print(f"[RESULT] avg_latency: {metrics['avg_latency']}")
print(f"[RESULT] PDR: {metrics['PDR']}")
print(f"[RESULT] total_time: {total_time}")



plt.figure(figsize=(15, 10))


