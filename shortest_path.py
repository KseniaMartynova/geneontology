import networkx as nx
import matplotlib.pyplot as plt
from goatools.obo_parser import GODag
import pandas as pd
import networkx as nx

dag = GODag("go-basic.obo")
undir_graph = nx.Graph() #граф без стрелок 

#вершины и рёбра в обоих направлениях
for term_id in dag:
    term = dag[term_id]
    undir_graph.add_node(term_id, name=term.name)
    
    for parent in term.parents:
        if parent.id in dag:
            undir_graph.add_edge(term_id, parent.id, rel_type='is_a')
    
    if hasattr(term, 'relationship'):
        for rel_type, targets in term.relationship.items():
            for target in targets:
                if target.id in dag:
                    undir_graph.add_edge(term_id, target.id, rel_type=rel_type)

def find_shortest_path(graph, term1, term2): #Функция для поиска кратчайшего пути
    try:
        return nx.shortest_path(graph, term1, term2)
    except nx.NetworkXNoPath:
        return None

TERM1 = "GO:0097435"  
TERM2 = "GO:0034314"  
path = find_shortest_path(undir_graph, TERM1, TERM2)#ищем кратчайший путь между терминами

if path:
    print("\n" + "="*80)
    print("Кратчайший путь:")
    for i, node in enumerate(path):
        print(f"{i+1}. {node} - {undir_graph.nodes[node]['name']}")
    
    # граф со стрелками делаем
    dir_graph = nx.DiGraph()
    for term_id in dag:
        term = dag[term_id]
        dir_graph.add_node(term_id, name=term.name)
        for parent in term.parents:
            if parent.id in dag:
                dir_graph.add_edge(parent.id, term_id, rel_type='is_a')
    
    #собираем все вершины
    all_nodes = set(path)
    for node in path:
        if node in dir_graph:
            all_nodes.update(dir_graph.predecessors(node))  #родители
            all_nodes.update(dir_graph.successors(node))    #дети
    subgraph = dir_graph.subgraph(all_nodes)
    
    #уровни вершины
    def assign_levels(graph):
        levels = {}
        for node in nx.topological_sort(graph):
            levels[node] = 0
            for predecessor in graph.predecessors(node):
                levels[node] = max(levels[node], levels[predecessor] + 1)
        return levels
    levels = assign_levels(subgraph)
    pos = nx.spring_layout(subgraph)
    
    #положение вершины в зависимости от их уровней
    y_shift = {node: levels[node] for node in subgraph.nodes()}
    pos = {node: (x, y) for (node, (x, _)) in pos.items() for y in [y_shift[node]]}
    
    node_colors = []
    edge_colors = []
    edge_widths = []
    for node in subgraph.nodes():
        if node == TERM1:
            node_colors.append('green')  # первый термина - зеленый
        elif node == TERM2:
            node_colors.append('purple')  # второй термина - фиолетовый
        elif node in path:
            node_colors.append('red')    # вершины на пути - красные
        else:
            node_colors.append('lightblue')  # Остальные узлы - голубые
    
    path_edges = []
    for i in range(len(path) - 1):
        if subgraph.has_edge(path[i], path[i+1]):
            path_edges.append((path[i], path[i+1]))
        elif subgraph.has_edge(path[i+1], path[i]):
            path_edges.append((path[i+1], path[i]))
    
    for u, v in subgraph.edges():
        if (u, v) in path_edges or (v, u) in path_edges:
            edge_colors.append('red')  
            edge_widths.append(3.0)    
        else:
            edge_colors.append('gray')  
            edge_widths.append(1.0)    
    
    
    plt.figure(figsize=(14, 10))
    nx.draw(
        subgraph, 
        pos, 
        with_labels=True, 
        arrows=True, 
        node_size=3000, 
        node_color=node_colors, 
        edge_color=edge_colors,
        width=edge_widths,
        font_size=10, 
        font_color='black', 
        font_weight='bold'
    )
    plt.title(f"Путь между {TERM1} и {TERM2}\n"
              f"{undir_graph.nodes[TERM1]['name']} → {undir_graph.nodes[TERM2]['name']}\n"
              f"Путь выделен красным", fontsize=14)
    plt.show()
    
    edges_data = []
    for u, v, data in subgraph.edges(data=True):
        edges_data.append({
            "source_id": u,
            "source_name": subgraph.nodes[u]["name"],
            "target_id": v,
            "target_name": subgraph.nodes[v]["name"],
            "relationship": data.get("rel_type", "unknown")
        })
    
 
    df = pd.DataFrame(edges_data)
    print("\nТаблица связей:")
    print(df.head())
