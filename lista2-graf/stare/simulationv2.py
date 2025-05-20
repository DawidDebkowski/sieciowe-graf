import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random
import itertools

# Parametry
NUM_NODES = 20
MAX_EDGES = 30
T_max = 0.05
m = 1000  # średnia wielkość pakietu w bitach
NUM_SIM = 100

# Tworzenie grafu losowego bez izolowanych wierzchołków
G = nx.gnm_random_graph(NUM_NODES, MAX_EDGES)
while not nx.is_connected(G):
    G = nx.gnm_random_graph(NUM_NODES, MAX_EDGES)

# Losowanie macierzy N (natężeń) – na początek niewielkie wartości
N = np.zeros((NUM_NODES, NUM_NODES))
for i in range(NUM_NODES):
    for j in range(NUM_NODES):
        if i != j:
            N[i][j] = random.randint(0, 5)

# Funkcje przepustowości c(e) i przepływu a(e)
c_dict_original = {}
a_dict = {}
for edge in G.edges():
    c = random.randint(20000, 30000)  # bity na sekundę
    c_dict_original[tuple(sorted(edge))] = c

a_dict = {e: random.randint(100, 300) for e in G.edges()}  # pakiety na sekundę

# Dodanie niezawodności dla każdej krawędzi
p_dict_original = {}
for edge in c_dict_original:
    p_dict_original[edge] = random.uniform(0.90, 0.99)

# Funkcja do liczenia średniego opóźnienia T
def compute_average_delay(G_sub, N_mat, c_dict, num_nodes, m, G_total):
    a_dict_local = {}
    for edge in G_sub.edges():
        a = 0
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j and nx.has_path(G_sub, i, j):
                    path = nx.shortest_path(G_sub, source=i, target=j)
                    for k in range(len(path) - 1):
                        if tuple(sorted((path[k], path[k+1]))) == tuple(sorted(edge)):
                            a += N_mat[i][j] / len(path)
        a_dict_local[tuple(sorted(edge))] = a

    T = 0
    for edge in G_sub.edges():
        edge_key = tuple(sorted(edge))
        a = a_dict_local[edge_key]
        c = c_dict[edge_key]
        if c > a * m:
            T += a / ((c / m) - a)
        else:
            T += float('inf')

    return T / G_total if G_total > 0 else float('inf')

# Symulacja niezawodności

def simulate_reliability(G_full, N_mat, c_dict, p_dict, T_max, m, num_sim, num_nodes):
    G_total = np.sum(N_mat)
    successes = 0
    valid_trials = 0

    for _ in range(num_sim):
        G_trial = nx.Graph()
        G_trial.add_nodes_from(G_full.nodes())

        for edge in G_full.edges():
            p_e = p_dict[tuple(sorted(edge))]
            if random.random() < p_e:
                G_trial.add_edge(*edge)

        if not nx.is_connected(G_trial):
            continue

        valid_trials += 1
        T_trial = compute_average_delay(G_trial, N_mat, c_dict, num_nodes, m, G_total)

        if T_trial < T_max:
            successes += 1

    return successes / valid_trials if valid_trials > 0 else 0.0

# Wyświetlanie grafu
def draw_graph(G, c_dict, p_dict):
    pos = nx.spring_layout(G)
    edge_labels = {edge: f"c={c_dict[tuple(sorted(edge))]}\np={p_dict[tuple(sorted(edge))]:.2f}" for edge in G.edges()}
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
    plt.title("Topologia sieci z przepustowościami i niezawodnościami")
    plt.show()

print("start")

# Eksperyment 1: zwiększanie natężeń
reliabilities_exp1 = []
for scale in np.linspace(1, 5, 10):
    N_scaled = N * scale
    r = simulate_reliability(G, N_scaled, c_dict_original, p_dict_original, T_max, m, NUM_SIM, NUM_NODES)
    reliabilities_exp1.append(r)

# # Eksperyment 2: zwiększanie przepustowości
# reliabilities_exp2 = []
# for scale in np.linspace(1, 5, 10):
#     c_scaled = {e: int(c * scale) for e, c in c_dict_original.items()}
#     r = simulate_reliability(G, N, c_scaled, p_dict_original, T_max, m, NUM_SIM, NUM_NODES)
#     reliabilities_exp2.append(r)

# # Eksperyment 3: dodawanie nowych krawędzi
# reliabilities_exp3 = []
# G_exp3 = G.copy()
# c_dict_exp3 = c_dict_original.copy()
# p_dict_exp3 = p_dict_original.copy()
# available_edges = list(itertools.combinations(range(NUM_NODES), 2))
# random.shuffle(available_edges)
# new_edges_added = 0
# avg_capacity = int(np.mean(list(c_dict_original.values())))

# while new_edges_added < 10:
#     for e in available_edges:
#         if e not in G_exp3.edges() and tuple(reversed(e)) not in G_exp3.edges():
#             G_exp3.add_edge(*e)
#             c_dict_exp3[e] = avg_capacity
#             p_dict_exp3[e] = random.uniform(0.90, 0.99)
#             new_edges_added += 1
#             r = simulate_reliability(G_exp3, N, c_dict_exp3, p_dict_exp3, T_max, m, NUM_SIM, NUM_NODES)
#             reliabilities_exp3.append(r)
#             break

# Wizualizacja grafu z opisem krawędzi
draw_graph(G, c_dict_original, p_dict_original)

# Wykresy zmian niezawodności
plt.figure(figsize=(12, 5))
plt.subplot(1, 3, 1)
plt.plot(np.linspace(1, 5, 10), reliabilities_exp1, marker='o')
plt.title("Niezawodność vs Natężenia")
plt.xlabel("Skalowanie natężeń")
plt.ylabel("Pr[T < T_max]")

# plt.subplot(1, 3, 2)
# plt.plot(np.linspace(1, 5, 10), reliabilities_exp2, marker='o', color='green')
# plt.title("Niezawodność vs Przepustowości")
# plt.xlabel("Skalowanie przepustowości")

# plt.subplot(1, 3, 3)
# plt.plot(range(1, len(reliabilities_exp3) + 1), reliabilities_exp3, marker='o', color='red')
# plt.title("Niezawodność vs Liczba dodanych krawędzi")
# plt.xlabel("Nowe krawędzie")

plt.tight_layout()
plt.show()
