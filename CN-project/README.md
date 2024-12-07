# Title
**Comparative Analysis and Security Enhancement of Routing Protocols in Mobile Ad hoc Networks (MANETs): A Focus on DSDV, AODV, DSR, and OLSR Protocols**

---

## Abstract
This project explores and implements four key routing protocols for Mobile Ad hoc Networks (MANETs) — DSDV, AODV, DSR, and OLSR. These protocols are widely studied in academic and industrial research for their applicability in dynamic, self-organizing network environments. Our project not only aims to implement these protocols from scratch in Python but also performs a comprehensive comparative analysis across metrics such as throughput, latency, packet delivery ratio, and control overhead. Additionally, we address common vulnerabilities for each protocol, implementing and evaluating mitigation techniques to enhance security and reliability. We use RFCs and foundational research papers as our primary technical references.

---

## Aim
To implement and evaluate DSDV, AODV, DSR, and OLSR protocols in Python, perform a comparative analysis on core performance metrics, and address well-known security vulnerabilities to improve protocol robustness in MANET environments.

---

## Project Description
In this project, we develop a Python-based simulation environment to implement and test four widely researched MANET routing protocols:
- **Destination-Sequenced Distance-Vector (DSDV)**
- **Ad hoc On-Demand Distance Vector (AODV)**
- **Dynamic Source Routing (DSR)**
- **Optimized Link State Routing (OLSR)**

Each protocol’s design aligns with its original specifications, with reference to the corresponding **RFCs** and **research papers**. Our approach includes developing a comparative analysis framework, measuring protocol performance across several network metrics, and identifying areas for optimization and enhancement. Furthermore, we simulate common network attacks specific to each protocol, including black hole attacks in AODV and selective forwarding attacks in OLSR, and propose corresponding mitigation techniques.

---

## Objectives
1. **Protocol Implementation**: Develop Python-based implementations of DSDV, AODV, DSR, and OLSR protocols, adhering to their foundational designs as per respective RFCs and research publications.
2. **Comparative Analysis**: Perform a comprehensive analysis of each protocol on key metrics:
   - **Throughput**
   - **Latency**
   - **Packet Delivery Ratio (PDR)**
   - **Control Overhead**
   - **Routing Load**
3. **Vulnerability Simulation and Mitigation**: Identify and simulate well-known vulnerabilities in each protocol and implement mitigations:
   - **DSDV**: Address high control overhead by implementing adaptive update intervals.
   - **AODV**: Address black hole attacks through sequence number validation to ensure route authenticity.
   - **DSR**: Address stale route caching by implementing cache expiration mechanisms.
   - **OLSR**: Address topology control message modification by introducing message integrity checks.
4. **GUI Development**: Create a graphical user interface (GUI) for visualizing the network topology, protocol dynamics, and real-time performance metrics during simulation.
5. **Documentation and Reporting**: Provide comprehensive documentation, including technical details of protocol implementations, analysis results, and user instructions for the simulation environment.

---

## Protocols and Reference RFCs / Research Papers
1. **DSDV**:
   - **Description**: A proactive routing protocol that maintains routing tables in all nodes, with frequent updates to ensure accurate routing information.
   - **Primary Reference**: Perkins and Bhagwat’s research paper, "Highly Dynamic Destination-Sequenced Distance-Vector Routing (DSDV) for Mobile Computers" (1994).
   - **Problem Addressed**: High control overhead due to constant table updates in dynamic networks.
   
2. **AODV**:
   - **Description**: A reactive, on-demand routing protocol that discovers routes only when needed, minimizing unnecessary control messages.
   - **RFC**: RFC 3561
   - **Problem Addressed**: Vulnerability to black hole attacks, where a malicious node falsely advertises optimal routes to intercept data packets.

3. **DSR**:
   - **Description**: A source-routing protocol that allows nodes to cache source routes, making route discovery more efficient but increasing header size.
   - **RFC**: RFC 4728
   - **Problem Addressed**: Stale route caching, which leads to routing errors when network topology changes.

4. **OLSR**:
   - **Description**: A proactive, link-state routing protocol optimized for MANETs, using multipoint relays (MPRs) to reduce the number of transmissions needed.
   - **RFC**: RFC 3626
   - **Problem Addressed**: Vulnerability to topology control (TC) message modification, which can lead to inaccurate network maps.

---

## Technical Stack
1. **Programming Language**: Python
   - For its ease of use in network simulation, data handling, and testing, as well as its rich library support.
2. **Libraries and Frameworks**:
   - **Tkinter / PyQt**: For GUI development to visualize network topologies and protocol metrics.
   - **NetworkX**: To model the network graph, helping in route calculations and visualizations.
   - **Matplotlib / Plotly**: For data visualization to represent performance metrics like throughput, latency, and packet delivery ratio.
   - **Socket Programming (if needed)**: To simulate packet transmission between nodes.
3. **Data Analysis and Visualization**:
   - **Pandas**: For handling and analyzing data collected during simulation.
   - **Matplotlib** and **Plotly**: For generating graphs to compare protocol performance.

---

## Implementation Details
1. **Simulation Environment**:
   - A simulated MANET environment will be created, with nodes represented as vertices and communication links as edges.
   - Nodes will use implemented protocol rules to update routing tables, discover routes, and exchange data.
2. **GUI Features**:
   - **Topology Visualization**: Display the network topology with nodes and links.
   - **Metrics Display**: Show real-time statistics on protocol performance, including throughput, latency, and control overhead.
   - **Attack Simulation**: Enable toggling of protocol attacks (e.g., black hole in AODV) to observe effects on performance.
3. **Data Collection and Analysis**:
   - Simulated data will be logged and processed for each protocol, capturing metrics over time and across different network conditions.
   - Graphs and tables will be generated to represent comparative analysis results.

---

## Expected Outcomes
1. **Functional Implementations**: Working implementations of DSDV, AODV, DSR, and OLSR, validated through simulation and metric collection.
2. **Comparative Analysis**: A detailed analysis report covering throughput, latency, packet delivery ratio, control overhead, and routing load for each protocol.
3. **Security Analysis**: Insights into protocol vulnerabilities, showing the effect of attacks like black hole in AODV, with proposed mitigation effectiveness.
4. **Visualization and Reporting**: A GUI for network topology visualization, real-time metric display, and an automated report generator for comparative analysis.

---

## Conclusion
This project provides a comprehensive exploration of key MANET routing protocols by implementing, analyzing, and enhancing protocol performance and resilience. The work contributes to a deeper understanding of protocol behavior under typical and adverse conditions and highlights the importance of addressing security vulnerabilities to improve MANET robustness. The project also serves as a practical guide for network protocol design and evaluation, useful for researchers, engineers, and students in networking fields.

