import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from goatools.obo_parser import GODag

dag = GODag("go-basic.obo") #для файлов .obo специальный читатель - GODag
G = nx.DiGraph() # создается граф со стрелками

for go_id, term in dag.items(): #здесь в граф добавляются вершины для каждого термина
    G.add_node(go_id, 
               name=term.name, 
               namespace=term.namespace)
    
    for parent in term.parents: #добавляем связи (is a - является подклассом) это основные родительские связи!
        if parent.id in dag: # в term.parents хранится простой список родительских терминов (is a)
            G.add_edge(go_id, parent.id, rel_type="is_a") 
    
    if hasattr(term, 'relationship'): #какие еще связи есть кроме родительских выше?
        for rel_type, termins in term.relationship.items():# в term.relationship хранятся осталные связи (словарь: тип связи + список терминов)
            for termin in termins: # rel_type - тип связи, targets - список терминов для этой связи
                if termin.id in dag:
                    G.add_edge(go_id, termin.id, rel_type=rel_type)# добавляем стрелку от термина к цели 

def get_neighbors(go_id):
    if go_id not in G: #проверка сущестовования термина в графе
        return None
    
    return {
        "id": go_id,
        "name": G.nodes[go_id]["name"],
        "parents": list(G.predecessors(go_id)), # возвращает узлы, которые ссылаются на текущий узел. входящие стрелки!!!!
        # пример потому что ничего непонятно: для апоптоза это - programmed cell death. 
        "children": list(G.successors(go_id)) #возвращает узлы, на которые ссылается текущий узел. исходящие стрелки!!!!!!!!
        # пример потому что ничего непонятно: для апоптоза это - apoptotic signaling pathway
    }


term_id = "GO:0061572"
n = get_neighbors(term_id)
if n:
    print("\nТермин:", n["name"])
    print("Родители:", [dag[p].name for p in n["parents"] if p in dag])
    print("Дети:", [dag[c].name for c in n["children"] if c in dag])
else:
    print(f"Термин {term_id} не найден в графе")

def plot_g(go_id, depth=3):
    if go_id not in G:
        return None

    nodes = {go_id} #множество всех терминов, которые войдут в подграф
    current = {go_id} #множество терминов текущего уровня
    
    for x in range(3):
        next_level = set()
        for node in current:
            for parent in G.predecessors(node):
                if parent not in nodes:
                    nodes.add(parent)
                    next_level.add(parent)
            for child in G.successors(node):
                if child not in nodes:
                    nodes.add(child)
                    next_level.add(child)
        current = next_level
    
    subgraph = G.subgraph(nodes) #nodes-стартовый термин + соседи 
    
    plt.figure(figsize=(12, 8))
    p = nx.spring_layout(subgraph) #пружинная укладка графа (рассчитываем позиции узлов) и словарь с координатами уузлов
    
    color_map = {
        "biological_process": "blue",
        "molecular_function": "green",
        "cellular_component": "yellow"
    }
    colors = [color_map.get(G.nodes[n]["namespace"], "gray") for n in subgraph.nodes] #для неизвеснтных типов серый
    
    nx.draw(subgraph, p,
            node_color=colors,
            with_labels=True,
            labels={n: f"{n}\n{G.nodes[n]['name'][:15]}" for n in subgraph.nodes},
            node_size=1500,
            font_size=8,
            arrowsize=15)
    
    plt.title(f"GO: {dag[go_id].name}")
    plt.tight_layout()
    plt.savefig("go_subgraph.png")
    plt.show()
    return subgraph

subgraph = plot_g(term_id, depth=1)

if subgraph:
    df = pd.DataFrame([
        {
            "source_id": u,
            "source_name": G.nodes[u]["name"],
            "target_id": v,
            "target_name": G.nodes[v]["name"],
            "relationship": d["rel_type"]
        }
        for u, v, d in subgraph.edges(data=True)
    ])
    
    print("\nТаблица связей:")
    print(df.head())
    df.to_csv("go_edges.csv", index=False)
