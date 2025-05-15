import json
import os
import pandas as pd
import numpy as np
from loguru import logger
from utils.tool import *

edges_file = '深圳杯C题\\edges_info.json' 
nodes_file = '深圳杯C题\\nodes_info.json'

#打开文件
with open(edges_file, 'r', encoding='utf-8') as f:
    edges_info = json.load(f)
#因为json文件中存储的边是字符串格式的元组，所以需要将其转换为实际的元组
edges_info = [{tuple(eval(edge)): info for edge, info in edge_dict.items()} for edge_dict in edges_info]

with open(nodes_file, 'r', encoding='utf-8') as f:
    nodes_info = json.load(f)

graph = UndirectedGraph(nodes_info, edges_info)

def rprint(info:str,result:any) -> None:
    """
    打印结果
    :param info: 信息
    :param result: 结果
    :return: None
    """
    logger.info(info)
    print(result)

rprint("带有分布式发电的节点:", graph.find_nodes_by_attribute("DG", True))
rprint("查找具有特定属性的边",graph.find_edges_by_attribute("type", "普通线"))
rprint("查找两个节点之间的路径", graph.find_path(1, 59))
rprint("获取所有节点的度数", graph.get_all_degrees())
rprint("找出两个节点之间的所有路径", graph.get_all_paths(1, 5))
rprint("获取属性的统计摘要", graph.get_attribute_summary("DG"))
rprint("计算图的平均度数", graph.get_average_degree())
rprint("查找两个节点之间的边", graph.get_edge(1, 2))
rprint("获取边属性", graph.get_edge_attribute(1, 2))
rprint("统计边特定属性的分布情况", graph.get_edge_attribute_statistics("type"))
rprint("获取节点属性", graph.get_node_attribute(1))
rprint("获取节点特定属性的分布情况", graph.get_node_attribute_statistics("DG"))
rprint("获取节点的度", graph.get_node_degree(1))
rprint("检查两个节点之间是否有边", graph.has_edge(1, 2))
rprint("检查两个节点之间是否连通，并返回路径", graph.is_connected(1, 2))

#可视化从起始节点到一个或者多个目标结点的最短路径
graph.plot_shortest_paths(1, [2,62,4])



graph.print_metrics_report()