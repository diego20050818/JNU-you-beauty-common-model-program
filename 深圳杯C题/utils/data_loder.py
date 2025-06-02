
'''
# 将数据加载到内存中
数据格式为json
'''
import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
from collections import deque 
import json 
from loguru import logger

edges_file = '深圳杯C题\\data_file\\edges_info.json'
nodes_file = '深圳杯C题\\data_file\\nodes_info.json'

try:
    logger.info(f"Opening edges file: {edges_file}")
    with open(edges_file, 'r', encoding='utf-8') as f:
        edges_info = json.load(f)
    # 因为json文件中存储的边是字符串格式的元组，所以需要将其转换为实际的元组
    edges_info = [{tuple(eval(edge)): info for edge, info in edge_dict.items()} for edge_dict in edges_info]
    logger.info("Edges info loaded and processed successfully.")
except Exception as e:
    logger.error(f"Failed to load or process edges info: {e}")

try:
    logger.info(f"Opening nodes file: {nodes_file}")
    with open(nodes_file, 'r', encoding='utf-8') as f:
        nodes_info = json.load(f)
    logger.info("Nodes info loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load nodes info: {e}")

if __name__ == '__main__':
    print("="*20+" edges info "+"="*20)
    print(edges_info)
    print("="*20+" nodes info "+"="*20)
    print(nodes_info)