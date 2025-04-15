import random
import networkx as nx
import matplotlib.pyplot as plt

# ===================== STAŁE GLOBALNE =====================
NUM_NODES    = 20          # liczba wierzchołków
EXTRA_EDGES  = 5           # dodatkowych krawędzi obok cyklu (łącznie: cykl + EXTRA_EDGES < 30)
CAPACITY_MIN = 40000       # minimalna przepustowość krawędzi [bit/s]
CAPACITY_MAX = 70000      # maksymalna przepustowość krawędzi [bit/s]
COST_MIN     = 1           # minimalny koszt krawędzi
COST_MAX     = 10          # maksymalny koszt krawędzi
PACKET_SIZE  = 1000        # średni rozmiar pakietu w bitach (m)
T_MAX        = 0.5         # maksymalne dopuszczalne opóźnienie (T_max)
EDGE_RELIABILITY = 0.7   # prawdopodobieństwo, że krawędź działa
FLOW_PROB    = 0.2         # prawdopodobieństwo, że między daną parą (i,j) jest ruch (wartość 1 pakiet/s)
MC_ITER      = 1000        # liczba iteracji Monte Carlo do symulacji niezawodności
# ============================================================

def create_graph():
    """
    Tworzy graf G o NUM_NODES wierzchołkach:
      - Najpierw budowany jest cykl, aby zapewnić, że żaden wierzchołek nie jest izolowany.
      - Następnie dodajemy EXTRA_EDGES losowych krawędzi (przy czym |E| < 30).
      
    Każdej krawędzi przypisujemy:
      - capacity: przepustowość (w bitach/s) z zakresu [CAPACITY_MIN, CAPACITY_MAX]
      - cost: koszt używany przy wyszukiwaniu ścieżki, losowany z zakresu [COST_MIN, COST_MAX]
    """
    G = nx.Graph()
    for i in range(NUM_NODES):
        G.add_node(i)
        
    # Tworzymy cykl (zapewnia spójność podstawową)
    for i in range(NUM_NODES):
        u = i
        v = (i + 1) % NUM_NODES
        cap = random.randint(CAPACITY_MIN, CAPACITY_MAX)
        cost = random.randint(COST_MIN, COST_MAX)
        G.add_edge(u, v, capacity=cap, cost=cost)
    
    # Dodajemy dodatkowe krawędzie
    added = 0
    while added < EXTRA_EDGES:
        u = random.randint(0, NUM_NODES - 1)
        v = random.randint(0, NUM_NODES - 1)
        if u != v and not G.has_edge(u, v):
            cap = random.randint(CAPACITY_MIN, CAPACITY_MAX)
            cost = random.randint(COST_MIN, COST_MAX)
            G.add_edge(u, v, capacity=cap, cost=cost)
            added += 1
    return G

def create_flow_matrix():
    """
    Generuje macierz natężeń N (reprezentowaną jako słownik).
    Dla każdej pary (i, j), przy i != j, z prawdopodobieństwem FLOW_PROB
    przydziela się ruch równy 1 pakiet/s, w przeciwnym razie 0.
    """
    N = {}
    for i in range(NUM_NODES):
        for j in range(NUM_NODES):
            if i != j:
                N[(i, j)] = 1 if random.random() < FLOW_PROB else 0
    return N

def compute_routing_flows(G, N):
    """
    Dla danego grafu G i macierzy natężeń N oblicza rzeczywiste przepływy a(e) na krawędziach.
    Dla każdej pary (src, dst) z N[src,dst] > 0 wyszukuje najkrótszą ścieżkę wg atrybutu 'cost'
    i dodaje wartość n(src,dst) do każdej krawędzi na tej ścieżce.
    
    Zwraca:
      - flow_on_edge: słownik, gdzie kluczem jest uporządkowana krotka (u, v) a wartością suma ruchu
      - total_flow: całkowity ruch (suma n(i,j)) wszystkich par
    Jeśli dla którejś pary nie uda się znaleźć ścieżki, zwraca (None, None).
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
            # Dodajemy ruch do każdej krawędzi na znalezionej ścieżce
            for i in range(len(path) - 1):
                key = tuple(sorted((path[i], path[i+1])))
                flow_on_edge[key] += flow
    
    # Znajdź największy przepływ
    # max_flow_edge = max(flow_on_edge, key=flow_on_edge.get)
    # max_flow_value = flow_on_edge[max_flow_edge]
    # print(f"Największy przepływ: {max_flow_value} na krawędzi {max_flow_edge}")
    
    return flow_on_edge, total_flow

def compute_delay(G, flow_on_edge, total_flow, m):
    """
    Oblicza średnie opóźnienie T wg wzoru:
         T = (1/total_flow) * SUM_e ( a(e) / ( (c(e)/m) - a(e) ) )
    Dla każdej krawędzi:
         max_flow = c(e)/m  (maksymalny przepływ, który krawędź jest w stanie obsłużyć)
    Jeśli dla którejkolwiek krawędzi a(e) >= max_flow, funkcja zwraca nieskończoność.
    """
    if total_flow == 0:
        return float('inf')
    delay_sum = 0
    for u, v, attr in G.edges(data=True):
        key = tuple(sorted((u, v)))
        a_e = flow_on_edge[key]
        c_e = attr['capacity']
        max_flow = c_e / m  # maksymalny ruch w pakietach/s
        if a_e >= max_flow:
            return float('inf')
        delay_sum += a_e / (max_flow - a_e)
    return delay_sum / total_flow

COUNT = 0

def simulate_reliability(G_full, N, p, T_max, m, iterations=MC_ITER):
    global COUNT
    """
    Symuluje niezawodność sieci metodą Monte Carlo.
    Dla każdej iteracji:
      - Tworzy operacyjny podgraf G_oper, w którym każda krawędź działa z prawdopodobieństwem p.
      - Sprawdza, czy dla każdej pary (src, dst) z ruchem istnieje ścieżka.
      - Jeśli tak, oblicza dynamiczne przepływy i opóźnienie T.
      - Iteracja jest sukcesem, jeśli T < T_max.
      
    Zwraca stosunek sukcesów do liczby iteracji, w których trasowanie było możliwe.
    """
    success = 0
    valid_iterations = 0
    for _ in range(iterations):
        # Losujemy operacyjny graf: każda krawędź działa z prawdopodobieństwem p.
        G_oper = nx.Graph()
        G_oper.add_nodes_from(G_full.nodes)
        for u, v, attr in G_full.edges(data=True):
            if random.random() <= p:
                G_oper.add_edge(u, v, **attr)
        # Sprawdzamy, czy dla wszystkich par z ruchem istnieje ścieżka
        ok = True
        for (src, dst), flow in N.items():
            if flow > 0:
                if not nx.has_path(G_oper, src, dst):
                    ok = False
                    break
        flows, total_flow = compute_routing_flows(G_oper, N)
        if flows is None:
            continue
        if not ok:
            COUNT+=1
            if(COUNT < 10):
                plot_graph(G_oper, flows)
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
    Rysuje graf przy użyciu matplotlib.
    Na krawędzi wypisuje:
      - flow: obliczony dynamiczny przepływ (a(e)),
      - capacity: przepustowość krawędzi.
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
    plt.title("Topologia sieci (dynamiczne przepływy)")
    plt.axis("off")
    plt.show()

def main():
    random.seed(42)
    
    # Tworzymy graf oraz macierz natężeń N
    G = create_graph()
    N = create_flow_matrix()
    
    print(f"Liczba wierzchołków: {G.number_of_nodes()}")
    print(f"Liczba krawędzi: {G.number_of_edges()}")
    
    # Baseline: dynamiczne trasowanie w pełnym grafie (bez uszkodzeń)
    flows, total_flow = compute_routing_flows(G, N)
    if flows is None:
        print("Brak ścieżki pomiędzy niektórymi parami w pełnym grafie!")
        return
    T_full = compute_delay(G, flows, total_flow, PACKET_SIZE)
    print(f"Zagregowany ruch (suma n(i,j)): {total_flow}")
    print(f"Opóźnienie T w pełnym grafie: {T_full:.4f}")
    
    # Symulacja niezawodności (Monte Carlo)
    reliability = simulate_reliability(G, N, EDGE_RELIABILITY, T_MAX, PACKET_SIZE, iterations=MC_ITER)
    print(f"Oszacowana niezawodność sieci (T < T_MAX): {reliability:.4f}")
    
    # Rysujemy graf z dynamicznie wyliczonymi przepływami (baseline)
    plot_graph(G, flows)

if __name__ == '__main__':
    main()
