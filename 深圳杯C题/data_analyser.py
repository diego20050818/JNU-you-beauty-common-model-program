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

dg_nodes = graph.find_nodes_by_attribute("DG", True)
print("带有分布式发电的节点:", dg_nodes)

graph.print_metrics_report()