#!/usr/bin/env python3
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scapy.all import *  # Scapy – przykładowy import dla narzędzi sieciowych

# ------------------------
# Parametry początkowe
# ------------------------
NUM_NODES = 20       # liczba wierzchołków
NUM_EDGES = 25       # liczba krawędzi (< 30)
p = 0.95             # prawdopodobieństwo, że dana krawędź nie ulegnie uszkodzeniu
T_max = 0.05         # maksymalne akceptowalne opóźnienie
m = 1000             # średnia wielkość pakietu w bitach
MARGIN = 1.5         # margines przy ustalaniu przepustowości

NUM_SIM = 5000       # liczba iteracji Monte Carlo

# ------------------------
# Funkcje symulacyjne
# ------------------------
def compute_average_delay(G_sub, N_mat, c_dict, num_nodes, m, G_total):
    """
    Dla sprawnej sieci (spójnego podgrafu) przeliczamy przepływ na każdej krawędzi
    korzystając z macierzy natężeń N_mat.
    Obliczamy opóźnienie T wg wzoru:
      T = (1/G_total) * sum_e [ a(e) / ( c(e)/m - a(e) ) ]
    Jeżeli dla którejś krawędzi a(e) >= c(e)/m, zwracamy +inf.
    """
    # Inicjujemy przepływy na krawędziach (tylko dla krawędzi znajdujących się w pierwotnej strukturze)
    a_trial = {edge: 0 for edge in c_dict.keys()}
    
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j:
                try:
                    path = nx.shortest_path(G_sub, source=i, target=j)
                    for k in range(len(path)-1):
                        edge = tuple(sorted((path[k], path[k+1])))
                        if edge in a_trial:
                            a_trial[edge] += N_mat[i][j]
                except nx.NetworkXNoPath:
                    return float('inf')
    
    total_delay = 0
    for edge, a_val in a_trial.items():
        capacity = c_dict[edge]
        capacity_in_packets = capacity / m
        if a_val >= capacity_in_packets:
            return float('inf')
        total_delay += a_val / (capacity_in_packets - a_val)
    return total_delay / G_total

def simulate_reliability(G_full, N_mat, c_dict, p, T_max, m, num_sim, num_nodes):
    """
    Przeprowadza symulację Monte Carlo dla danej konfiguracji:
      - G_full: początkowy graf
      - N_mat: macierz natężeń
      - c_dict: słownik przepustowości dla krawędzi
      - p: prawdopodobieństwo nieuszkodzenia krawędzi
      - T_max: maksymalne opóźnienie
      - m: średnia wielkość pakietu
      - num_sim: liczba prób symulacyjnych
      - num_nodes: liczba wierzchołków
    Zwraca niezawodność jako stosunek prób, gdzie T < T_max, do prób przy spójnej sieci.
    """
    G_total = np.sum(N_mat)
    successes = 0
    valid_trials = 0
    
    for _ in range(num_sim):
        G_trial = nx.Graph()
        G_trial.add_nodes_from(G_full.nodes())
        for edge in G_full.edges():
            if random.random() < p:
                G_trial.add_edge(*edge)
        if not nx.is_connected(G_trial):
            continue
        valid_trials += 1
        T_trial = compute_average_delay(G_trial, N_mat, c_dict, num_nodes, m, G_total)
        if T_trial < T_max:
            successes += 1
    if valid_trials > 0:
        return successes / valid_trials
    else:
        return 0.0

# ------------------------
# Budowa początkowej topologii sieci
# ------------------------
G_full = nx.Graph()
G_full.add_nodes_from(range(NUM_NODES))

# Generujemy drzewo rozpinające, aby żaden wierzchołek nie był izolowany
random_weights = {(i, j): random.random() for i in range(NUM_NODES) for j in range(i + 1, NUM_NODES)}
G_complete = nx.Graph()
G_complete.add_nodes_from(range(NUM_NODES))
G_complete.add_edges_from((u, v, {'weight': w}) for (u, v), w in random_weights.items())
T = nx.minimum_spanning_tree(G_complete, algorithm="kruskal")
G_full.add_edges_from(T.edges())

# Dodajemy losowe krawędzie aż do uzyskania zadanej liczby krawędzi
while G_full.number_of_edges() < NUM_EDGES:
    u = random.randint(0, NUM_NODES - 1)
    v = random.randint(0, NUM_NODES - 1)
    if u != v and not G_full.has_edge(u, v):
        G_full.add_edge(u, v)

print("Topologia początkowa:")
print("Liczba wierzchołków:", G_full.number_of_nodes())
print("Liczba krawędzi:", G_full.number_of_edges())

# Rysujemy graf
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G_full, seed=42)
nx.draw(G_full, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=500)
plt.title("Początkowa topologia sieci")
plt.show()

# ------------------------
# Generacja początkowej macierzy natężeń N
# ------------------------
N_original = np.zeros((NUM_NODES, NUM_NODES), dtype=float)
for i in range(NUM_NODES):
    for j in range(NUM_NODES):
        if i != j:
            N_original[i][j] = random.randint(1, 5)
G_total_original = np.sum(N_original)
print("Suma pakietów w N (G):", G_total_original)

# ------------------------
# Obliczenie przepływów a(e) oraz ustalenie przepustowości c(e)
# ------------------------
a_dict = {}  # klucz: uporządkowana krawędź, wartość: przepływ (pak/s)
for edge in G_full.edges():
    edge_key = tuple(sorted(edge))
    a_dict[edge_key] = 0

for i in range(NUM_NODES):
    for j in range(NUM_NODES):
        if i != j:
            try:
                path = nx.shortest_path(G_full, source=i, target=j)
                for k in range(len(path)-1):
                    edge = tuple(sorted((path[k], path[k+1])))
                    a_dict[edge] += N_original[i][j]
            except nx.NetworkXNoPath:
                pass

# Ustalamy przepustowości c(e) dla każdej krawędzi
c_dict_original = {}
for edge, flow in a_dict.items():
    if flow == 0:
        c_dict_original[edge] = m
    else:
        c_dict_original[edge] = m * flow * MARGIN

# Symulacja bazowa
reliability_base = simulate_reliability(G_full, N_original, c_dict_original, p, T_max, m, NUM_SIM, NUM_NODES)
print("Bazowa niezawodność (Pr[T < T_max]): {:.2%}".format(reliability_base))

# ------------------------
# Eksperyment 1: Skalowanie macierzy natężeń N
# (stała topologia i przepustowości, zwiększamy intensywność ruchu)
# ------------------------
scale_factors_N = np.linspace(1.0, 3.0, 9)  # np. 1.0, 1.25, ..., 3.0
reliability_exp1 = []
for factor in scale_factors_N:
    N_scaled = N_original * factor
    rel = simulate_reliability(G_full, N_scaled, c_dict_original, p, T_max, m, NUM_SIM, NUM_NODES)
    reliability_exp1.append(rel)
    print("Skala natężenia = {:.2f}, niezawodność = {:.2%}".format(factor, rel))

plt.figure(figsize=(8,6))
plt.plot(scale_factors_N, reliability_exp1, marker='o')
plt.xlabel("Skalowanie macierzy natężeń N")
plt.ylabel("Niezawodność (Pr[T < T_max])")
plt.title("Eksperyment 1: Wpływ zwiększenia natężenia ruchu")
plt.grid(True)
plt.show()

# ------------------------
# Eksperyment 2: Skalowanie przepustowości c(e)
# (stała macierz natężeń i topologia, zwiększamy przepustowości)
# ------------------------
scale_factors_c = np.linspace(1.0, 3.0, 9)
reliability_exp2 = []
for factor in scale_factors_c:
    # Skalujemy przepustowości – macierz intensywności N pozostaje bez zmian
    c_scaled = {edge: c_dict_original[edge] * factor for edge in c_dict_original}
    rel = simulate_reliability(G_full, N_original, c_scaled, p, T_max, m, NUM_SIM, NUM_NODES)
    reliability_exp2.append(rel)
    print("Skala przepustowości = {:.2f}, niezawodność = {:.2%}".format(factor, rel))

plt.figure(figsize=(8,6))
plt.plot(scale_factors_c, reliability_exp2, marker='o', color='green')
plt.xlabel("Skalowanie przepustowości c(e)")
plt.ylabel("Niezawodność (Pr[T < T_max])")
plt.title("Eksperyment 2: Wpływ zwiększenia przepustowości")
plt.grid(True)
plt.show()

# ------------------------
# Eksperyment 3: Zmiana topologii – dodawanie nowych krawędzi
# (przy ustalonej macierzy N, dodajemy nowe krawędzie o przepustowości = średnia przepustowości z początkowego grafu)
# ------------------------
# Obliczamy średnią przepustowość na krawędzi z początkowego grafu
avg_capacity = np.mean(list(c_dict_original.values()))

# Na potrzeby eksperymentu wykonamy kopię początkowego grafu
G_exp3 = G_full.copy()
c_dict_exp3 = c_dict_original.copy()
# Lista wszystkich możliwych krawędzi (bez pętli) w grafie 20-wierzchołkowym
possible_edges = [tuple(sorted((i,j))) for i in range(NUM_NODES) for j in range(i+1, NUM_NODES)]
# Wykluczamy już istniejące krawędzie
available_edges = [e for e in possible_edges if e not in G_exp3.edges()]
num_edges_to_add = min(10, len(available_edges))  # dodamy maksymalnie 10 krawędzi

reliability_exp3 = []
added_edges = []
for i in range(num_edges_to_add+1):
    # Symulujemy niezawodność dla bieżącej topologii
    rel = simulate_reliability(G_exp3, N_original, c_dict_exp3, p, T_max, m, NUM_SIM, NUM_NODES)
    reliability_exp3.append(rel)
    print("Dodanych krawędzi = {}, niezawodność = {:.2%}".format(i, rel))
    # Dodajemy jedną krawędź, jeśli jeszcze mamy dostępne
    if i < num_edges_to_add:
        new_edge = available_edges[i]
        G_exp3.add_edge(*new_edge)
        c_dict_exp3[new_edge] = avg_capacity  # przepustowość nowej krawędzi = średnia z początkowego grafu
        added_edges.append(new_edge)

plt.figure(figsize=(8,6))
plt.plot(range(num_edges_to_add+1), reliability_exp3, marker='o', color='red')
plt.xlabel("Liczba dodanych krawędzi")
plt.ylabel("Niezawodność (Pr[T < T_max])")
plt.title("Eksperyment 3: Wpływ zmiany topologii (dodawanie krawędzi)")
plt.grid(True)
plt.show()
