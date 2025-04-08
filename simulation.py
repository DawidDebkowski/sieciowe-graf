#!/usr/bin/env python3
import random
import numpy as np
import networkx as nx
from scapy.all import *  # Scapy – wykorzystywane jako przykładowy import narzędzi sieciowych

# ------------------------
# Parametry symulacji
# ------------------------
NUM_NODES = 20       # liczba wierzchołków
NUM_EDGES = 25       # liczba krawędzi (< 30)
p = 0.95             # prawdopodobieństwo, że dana krawędź nie ulegnie uszkodzeniu w danym przedziale czasu
T_max = 0.05         # maksymalne opóźnienie, które uznajemy za akceptowalne (parametr)
m = 1000             # średnia wielkość pakietu w bitach
MARGIN = 1.5         # margines przy ustalaniu przepustowości (tak, aby c(e)/m > a(e) zawsze)

NUM_SIM = 5000       # liczba iteracji Monte Carlo

# ------------------------
# Budowa topologii sieci (graf G)
# ------------------------
# Tworzymy graf o NUM_NODES wierzchołkach
G_full = nx.Graph()
G_full.add_nodes_from(range(NUM_NODES))

# Aby żaden wierzchołek nie był izolowany, najpierw tworzymy drzewo rozpinające
T = nx.generators.trees.random_tree(NUM_NODES, seed=42)
G_full.add_edges_from(T.edges())

# Dodajemy losowe krawędzie aż osiągniemy żądaną liczbę NUM_EDGES (<30)
while G_full.number_of_edges() < NUM_EDGES:
    u = random.randint(0, NUM_NODES - 1)
    v = random.randint(0, NUM_NODES - 1)
    if u != v and not G_full.has_edge(u, v):
        G_full.add_edge(u, v)

print("Topologia grafu:")
print("Liczba wierzchołków:", G_full.number_of_nodes())
print("Liczba krawędzi:", G_full.number_of_edges())

# ------------------------
# Generacja macierzy natężeń N
# ------------------------
# Dla uproszczenia przyjmujemy, że dla każdej pary (i, j), i != j, wartość natężenia to losowa liczba pakietów na sekundę w przedziale [1, 5].
N_mat = np.zeros((NUM_NODES, NUM_NODES), dtype=int)
for i in range(NUM_NODES):
    for j in range(NUM_NODES):
        if i != j:
            N_mat[i][j] = random.randint(1, 5)

# Sumaryczna liczba pakietów (G_total) – wykorzystywana w wzorze na opóźnienie
G_total = np.sum(N_mat)
print("Suma pakietów w N (G):", G_total)

# ------------------------
# Obliczenie pierwotnego przepływu a(e) oraz ustalenie przepustowości c(e)
# ------------------------
# Dla każdej krawędzi będziemy sumować pakiety które przez nią przechodzą – wybieramy najkrótszą ścieżkę w pełnej sieci
a_dict = {}  # słownik, klucz: krawędź (u,v) uporządkowany (tuple sorted), wartość: przepływ (pak/s)
for edge in G_full.edges():
    edge_key = tuple(sorted(edge))
    a_dict[edge_key] = 0

# Dla każdej pary (i, j) wyznaczamy najkrótszą ścieżkę i zwiększamy przepływ dla każdej krawędzi na ścieżce
for i in range(NUM_NODES):
    for j in range(NUM_NODES):
        if i != j:
            try:
                path = nx.shortest_path(G_full, source=i, target=j)
                # Dla każdej pary kolejnych wierzchołków na ścieżce
                for k in range(len(path)-1):
                    edge = tuple(sorted((path[k], path[k+1])))
                    a_dict[edge] += N_mat[i][j]
            except nx.NetworkXNoPath:
                # Nie powinno się zdarzyć przy spójnym grafie
                pass

# Ustalamy przepustowość c(e) dla każdej krawędzi, pamiętając, że c(e)/m musi być większe niż a(e)
c_dict = {}
for edge, flow in a_dict.items():
    # Aby uniknąć problemu gdy flow == 0 (krawędź mogła nie być wykorzystana),
    # ustawiamy minimalną przepustowość równą m (czyli c(e)/m = 1)
    if flow == 0:
        c_dict[edge] = m
    else:
        c_dict[edge] = m * flow * MARGIN

# ------------------------
# Funkcja obliczająca średnie opóźnienie T dla danej konfiguracji sieci (przepływy liczone po reroutingu)
# ------------------------
def compute_average_delay(G_sub):
    """
    Dla sprawnej sieci (spójnego podgrafu) przeliczamy przepływ na każdej krawędzi,
    wybierając najkrótsze ścieżki dla ruchu między każdą parą wierzchołków.
    Obliczamy opóźnienie T wg wzoru:
      T = (1/G_total) * SUM_e [ a(e) / ( c(e)/m - a(e) ) ]
    Jeżeli dla którejś krawędzi a(e) >= c(e)/m, zwracamy opóźnienie równe +inf.
    """
    # Nowe przepływy – zainicjujemy zero dla krawędzi, ale tylko dla tych, które występują w oryginalnym grafie
    a_trial = {edge: 0 for edge in c_dict.keys()}
    
    # Dla każdej pary wierzchołków wyznaczamy ścieżkę w podgrafie G_sub (który jest spójny)
    for i in range(NUM_NODES):
        for j in range(NUM_NODES):
            if i != j:
                try:
                    path = nx.shortest_path(G_sub, source=i, target=j)
                    for k in range(len(path)-1):
                        edge = tuple(sorted((path[k], path[k+1])))
                        # Upewniamy się, że krawędź występowała w projekcie (powinna)
                        if edge in a_trial:
                            a_trial[edge] += N_mat[i][j]
                except nx.NetworkXNoPath:
                    # W teorii nie powinno wystąpić, jeśli G_sub jest spójny
                    return float('inf')
    
    # Obliczamy opóźnienie dla każdej krawędzi
    total_delay = 0
    for edge, a_val in a_trial.items():
        capacity = c_dict[edge]  # w bitach na sekundę
        # Przepustowość w jednostkach pakietów/s: c(e)/m
        capacity_in_packets = capacity / m
        # Jeżeli kanał jest przeładowany lub równy granicy, opóźnienie przyjmujemy jako nieskończoność
        if a_val >= capacity_in_packets:
            return float('inf')
        delay = a_val / (capacity_in_packets - a_val)
        total_delay += delay
    T = total_delay / G_total
    return T

# ------------------------
# Monte Carlo – szacowanie niezawodności
# ------------------------
successes = 0
valid_trials = 0  # liczba prób, gdzie sieć pozostała spójna

for sim in range(NUM_SIM):
    # Na bazie oryginalnego grafu G_full tworzymy podgraf z uszkodzonymi krawędziami
    G_trial = nx.Graph()
    G_trial.add_nodes_from(G_full.nodes())
    for edge in G_full.edges():
        if random.random() < p:
            G_trial.add_edge(*edge)
            
    # Sprawdzamy spójność
    if not nx.is_connected(G_trial):
        continue  # ta próba jest odrzucana – sieć jest rozspójna
    valid_trials += 1
    
    # Obliczamy średnie opóźnienie T
    T_trial = compute_average_delay(G_trial)
    if T_trial < T_max:
        successes += 1

if valid_trials > 0:
    reliability = successes / valid_trials
    print("\nSymulacja:")
    print("Liczba prób (spójnych konfiguracji):", valid_trials)
    print("Liczba prób z T < T_max:", successes)
    print("Szacowana niezawodność: {:.2%}".format(reliability))
else:
    print("We wszystkich próbach sieć była rozspójna.")
