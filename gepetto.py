import random
import networkx as nx
import matplotlib.pyplot as plt

# Ustalenia globalne (parametry)
NUM_NODES = 20
# Ustawiamy docelowo mniej niż 30 krawędzi
# W przykładzie: cykl (20) + kilka przekątnych (np. 5), co daje 25 krawędzi.
EXTRA_EDGES = 5

# Parametry przepływu i opóźnienia
# m - średnia wielkość pakietu (w bitach)
m = 1000  
# Parametr T_max (próg opóźnienia)
T_max = 0.5  
# p - prawdopodobieństwo, że dana krawędź nie ulegnie uszkodzeniu w dowolnym przedziale czasowym
p = 0.95  

# Funkcja tworząca przykładowy graf wraz z atrybutami na krawędziach
def create_graph():
    G = nx.Graph()  # przyjmujemy graf nieskierowany (dla uproszczenia testu)
    
    # Dodajemy wierzchołki
    for i in range(NUM_NODES):
        G.add_node(i)
        
    # Najpierw budujemy cykl, żeby żaden wierzchołek nie był izolowany.
    for i in range(NUM_NODES):
        u = i
        v = (i+1) % NUM_NODES
        # Losujemy przepustowość - np. pomiędzy 5000 a 10000 bit/s
        cap = random.randint(5000, 10000)
        # Losujemy przepływ - mniejszy niż przepustowość, np. między 100 a 90% przepustowości
        flow = random.randint(100, int(cap * 0.9))
        # Koszt - przykładowo losowo z przedziału 1 do 10
        cost = random.randint(1, 10)
        # Niezawodność danej krawędzi wynosi p (przekazany parametr)
        G.add_edge(u, v, capacity=cap, flow=flow, cost=cost, reliability=p)
    
    # Dodajemy EXTRA_EDGES dodatkowych krawędzi, dbając, żeby nie powstało więcej niż 30
    added = 0
    while added < EXTRA_EDGES:
        u = random.randint(0, NUM_NODES-1)
        v = random.randint(0, NUM_NODES-1)
        if u != v and not G.has_edge(u, v):
            cap = random.randint(5000, 10000)
            flow = random.randint(100, int(cap * 0.9))
            cost = random.randint(1, 10)
            G.add_edge(u, v, capacity=cap, flow=flow, cost=cost, reliability=p)
            added += 1
    return G

# Oblicza średnie opóźnienie T dla zadanej sieci (zakładamy, że liczymy tylko po aktywnych krawędziach)
def compute_delay(graph, m):
    # Sumujemy przepływy a(e) dla wszystkich krawędzi w grafie
    total_flow = sum(graph[u][v]['flow'] for u, v in graph.edges)
    # Aby uniknąć dzielenia przez zero, przyjmujemy że:
    if total_flow == 0:
        return float('inf')
    
    delay_sum = 0
    for u, v in graph.edges:
        a_e = graph[u][v]['flow']
        c_e = graph[u][v]['capacity']
        # Warunek: c(e) > a(e), ale mimo wszystko zabezpieczamy dzielenie
        if c_e <= a_e:
            return float('inf')
        delay_sum += a_e / ((c_e / m) - a_e)
    return delay_sum / total_flow

# Funkcja symulująca niezawodność sieci metodą Monte Carlo
def simulate_reliability(G_full, p, T_max, m, iterations=10000):
    success = 0
    for _ in range(iterations):
        # Tworzymy podgraf – usuwamy krawędzie, które "zepsuły się"
        G_oper = nx.Graph()
        G_oper.add_nodes_from(G_full.nodes)
        for u, v, attr in G_full.edges(data=True):
            # Dla każdej krawędzi sprawdzamy, czy działa
            if random.random() <= p:
                G_oper.add_edge(u, v, **attr)
        # Sprawdzamy spójność grafu – jeśli graf nie jest spójny, przyjmujemy, że sieć nie spełnia warunków
        if not nx.is_connected(G_oper):
            continue
        # Obliczamy opóźnienie T dla podgrafu operacyjnego
        T = compute_delay(G_oper, m)
        if T < T_max:
            success += 1
    return success / iterations

# Funkcja rysująca graf
def plot_graph(G):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 8))
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
    nx.draw_networkx_labels(G, pos)
    # Rysujemy etykiety krawędzi: możemy wypisać np. wartość przepływu
    edge_labels = {(u, v): f"a:{G[u][v]['flow']}\nc:{G[u][v]['capacity']}" for u, v in G.edges}
    nx.draw_networkx_edges(G, pos, width=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title("Topologia sieci")
    plt.axis("off")
    plt.show()

def main():
    # Ustalamy ziarno, żeby wyniki były powtarzalne
    random.seed(42)
    
    # Tworzymy graf
    G = create_graph()
    print(f"Liczba wierzchołków: {G.number_of_nodes()}")
    print(f"Liczba krawędzi: {G.number_of_edges()}")
    
    # Obliczamy opóźnienie dla pełnej (bez uszkodzeń) sieci
    T_full = compute_delay(G, m)
    # Obliczamy zagregowaną intensywność przepływów (możemy przyjąć, że G = suma flow na wszystkich krawędziach)
    G_intensity = sum(data['flow'] for u, v, data in G.edges(data=True))
    print(f"Zagregowana intensywność przepływów G: {G_intensity}")
    print(f"Opóźnienie T dla pełnej sieci: {T_full:.4f}")
    
    # Symulacja niezawodności
    iterations = 10000  # liczba prób Monte Carlo
    reliability = simulate_reliability(G, p, T_max, m, iterations)
    print(f"Oszacowana niezawodność sieci (prawdopodobieństwo, że T < T_max i sieć jest spójna): {reliability:.4f}")
    
    # Rysujemy graf
    plot_graph(G)

if __name__ == '__main__':
    main()
