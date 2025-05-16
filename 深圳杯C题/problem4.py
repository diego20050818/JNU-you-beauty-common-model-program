from utils.tool import UndirectedGraph
from utils.RiskAnalyzer import RiskAnalyzer
from utils.data_loder import edges_info, nodes_info

import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
from collections import deque 
import json 
from loguru import logger
from tqdm.rich import tqdm

def problem4():
    """问题4：在光伏节点配置 15% 储能前后的风险比较"""
    node_id = "32"  # 注意：nodes_info 的 key 是字符串

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
    plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号
    def apply_storage(node, ratio=0.15):
        """将原光伏容量削减 ratio 的比例用于储能吸纳"""
        node["power"] *= (1 - ratio)

    capacities = np.arange(300, 901, 90)
    risks_no_storage = []
    risks_with_storage = []

    # 找到与该节点相连的第一个邻居
    neighbor = None
    for edge_dict in edges_info:
        (u, v) = list(edge_dict.keys())[0]
        if str(u) == node_id:
            neighbor = v
            break
        elif str(v) == node_id:
            neighbor = u
            break

    for cap in tqdm(capacities, desc="问题4：储能对比仿真"):
        # 不带储能
        nodes_info_sim = json.loads(json.dumps(nodes_info))
        nodes_info_sim[node_id]["power"] = cap
        analyzer = RiskAnalyzer(nodes_info_sim, edges_info)
        if neighbor is not None:
            line = (int(node_id), int(neighbor))
            risks_no_storage.append(analyzer.overload_risk(line))
        else:
            risks_no_storage.append(0)

        # 带储能
        nodes_info_sim_storage = json.loads(json.dumps(nodes_info))
        nodes_info_sim_storage[node_id]["power"] = cap
        apply_storage(nodes_info_sim_storage[node_id])
        analyzer_storage = RiskAnalyzer(nodes_info_sim_storage, edges_info)
        if neighbor is not None:
            risks_with_storage.append(analyzer_storage.overload_risk(line))
        else:
            risks_with_storage.append(0)

    plt.plot(capacities, risks_no_storage, 'r-o', label="无储能")
    plt.plot(capacities, risks_with_storage, 'b-s', label="配置储能")
    plt.xlabel("光伏最大接入容量 (kW)")
    plt.ylabel("过负荷风险")
    plt.title("问题4：储能前后过负荷风险对比")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == '__main__':
    problem4()