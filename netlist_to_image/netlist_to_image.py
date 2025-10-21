import re
import networkx as nx
import matplotlib.pyplot as plt

def parse_netlist(netlist_text):
    """
    Very basic parser for SPICE-like netlists.
    Extracts component name and connected nodes.
    """
    lines = netlist_text.strip().splitlines()
    components = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('*') or line.startswith('.'):
            continue  # skip comments and directives
        tokens = line.split()
        name = tokens[0]
        if len(tokens) >= 3:
            n1, n2 = tokens[1], tokens[2]
            components.append((name, n1, n2))
    return components


def netlist_to_graph(components):
    """
    Builds a graph using NetworkX with nodes as nets and edges as components.
    """
    G = nx.Graph()
    for name, n1, n2 in components:
        G.add_edge(n1, n2, label=name)
    return G


def draw_circuit(netlist_text, title="Circuit Diagram"):
    comps = parse_netlist(netlist_text)
    G = netlist_to_graph(comps)
    
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8,6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1200, font_size=10)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    plt.title(title)
    plt.axis('off')
    plt.show()


# Example usage
netlist_text = """
* Simple RC low-pass
V1 in 0 DC 5
R1 in out 1k
C1 out 0 100n
.tran 0 1m
.end
"""

nl2 = """
* Z:\mnt\spice-netlists\LT1054_TA14.asc
V1 IN 0 10
C1 N002 N005 100µ
XU1 N001 N002 0 N005 N006 N004 N003 IN LT1054
C2 IN 0 2µ
R1 N001 OUT 102K
R2 N001 N004 20K
C3 0 OUT 100µ Rser=10m
D1 N007 N006 1N914
C4 N006 0 100µ
D2 OUT N007 1N914
C5 N005 N007 10µ
C6 N001 OUT .002µ
Rload 0 OUT 50
.tran 5m startup
* LT1054 - Switched-Capacitor Voltage Converter with Regulator\nNegative Doubler with Regulator\nInput: 3.5V to 15V     Output: -5 @ 100mA
* Note:\n  If the simulation model is not found please update with the "Sync Release" command from the "Tools" menu.\n  It remains the customer's responsibility to verify proper and reliable operation in the actual application.\n  Component substitution and printed circuit board layout may significantly affect circuit performance or reliability\n  Contact your local sales representative for assistance. This circuit is distributed to customers only for use with LTC parts\n  Copyright © 2012 Linear Technology Inc. All rights reserved.
.backanno
.end
"""

draw_circuit(nl2)
