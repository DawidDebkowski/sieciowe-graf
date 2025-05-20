import random
import networkx as nx
import matplotlib.pyplot as plt

"""
    a - przepływ (w pakietach)
    c - przepustowość (w bitach)
    e - edge
"""

# Ustalenia globalne (parametry)
NUM_NODES = 20
# Ustawiamy docelowo mniej niż 30 krawędzi:
# W przykładzie: cykl (20) + kilka dodatkowych krawędzi (np. 5), co daje 25 krawędzi.
EXTRA_EDGES = 5

# Parametry przepływu i opóźnienia
m = 1000  # średnia wielkość pakietu (w bitach)
T_max = 0.5  # maksymalne dopuszczalne opóźnienie
p = 0.95  # prawdopodobieństwo, że dana krawędź nie ulegnie uszkodzeniu

T_SUM = 0
SIM_AMOUNT = 0

# Funkcja tworząca przykładowy graf wraz z atrybutami na krawędziach
def create_graph():
    G = nx.Graph()
    
    # Dodajemy wierzchołki
    for i in range(NUM_NODES):
        G.add_node(i)
        
    # Najpierw budujemy cykl, żeby żaden wierzchołek nie był izolowany.
    for i in range(NUM_NODES):
        u = i
        v = (i + 1) % NUM_NODES
        # Losujemy przepustowość - np. z przedziału 5000 do 10000 bit/s
        cap = random.randint(5000, 10000)
        # Wyliczamy maksymalną liczbę pakietów na sekundę możliwą do przesłania: cap/m
        max_packets = int(cap / m)
        # Losujemy przepływ, aby był mniejszy niż 90% maksymalnej liczby pakietów
        # Upewniamy się, że max_packets jest przynajmniej 1.
        flow = random.randint(1, max(1, int(max_packets * 0.9)))
        # Losujemy koszt (np. z przedziału 1 do 10)
        cost = random.randint(1, 10)
        G.add_edge(u, v, capacity=cap, flow=flow, cost=cost, reliability=p)
    
    # Dodajemy EXTRA_EDGES dodatkowych krawędzi, dbając, żeby nie przekroczyć 30
    added = 0
    while added < EXTRA_EDGES:
        u = random.randint(0, NUM_NODES - 1)
        v = random.randint(0, NUM_NODES - 1)
        if u != v and not G.has_edge(u, v):
            cap = random.randint(5000, 10000)
            max_packets = int(cap / m)
            flow = random.randint(1, max(1, int(max_packets * 0.9)))
            cost = random.randint(1, 10)
            G.add_edge(u, v, capacity=cap, flow=flow, cost=cost, reliability=p)
            added += 1
    return G

# Oblicza średnie opóźnienie T dla zadanej sieci (liczone tylko po aktywnych krawędziach)
def compute_delay(graph, m):
    # Zagregowany przepływ (suma a(e) dla wszystkich krawędzi)
    total_flow = sum(graph[u][v]['flow'] for u, v in graph.edges)
    if total_flow == 0:
        return float('inf')
    
    delay_sum = 0
    for u, v in graph.edges:
        a_e = graph[u][v]['flow']
        c_e = graph[u][v]['capacity']
        # Poprawiony warunek: sprawdzamy, czy liczba przesłanych pakietów jest mniejsza od maksymalnej liczby pakietów możliwych do przesłania
        if (c_e / m) <= a_e:
            return float('inf')
        delay_sum += a_e / ((c_e / m) - a_e)
    return delay_sum / total_flow

# Funkcja symulująca niezawodność sieci metodą Monte Carlo
def simulate_reliability(G_full, p, T_max, m, iterations=10000):
    global T_SUM, SIM_AMOUNT
    success = 0
    for _ in range(iterations):
        # Tworzymy podgraf – usuwamy krawędzie, które "zepsuły się"
        G_oper = nx.Graph()
        G_oper.add_nodes_from(G_full.nodes)
        for u, v, attr in G_full.edges(data=True):
            if random.random() <= p:
                G_oper.add_edge(u, v, **attr)
        # Sprawdzamy spójność grafu – jeśli graf nie jest spójny, symulacja ta nie liczy się jako sukces
        if not nx.is_connected(G_oper):
            continue
        # Obliczamy opóźnienie T dla działającego podgrafu
        T = compute_delay(G_oper, m)
        T_SUM += T
        SIM_AMOUNT += 1
        if T < T_max:
            success += 1
    return success / iterations

# Funkcja rysująca graf
def plot_graph(G):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 8))
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
    nx.draw_networkx_labels(G, pos)
    edge_labels = {(u, v): f"a: {G[u][v]['flow']}\nc: {G[u][v]['capacity']}" for u, v in G.edges}
    nx.draw_networkx_edges(G, pos, width=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title("Topologia sieci")
    plt.text(0.5, 0, f"Węzły i krawędzie z atrybutami przepływu i przepustowości. \n'a' - przepustowość w pakietach\n'c' - przepływ w bitach\nŚrednia wielkość pakietu: {m}", 
             horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.axis("off")
    plt.show()

def main():
    random.seed(42)
    
    # Tworzymy graf
    G = create_graph()
    print(f"Liczba wierzchołków: {G.number_of_nodes()}")
    print(f"Liczba krawędzi: {G.number_of_edges()}")
    
    # Obliczamy opóźnienie dla pełnej (bez uszkodzeń) sieci
    T_full = compute_delay(G, m)
    G_intensity = sum(data['flow'] for u, v, data in G.edges(data=True))
    print(f"Zagregowana intensywność przepływów G: {G_intensity}")
    print(f"Opóźnienie T dla pełnej sieci: {T_full:.4f}")
    
    # Symulacja niezawodności
    iterations = 10000
    reliability = simulate_reliability(G, p, T_max, m, iterations)
    print(f"Symulacje zakończone. Liczba udanych symulacji: {SIM_AMOUNT}.")
    print(f"    Oszacowana niezawodność sieci (prawdopodobieństwo, że T < T_max i sieć jest spójna): {reliability:.4f}")
    print(f"    Średnie T dla sprawdzonych grafów w Monte Carlo: {(T_SUM/SIM_AMOUNT):.4f}")
    
    # Rysujemy graf
    plot_graph(G)

if __name__ == '__main__':
    main()
