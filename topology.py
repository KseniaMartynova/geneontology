import networkx as nx
import matplotlib.pyplot as plt
from goatools.obo_parser import GODag

dag = GODag("go-basic.obo") #для файлов .obo специальный читатель - GODag
G = nx.DiGraph() # создается граф со стрелками
for term in dag.keys(): #здесь в граф добавляются вершины для каждого термина
    G.add_node(term, name=dag[term].name)
    for parent in dag[term].parents:
        G.add_edge(parent.id, term)
#Функция для получения связанных с вершиной вершин
def get_neighbors(graph, term_id, depth=3):
    related_terms = set()
    if depth > 0:
        neighbors = list(graph.neighbors(term_id))
        related_terms.update(neighbors)
        for neighbor in neighbors:
            related_terms.update(get_neighbors(graph, neighbor, depth - 1))
    return related_terms

#Функция для определения уровней 
def lev(graph):
    lev = {}
    for term in nx.topological_sort(graph):
        lev[term] = 0
        for predecessor in graph.predecessors(term):
            lev[term] = max(lev[term], lev[predecessor] + 1)
    return lev


term_id = "GO:0061572" 
n= get_neighbors(G, term_id)
# Создаем подграф 
subgraph = G.subgraph(n.union({term_id}))
# Определяем уровни
lev = lev(subgraph)
#Визуализируем граф
pos = nx.spring_layout(subgraph)

#Изменяем положение вершин в зависимости от их уровней
y_shift = {node: lev[node] for node in subgraph.nodes()}
pos = {node: (x, y) for (node, (x, _)) in pos.items() for y in [y_shift[node]]}

plt.figure(figsize=(12, 8))
nx.draw(subgraph, pos, with_labels=True, arrows=True, node_size=3000, node_color='lightblue', font_size=10, font_color='black', font_weight='bold')
plt.show()
