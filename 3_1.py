import networkx as nx
import matplotlib.pyplot as plt
from goatools.obo_parser import GODag
dag = GODag("go-basic.obo")
G = nx.DiGraph() # ориентированный граф

for term in dag.keys():
    G.add_node(term, name=dag[term].name) #Для каждого термина добавляется узел в граф с атрибутом name
    for parent in dag[term].parents:
        G.add_edge(parent.id, term, rel_type='is_a')#Для каждого отношения is_a  добавляется ребро в граф

# Функция для вычисления глубины вершины, без нее мы не знаем что делать, потому что не знаем на какой глубине находится термин и какую вершину нужно поднимать
def depth(graph, node_id):
    if node_id not in graph:
        return -1
    
    # Используем BFS для нахождения максимальной глубины от корней
    visited = set()
    queue = [(node_id, 0)]
    max_depth = 0
    
    while queue:
        current, current_depth = queue.pop(0)
        if current not in visited:
            visited.add(current)
            max_depth = max(max_depth, current_depth)
            
            # Идем к родителям
            for predecessor in graph.predecessors(current):
                queue.append((predecessor, current_depth + 1))
    
    return max_depth

# Функция для получения непосредственного родителя
def parent(graph, node_id):
    if node_id not in graph:
        return None
    # Спрашиваем У этого узла есть родители?
    predecessors = list(graph.predecessors(node_id))
    # Если есть возвращаем первого родителя
    # Если нет, значит это корень - возвращаем None
    return predecessors[0] if predecessors else None

def LCA(u, v):
    # Проверяем, что вершины существуют в графе
    if u not in G or v not in G:
        print(f"Одна из вершин не найдена в графе: {u}, {v}")
        return None
    
    #Получаем глубины вершин
    h1 = depth(G, u)
    h2 = depth(G, v)
    
    print(f"Глубина {u}: {h1}")
    print(f"Глубина {v}: {h2}")
    
    current_u, current_v = u, v
    
    #Выравниваем глубины
    while h1 != h2:
        if h1 > h2:
            current_u = parent(G, current_u)
            if current_u is None:
                break
            h1 -= 1
            print(f"Поднимаем u до {current_u}, новая глубина: {h1}")
        else:
            current_v = parent(G, current_v)
            if current_v is None:
                break
            h2 -= 1
            print(f"Поднимаем v до {current_v}, новая глубина: {h2}")
    
    # Если после выравнивания одна из вершин стала None - возвращаем корень
    if current_u is None or current_v is None:
        return None
    
    print(f"После выравнивания: u={current_u}, v={current_v}")
    
    # Синхронно поднимаемся вверх
    while current_u != current_v:
        current_u = parent(G, current_u)
        current_v = parent(G, current_v)
        
        if current_u is None or current_v is None:
            break
            
        print(f"Синхронный подъем: u={current_u}, v={current_v}")
    
    return current_u

TERM1 = "GO:0048523"  
TERM2 = "GO:1903053"  

lca_result = LCA(TERM1, TERM2)

print("\n" + "=" * 60)
if lca_result:
    print(f"РЕЗУЛЬТАТ:")
    print(f"LCA({TERM1}, {TERM2}) = {lca_result}")
    print(f"Название: {G.nodes[lca_result]['name']}")
else:
    print("Общий предок не найден")

# Визуализация пути
if lca_result:
    print("\n" + "=" * 60)
    print("ВИЗУАЛИЗАЦИЯ ПУТЕЙ:")
    all_nodes = set([TERM1, TERM2, lca_result])
    
    # Добавляем пути от LCA к каждому термину
    try:
        path1 = nx.shortest_path(G, lca_result, TERM1)
        all_nodes.update(path1)
        print(f"Путь от LCA к {TERM1}: {' -> '.join(path1)}")
    except nx.NetworkXNoPath:
        print(f"Нет пути от LCA к {TERM1}")
    
    try:
        path2 = nx.shortest_path(G, lca_result, TERM2)
        all_nodes.update(path2)
        print(f"Путь от LCA к {TERM2}: {' -> '.join(path2)}")
    except nx.NetworkXNoPath:
        print(f"Нет пути от LCA к {TERM2}")
    
    # Создаем подграф 
    subgraph = G.subgraph(all_nodes)
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(subgraph, seed=42)
    
    # Цвета вершин
    node_colors = []
    for node in subgraph.nodes():
        if node == TERM1:
            node_colors.append('green')
        elif node == TERM2:
            node_colors.append('green')
        elif node == lca_result:
            node_colors.append('red')
        else:
            node_colors.append('lightblue')
    
    # Размеры вершин
    node_sizes = []
    for node in subgraph.nodes():
        if node == TERM1 or node == TERM2:
            node_sizes.append(2000)
        elif node == lca_result:
            node_sizes.append(2000)
        else:
            node_sizes.append(2000)
    
    nx.draw(subgraph, pos, with_labels=True, arrows=True,
            node_size=node_sizes, node_color=node_colors,
            font_size=8, font_weight='bold',
            edge_color='gray', width=1.5)
    
    plt.title(f"LCA: {lca_result} - {G.nodes[lca_result]['name']}", fontsize=14)
    plt.show()
    
    print("\n" + "=" * 60)
    print("ТАБЛИЦА СВЯЗЕЙ:")
    print("Родитель -> Потомок | Тип связи")
    
    for u, v, data in subgraph.edges(data=True):
        print(f"{u} -> {v} | {data.get('rel_type', 'is_a')}")
