import networkx as nx
import matplotlib.pyplot as plt
from goatools.obo_parser import GODag
import pandas as pd
dag = GODag("go-basic.obo")
G = nx.DiGraph()

for term in dag.keys():  # term - это GO ID типа "GO:0000001"
    #Добавляем термин в граф
    G.add_node(term, name=dag[term].name)  # сохраняем название термина
    
    # Добавляем связи с родительями
    for parent in dag[term].parents:  # у каждого термина есть родители
        G.add_edge(parent.id, term, rel_type='is_a')  # стрелка от родителя к термину
        # 'is_a' - это тип связи "является подклассом"
# Функция для получения соседей
def get_related_nodes(graph, node_id, depth=3):
    related_nodes = set()  # здесь будем хранить всех соседей
    if depth > 0:  # если еще не достигли максимальной глубины
        neighbors = list(graph.neighbors(node_id))  # находим непосредственных соседей
        related_nodes.update(neighbors)  # добавляем их в результат
        for neighbor in neighbors:  # для каждого соседа рекурсивно ищем его соседей
            related_nodes.update(get_related_nodes(graph, neighbor, depth - 1))
    return related_nodes

# Функция для определения уровней терминов
def lev(graph):
    levels = {}  # словарь из терминов и их уровеней
    #укладываем термины сверху вниз
    for node in nx.topological_sort(graph):
        levels[node] = 0  # начальный уровень
        # Уровень узла = максимальный уровень родителей + 1
        for predecessor in graph.predecessors(node):
            levels[node] = max(levels[node], levels[predecessor] + 1)
    return levels

# Функция для поиска всех предков термина 
def get_all_ancestors(graph, node_id):
    ancestors = set()  # множество для хранения предков
    queue = [node_id]  # очередь для обхода в ширину
    
    while queue:
        current = queue.pop(0)  # берем первый элемент из очереди
        ancestors.add(current)  # добавляем его в предки
        # Добавляем всех родителей текущего узла в очередь
        for predecessor in graph.predecessors(current):
            if predecessor not in ancestors:
                queue.append(predecessor)
    
    return ancestors

# Основная функция для поиска общего предка 
def find_parent(graph, terms):
    if not terms:  # если список терминов пустой
        return None
    
    ancestors_list = []#здесь предки для каждого термина
    for term in terms:
        if term in graph:
            ancestors_list.append(get_all_ancestors(graph, term))
        else:
            print(f"ермин {term} не найден")
            return None
    
    # Находим общих предков 
    common_ancestors = set.intersection(*ancestors_list)
    
    if not common_ancestors:  # если общих предков нет
        return None
    
    # Определяем уровни всех терминов в графе
    global_levels = lev(graph)
    
    # Ищем предка самого нижнего
    c_p = None
    max_level = -1
    for ancestor in common_ancestors:
        if ancestor in global_levels and global_levels[ancestor] > max_level:
            max_level = global_levels[ancestor]
            c_p = ancestor
    
    return c_p  # возвращаем наименьшего общего предка

# Термины для которых ищем общего предка
GROUP_TERMS = ["GO:0098754", "GO:0071230", "GO:1901700", 
   # "GO:0007015", 
   # "GO:0045010", 
   # "GO:0030036",  
   # "GO:0030041",  
   # "GO:0031034",
]

# Ищем общего предка для группы
c_p = find_parent(G, GROUP_TERMS)

# Объявляем subgraph_c_p глобально, чтобы использовать позже
subgraph_c_p = None

if c_p:  # если предок найден
    print("\n" + "="*80)
    print(f"Наименьший общий предок для группы:")
    # Выводим информацию по каждому термину
    for term in GROUP_TERMS:
        print(f"- {term}: {G.nodes[term]['name']}")
    print(f"\nLCA: {c_p} - {G.nodes[c_p]['name']}")  # сам общий предок
    
    #  для визуализации
    all_nodes = set(GROUP_TERMS + [c_p])  # начальные термины + НОБ
    
    # Добавляем все узлы на путях от НОБ к терминам
    for term in GROUP_TERMS:
        try:
            path = nx.shortest_path(G, c_p, term)  # кратчайший путь
            all_nodes.update(path)  # добавляем все узлы пути
        except nx.NetworkXNoPath:  # если пути нет
            continue
    
    # Создаем подграф только с нужными узлами
    subgraph_c_p = G.subgraph(all_nodes)
    
    # Определяем уровни узлов в подграфе
    levels_c_p = lev(subgraph_c_p)
    
    # Генерируем позиции узлов для визуализации
    pos_c_p = nx.spring_layout(subgraph_c_p)
    
    # позиции по уровням чтобы выше bkb ниже
    y_shift_parent = {node: levels_c_p[node] for node in subgraph_c_p.nodes()}
    pos_parent = {node: (x, y) for (node, (x, _)) in pos_c_p.items() for y in [y_shift_parent[node]]}
    
    node_colors = []  # цвета узлов
    edge_colors = []  # цвета связей
    edge_widths = []  # толщина связей
    
    for node in subgraph_c_p.nodes():
        if node in GROUP_TERMS:  # исходные термины - зеленые
            node_colors.append('green')
        elif node == c_p:  # общий предок - красный
            node_colors.append('red')
        else:  # остальные - голубые
            node_colors.append('lightblue')
    
    # Находим все ребра на путях от НОБ к терминам
    path_edges = []
    for term in GROUP_TERMS:
        try:
            path_to_term = nx.shortest_path(G, c_p, term)
            # Добавляем все ребра пути
            for i in range(len(path_to_term) - 1):
                path_edges.append((path_to_term[i], path_to_term[i+1]))
        except nx.NetworkXNoPath:
            continue
    
    for u, v in subgraph_c_p.edges():
        if (u, v) in path_edges:  # ребра пути - красные и толстые
            edge_colors.append('red')
            edge_widths.append(3.0)
        else:  # остальные - серые и тонкие
            edge_colors.append('gray')
            edge_widths.append(1.0)
    
    plt.figure(figsize=(14, 10))
    nx.draw(
        subgraph_c_p, 
        pos_c_p, 
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
    plt.title(f"Наименьший общий предок для группы терминов\nLCA: {c_p} - {G.nodes[c_p]['name']}", fontsize=14)
    plt.show()
    
else:
    print("\nДля указанной группы терминов общий предок не найден")

# Вывод списка смежности
print("\n" + "="*80)
print("Таблица связей:")
print("Родитель -> Потомок | Тип связи")

if subgraph_c_p is not None:  # проверяем, что подграф существует
    edges_table = []
    for u, v, data in subgraph_c_p.edges(data=True):
        edge_info = f"{u} -> {v} | {data.get('rel_type', 'is_a')}"
        edges_table.append(edge_info)

    #Сортируем
    edges_table_sorted = sorted(edges_table)

    #построчно!!!!!!!!!!
    for edge in edges_table_sorted:
        print(edge)
else:
    print("Невозможно вывести таблицу связей: общий предок не найден")
