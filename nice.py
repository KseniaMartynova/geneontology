import networkx as nx
import matplotlib.pyplot as plt
from goatools.obo_parser import GODag
import pandas as pd
import numpy as np
dag = GODag("go-basic.obo")

#для форматирования текста под размер вершины
def format(text, max_width=15, max_lines=3):
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        if len(' '.join(current_line + [word])) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:max_width-3] + '...' if len(lines[-1]) > max_width-3 else lines[-1]
    
    return '\n'.join(lines)

#граф без стрелок
undir_graph = nx.Graph()

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

def find_shortest_path(graph, term1, term2,term3):# для поиска кратчайшего пути
    try:
        return nx.shortest_path(graph, term1, term2,term3)
    except nx.NetworkXNoPath:
        return None
# Функция для поиска кратчайшего пути
def find_shortest_path(graph, term1, term2):
    try:
        return nx.shortest_path(graph, term1, term2)
    except nx.NetworkXNoPath:
        return None

TERM1 = "GO:0097435"  
TERM2 = "GO:0034314"  

path = find_shortest_path(undir_graph, TERM1, TERM2)

if path:
    print("\n" + "="*80)
    print("Кратчайший путь между терминами:")
    for i, node in enumerate(path):
        print(f"{i+1}. {undir_graph.nodes[node]['name']} ({node})")
    
    # Создаем ориентированный граф для визуализации иерархии
    dir_graph = nx.DiGraph()
    for term_id in dag:
        term = dag[term_id]
        formatted_name = format(term.name)
        dir_graph.add_node(term_id, name=term.name, label=formatted_name)
        for parent in term.parents:
            if parent.id in dag:
                dir_graph.add_edge(parent.id, term_id, rel_type='is_a')
    
    all_nodes = set(path)
    
    #соседей 
    for node in path:
        if node in dir_graph:
            all_nodes.update(dir_graph.predecessors(node))  # Родители
            all_nodes.update(dir_graph.successors(node))    # Дети
    
    subgraph = dir_graph.subgraph(all_nodes)
    
    # Функция для определения уровней 
    def assign_levels(graph):
        levels = {}
        for node in nx.topological_sort(graph):
            levels[node] = 0
            for predecessor in graph.predecessors(node):
                levels[node] = max(levels[node], levels[predecessor] + 1)
        return levels
    
    levels = assign_levels(subgraph)
    
    pos = {}
    level_spacing = 5.0
    node_spacing = 2.0
    
    # Группируем вершины по уровням
    lev = {}
    for node, level in levels.items():
        if level not in lev:
            lev[level] = []
        lev[level].append(node)
    
    #расставляем вершины по уровням
    max_nodes_in_level = max(len(nodes) for nodes in lev.values())
    
    for level, nodes in lev.items():
        y = level * level_spacing
        x_start = - (len(nodes) * node_spacing) / 2
        for i, node in enumerate(nodes):
            x = x_start + i * node_spacing
            #случайное смещение для предотвращения наложения
            x += np.random.uniform(-0.2, 0.2)
            y += np.random.uniform(-0.2, 0.2)
            pos[node] = (x, y)
    
    node_colors = []
    edge_colors = []
    edge_widths = []
    
    for node in subgraph.nodes():
        if node == TERM1:
            node_colors.append('green')  # првый термина - зеленый
        elif node == TERM2:
            node_colors.append('purple')  # второй термина - фиолетовый
        elif node in path:
            node_colors.append('red')    # вершины пути  красные
        else:
            node_colors.append('lightblue')  
    
    #список ребер пути
    path_edges = []
    for i in range(len(path) - 1):
        if subgraph.has_edge(path[i], path[i+1]):
            path_edges.append((path[i], path[i+1]))
        elif subgraph.has_edge(path[i+1], path[i]):
            path_edges.append((path[i+1], path[i]))
    

    for u, v in subgraph.edges():
        if (u, v) in path_edges or (v, u) in path_edges:
            edge_colors.append('red')  # Ребра пути красные
            edge_widths.append(3.0)    
        else:
            edge_colors.append('gray')  
            edge_widths.append(1.0)     
    
    #рисуем граф с выделенным путем
    plt.figure(figsize=(14, 10))
    
    #рисуем вершины
    nx.draw_networkx_nodes(
        subgraph, 
        pos, 
        node_size=5000,
        node_color=node_colors,
        alpha=0.9,
        edgecolors='black',
        linewidths=1.5
    )
    
    nx.draw_networkx_edges(
        subgraph,
        pos,
        edge_color=edge_colors,
        width=edge_widths,
        arrows=True,
        arrowstyle='-|>',
        arrowsize=20,
        connectionstyle='arc3,rad=0.1'  # ребра огибающие
    )
    
    #рисуем подписи
    labels = {node: subgraph.nodes[node]['label'] for node in subgraph.nodes()}
    text_items = {}
    for node, (x, y) in pos.items():
        label = labels[node]
        t = plt.text(
            x, y, label,
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=9,
            fontweight='bold',
            wrap=True
        )
        text_items[node] = t
    
    #текст не выходит за границы узлов??
    for node, t in text_items.items():
        bbox = t.get_window_extent(renderer=plt.gcf().canvas.get_renderer())
        bbox = bbox.transformed(plt.gca().transData.inverted())
        
        # Получаем координаты вершины
        x, y = pos[node]
        node_radius = 0.08  
        
        #выходит ли текст за границы вершины???
        if (bbox.x0 < x - node_radius or bbox.x1 > x + node_radius or
            bbox.y0 < y - node_radius or bbox.y1 > y + node_radius):
            #уменьшаем шрифт в случае проблемы
            t.set_fontsize(8)
    
    plt.axis('off')
    plt.tight_layout()
    
    plt.show()
    
    ed = []
    for u, v, data in subgraph.edges(data=True):
        ed.append({
            "source_id": u,
            "source_name": subgraph.nodes[u]['name'],
            "target_id": v,
            "target_name": subgraph.nodes[v]['name'],
            "relationship": data.get("rel_type", "unknown")
        })
    df = pd.DataFrame(ed)
    print("\nТаблица связей:")
    print(df.head())
