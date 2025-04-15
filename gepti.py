import random
import networkx as nx
import matplotlib.pyplot as plt

# Globalne parametry
NUM_NODES = 20
EXTRA_EDGES = 5  # cykl (20 krawędzi) + kilka dodatkowych (<30 krawędzi)

# Parametry przepływu i opóźnienia
m = 1000       # średnia wielkość pakietu w bitach
T_max = 0.5    # maksymalne dopuszczalne opóźnienie
p = 0.95       # prawdopodobieństwo, że dana krawędź działa

def create_graph():
    """
    Tworzy graf G o 20 wierzchołkach:
      - Najpierw budowany jest cykl, aby każdy wierzchołek miał co najmniej dwa połączenia.
      - Następnie dodajemy losowo dodatkowe krawędzie (EXTRA_EDGES), zachowując warunek, że |E| < 30.
      
    Każdej krawędzi przypisywane są dwa atrybuty:
      - capacity: przepustowość w bitach/s (losowo z przedziału 5000–10000),
      - cost: koszt/kryterium używane przy wyszukiwaniu najkrótszej ścieżki (losowo z przedziału 1–10).
    """
    G = nx.Graph()
    for i in range(NUM_NODES):
        G.add_node(i)
        
    # Dodajemy cykl
    for i in range(NUM_NODES):
        u = i
        v = (i + 1) % NUM_NODES
        cap = random.randint(5000, 10000)
        cost = random.randint(1, 10)
        G.add_edge(u, v, capacity=cap, cost=cost)
    
    # Dodajemy dodatkowe krawędzie
    added = 0
    while added < EXTRA_EDGES:
        u = random.randint(0, NUM_NODES - 1)
        v = random.randint(0, NUM_NODES - 1)
        if u != v and not G.has_edge(u, v):
            cap = random.randint(5000, 10000)
            cost = random.randint(1, 10)
            G.add_edge(u, v, capacity=cap, cost=cost)
            added += 1
    return G

def create_flow_matrix():
    """
    Generuje macierz natężeń N (reprezentowaną jako słownik)
    dla każdej pary (i, j) (i ≠ j) z prawdopodobieństwem 0.2 przyjmuje ruch 1 pakiet/s,
    w przeciwnym razie ruch wynosi 0.
    """
    N = {}
    for i in range(NUM_NODES):
        for j in range(NUM_NODES):
            if i != j:
                N[(i, j)] = 1 if random.random() < 0.2 else 0
    return N

def compute_routing_flows(G, N):
    """
    Dla danego grafu G i macierzy przepływów N oblicza rzeczywiste przepływy a(e) na krawędziach.
    Dla każdej pary (src, dst) z N[src, dst] > 0 wyszukuje najkrótszą ścieżkę 
    (wg atrybutu 'cost') i dodaje wartość n(src,dst) do każdej krawędzi na tej ścieżce.
    
    Zwraca słownik flow_on_edge, gdzie kluczem jest krotka (u, v) (uporządkowana – mniejsze pierwsze),
    oraz całkowity ruch (suma n(i,j)).
    
    Jeśli dla którejkolwiek pary nie uda się znaleźć ścieżki (np. graf nie jest spójny), zwraca (None, None).
    """
    # Inicjujemy przepływy na krawędziach
    flow_on_edge = {}
    for u, v, attr in G.edges(data=True):
        key = tuple(sorted((u, v)))
        flow_on_edge[key] = 0
    
    total_flow = 0
    for (src, dst), flow in N.items():
        if flow > 0:
            try:
                path = nx.shortest_path(G, source=src, target=dst, weight='cost')
            except nx.NetworkXNoPath:
                return None, None
            total_flow += flow
            # Rozkładamy flow po krawędziach na ścieżce
            for i in range(len(path) - 1):
                edge = tuple(sorted((path[i], path[i+1])))
                flow_on_edge[edge] += flow
    return flow_on_edge, total_flow

def compute_delay(G, flow_on_edge, total_flow, m):
    """
    Oblicza średnie opóźnienie T wg wzoru:
       T = 1/G_total * SUM_e ( a(e) / ( (c(e)/m) - a(e) ) )
    G_total to suma ruchu ze wszystkich par (macierzy N).
    
    Jeżeli dla którejkolwiek krawędzi a(e) >= c(e)/m (czyli przepływ przekracza dopuszczalną wartość),
    funkcja zwraca nieskończoność.
    """
    if total_flow == 0:
        return float('inf')
    delay_sum = 0
    for u, v, attr in G.edges(data=True):
        key = tuple(sorted((u, v)))
        a_e = flow_on_edge[key]
        c_e = attr['capacity']
        max_packets = c_e / m  # maksymalny przepływ w pakietach/s
        if a_e >= max_packets:
            return float('inf')
        delay_sum += a_e / (max_packets - a_e)
    return delay_sum / total_flow

def simulate_reliability(G_full, N, p, T_max, m, iterations=1000):
    """
    Symuluje niezawodność sieci metodą Monte Carlo.
    Dla każdej iteracji:
      - Tworzy operacyjny podgraf G_oper, w którym każda krawędź działa z prawdopodobieństwem p.
      - Sprawdza, czy dla każdej pary (src, dst) z N[src,dst]>0 istnieje ścieżka.
      - Jeśli tak, oblicza dynamiczne przepływy i opóźnienie T.
      - Iteracja jest sukcesem, jeśli T < T_max.
      
    Funkcja zwraca stosunek sukcesów do liczby iteracji, dla których udało się wyznaczyć trasowanie.
    """
    success = 0
    valid_iterations = 0
    for _ in range(iterations):
        # Tworzymy operacyjny graf: losowo usuwamy krawędzie
        G_oper = nx.Graph()
        G_oper.add_nodes_from(G_full.nodes)
        for u, v, attr in G_full.edges(data=True):
            if random.random() <= p:
                G_oper.add_edge(u, v, **attr)
        # Dla każdej pary (src, dst) z ruchem sprawdzamy, czy jest ścieżka
        ok = True
        for (src, dst), flow in N.items():
            if flow > 0:
                if not nx.has_path(G_oper, src, dst):
                    ok = False
                    break
        if not ok:
            continue
        flows, total_flow = compute_routing_flows(G_oper, N)
        if flows is None:
            continue
        T = compute_delay(G_oper, flows, total_flow, m)
        valid_iterations += 1
        if T < T_max:
            success += 1
    if valid_iterations == 0:
        return 0
    return success / valid_iterations

def plot_graph(G, flow_on_edge):
    """
    Rysuje graf przy użyciu matplotlib. Na każdej krawędzi wypisuje:
      - a(e): obliczony przepływ dla pełnego grafu,
      - c(e): przepustowość krawędzi.
    """
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(12, 10))
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
    nx.draw_networkx_labels(G, pos)
    edge_labels = {}
    for u, v, attr in G.edges(data=True):
        key = tuple(sorted((u, v)))
        flow_val = flow_on_edge.get(key, 0)
        label = f"flow: {flow_val}\nc: {attr['capacity']}"
        edge_labels[(u, v)] = label
    nx.draw_networkx_edges(G, pos, width=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title("Topologia sieci (pełny graf z dynamicznymi przepływami)")
    plt.axis("off")
    plt.show()

def main():
    random.seed(42)
    
    # Tworzymy graf i macierz natężeń N
    G = create_graph()
    N = create_flow_matrix()
    
    print(f"Liczba wierzchołków: {G.number_of_nodes()}")
    print(f"Liczba krawędzi: {G.number_of_edges()}")
    
    # Baseline: obliczamy przepływy i opóźnienie dla pełnego (nieuszkodzonego) grafu
    flows, total_flow = compute_routing_flows(G, N)
    if flows is None:
        print("Brak ścieżki między niektórymi parami w pełnym grafie!")
        return
    T_full = compute_delay(G, flows, total_flow, m)
    print(f"Zagregowany ruch (suma n(i,j)): {total_flow}")
    print(f"Opóźnienie T w pełnym grafie: {T_full:.4f}")
    
    # Symulacja niezawodności przy dynamicznym trasowaniu
    reliability = simulate_reliability(G, N, p, T_max, m, iterations=1000)
    print(f"Oszacowana niezawodność sieci (T < T_max): {reliability:.4f}")
    
    # Rysujemy graf z wyliczonymi przepływami (baseline)
    plot_graph(G, flows)

if __name__ == "__main__":
    main()
