import pandas 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from utils.tool import UndirectedGraph

#负荷参数
data = pandas.read_excel(r'E:\学习\数模相关\code_of_argorithm\深圳杯C题\C题附件：有源配电网62节点系统基本参数.xlsx',
                         sheet_name="表1 有源配电网62节点系统负荷参数")

#拓扑参数
info = pandas.read_excel(r'E:\学习\数模相关\code_of_argorithm\深圳杯C题\C题附件：有源配电网62节点系统基本参数.xlsx',
                         sheet_name="表2 有源配电网62节点系统拓扑参数")


#+++++++数据预处理+++++++++++
from itertools import islice

nodes_info = []
#print("=" * 20+"node info"+"=" * 20)
for _,content in data.iterrows():
    #print(f"NO.{id}:\tP:{p}kW")
    id,p = tuple(content)
    id:int = int(id)
    p:float = float(p)
    node_info = {
        "id": id,
        "p": p
    }
    nodes_info.append(node_info)

    #print(f"NO.{id}\tP:{p}kW")

edges_info = []    
#print("=" * 20+"edge info"+"=" * 20)
for _,content in info.iterrows():
    #from_node起点，to_node终点,length长度,resistor电阻，reactance电抗
    id,from_node,to_node,length,Resistor,Reactance = tuple(content)
    id:int = int(id)
    from_node:int = int(from_node)
    to_node:int = int(to_node)
    edge_info = {
        "id": id,
        "from_node": from_node,
        "to_node": to_node,
        "length": length,
        "Resistor": Resistor,
        "Reactance": Reactance
    }
    edges_info.append(edge_info)
    #print(f"NO.{id}:\tfrom_node:{from_node}\tto_node:{to_node}\tlength:{length}km\tResistor:{Resistor}Ω/km\tReactance:{Reactance}Ω/km")

    graph_edges = []

# 辅助：定义每个节点的属性（负荷类型、是否接DG）
node_info_from_img = {
    1: {"type": "居民", "DG": False},
    2: {"type": "居民", "DG": False},
    3: {"type": "居民", "DG": False},
    4: {"type": "居民", "DG": False},
    5: {"type": "居民", "DG": False},
    6: {"type": "居民", "DG": False},
    7: {"type": "办公和建筑", "DG": False},
    8: {"type": "居民", "DG": False},
    9: {"type": "政府和机构", "DG": False},
    10: {"type": "居民", "DG": False},
    11: {"type": "商业", "DG": False},
    12: {"type": "办公和建筑", "DG": False},
    13: {"type": "居民", "DG": False},
    14: {"type": "办公和建筑", "DG": False},
    15: {"type": "居民", "DG": False},
    16: {"type": "商业", "DG": True},
    17: {"type": "居民", "DG": False},
    18: {"type": "办公和建筑", "DG": False},
    19: {"type": "居民", "DG": False},
    20: {"type": "居民", "DG": False},
    21: {"type": "政府和机构", "DG": False},
    22: {"type": "居民", "DG": True},
    23: {"type": "居民", "DG": False},
    24: {"type": "居民", "DG": False},
    25: {"type": "居民", "DG": False},
    26: {"type": "居民", "DG": False},
    27: {"type": "商业", "DG": False},
    28: {"type": "居民", "DG": False},
    29: {"type": "政府和机构", "DG": False},
    30: {"type": "居民", "DG": False},
    31: {"type": "商业", "DG": False},
    32: {"type": "办公和建筑", "DG": True},
    33: {"type": "商业", "DG": False},
    34: {"type": "商业", "DG": False},
    35: {"type": "居民", "DG": True},
    36: {"type": "政府和机构", "DG": False},
    37: {"type": "居民", "DG": False},
    38: {"type": "商业", "DG": False},
    39: {"type": "居民", "DG": True},
    40: {"type": "办公和建筑", "DG": False},
    41: {"type": "居民", "DG": False},
    42: {"type": "商业", "DG": True},
    43: {"type": "居民", "DG": False},
    44: {"type": "居民", "DG": False},
    45: {"type": "政府和机构", "DG": False},
    46: {"type": "居民", "DG": False},
    47: {"type": "办公和建筑", "DG": False},
    48: {"type": "居民", "DG": True},
    49: {"type": "商业", "DG": False},
    50: {"type": "居民", "DG": False},
    51: {"type": "居民", "DG": False},
    52: {"type": "居民", "DG": True},
    53: {"type": "商业", "DG": False},
    54: {"type": "居民", "DG": False},
    55: {"type": "居民", "DG": True},
    56: {"type": "商业", "DG": False},
    57: {"type": "居民", "DG": False},
    58: {"type": "政府和机构", "DG": False},
    59: {"type": "居民", "DG": False},
    60: {"type": "居民", "DG": False},
    61: {"type": "政府和机构", "DG": False},
    62: {"type": "居民", "DG": False},
}

for info in nodes_info:
    node_info_from_img[info["id"]]["power"] = info["p"]  # 添加功率属性



# 创建一个辅助函数，用于添加边
def add_edge(from_node, to_node, edge_info):
    # 因为是无向图，我们只存储一个方向的边
    # 为了确保边的唯一性，我们总是将较小的节点编号放在前面
    if from_node > to_node:
        from_node, to_node = to_node, from_node
    
    # 检查边是否已存在
    for edge_dict in graph_edges:
        if (from_node, to_node) in edge_dict:
            # 如果边已存在，更新边信息
            edge_dict[(from_node, to_node)].update(edge_info)
            return
    
    # 如果边不存在，添加新的边，确保包含所有必要的字段
    default_edge_info = {
        "length": 0,  # 默认值，应该被实际值覆盖
        "type": "普通线", 
        "分段开关": "None", 
        "联络开关": "None", 
        "Resistor": 0,  # 默认值，应该被实际值覆盖
        "Reactance": 0   # 默认值，应该被实际值覆盖
    }
    
    # 用提供的edge_info更新默认值
    default_edge_info.update(edge_info)
    
    # 添加完整的边信息
    graph_edges.append({(from_node, to_node): default_edge_info})

# 添加边（假设edges_info已存在）
# 以下是示例代码，实际使用时需要替换为实际的edges_info


# 添加所有边
for edge in edges_info:
    from_node = edge["from_node"]
    to_node = edge["to_node"]
    length = edge["length"]
    Resistor = edge["Resistor"]
    Reactance = edge["Reactance"]
    
    # 添加边到图
    edge_info = {
        "length": length, 
        "type": "普通线", 
        "分段开关": "None", 
        "联络开关": "None", 
        "Resistor": Resistor, 
        "Reactance": Reactance
    }
    add_edge(from_node, to_node, edge_info)

# 更新联络线
tie_edges = [
    (29, 19),
    (43, 13),
    (23, 62)
]

for from_node, to_node in tie_edges:
    # 更新边类型为联络线，但保留其他属性不变
    add_edge(from_node, to_node, {"type": "馈线间联络线"})

# 更新分段开关
switch_edges = [
    [(3,4),"S1"],
    [(5,6),"S2"],
    [(7,8),"S3"],
    [(9,10),"S4"],
    [(11,12),"S5"],
    [(5,14),"S6"],
    [(15,16),"S7"],
    [(1,17),"S8"],
    [(3,20),"S9"],
    [(20,21),"S10"],
    [(24,25),"S11"],
    [(26,27),"S12"],
    [(25,30),"S13"],
    [(30,31),"S14"],
    [(26,33),"S15"],
    [(33,34),"S16"],
    [(24,36),"S17"],
    [(37,38),"S18"],
    [(24,40),"S19"],
    [(40,41),"S20"],
    [(45,46),"S21"],
    [(47,48),"S22"],
    [(44,49),"S23"],
    [(50,51),"S24"],
    [(45,53),"S25"],
    [(53,54),"S26"],
    [(43,56),"S27"],
    [(57,58),"S28"],
    [(60,61),"S29"],
]

for (from_node, to_node), switch in switch_edges:
    # 更新分段开关，但保留其他属性不变
    add_edge(from_node, to_node, {"分段开关": switch})

# 更新联络开关
tie_switch_edges = [
    [(29, 19), "S29-2"],
    [(43, 13), "S13-1"],
    [(23, 62), "S62-3"]
]

for (from_node, to_node), switch in tie_switch_edges:
    # 更新联络开关，但保留其他属性不变
    add_edge(from_node, to_node, {"联络开关": switch})


# 打印最终结果
""" print("=" * 20 + "graph edges" + "=" * 20)
for edge_dict in graph_edges:
    for edge, info in edge_dict.items():
        print(f"Edge {edge}: {info}") """
import json
#存储为文件
with open("深圳杯C题/edges_info.json", "w",encoding='utf-8') as f:
    # 转换节点ID为字符串以避免JSON序列化问题
    serializable_graph_edges = [{str(edge): info for edge, info in edge_dict.items()} for edge_dict in graph_edges]
    json.dump(serializable_graph_edges, f, indent=4,ensure_ascii=False)

with open("深圳杯C题/nodes_info.json", "w",encoding='utf-8') as f:
    json.dump(node_info_from_img, f, indent=4,ensure_ascii=False)

def main():
    # 创建无向图实例
    graph = UndirectedGraph(node_info_from_img, graph_edges)
    
    # 查询节点属性
    print("节点1的类型:", graph.get_node_attribute(1, "type"))
    
    # 查询边属性
    print("节点1和节点2之间的距离:", graph.get_edge_attribute(1, 2, "length"))
    
    # 检查两个节点之间是否有边
    print("节点1和节点2之间是否有边:", graph.has_edge(1, 2))
    
    # 查找两个节点是否连通并打印路径
    graph.is_connected(1, 59)
    
    # 打印节点的邻居
    graph.print_node_neighbors(1)
    
    # 查找具有特定属性的节点
    dg_nodes = graph.find_nodes_by_attribute("DG", True)
    print("带有分布式发电的节点:", dg_nodes)
    
    # 查找具有特定属性的边
    tie_edges = graph.find_edges_by_attribute("type", "普通线")
    print("普通线:", tie_edges)
    #graph.visualize(node_attribute='weight', edge_attribute='distance', title='示例图')
    #graph.visualize_graph_metrics()
    # 打印整个图
    #graph.print_graph()

if __name__ == "__main__":
    main()