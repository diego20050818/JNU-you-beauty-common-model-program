from utils.RiskAnalyzer import RiskAnalyzer
from utils.data_loder import edges_info, nodes_info

import numpy as np  
import matplotlib.pyplot as plt  
from collections import deque 
import json 
from tqdm.rich import tqdm

def problem2():
    """问题2：分析 DG 容量从 300 至 900kW 的风险演变曲线"""
    capacities = np.arange(300, 901, 90)
    risks = []

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
    plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

    # 找到所有DG节点的key（字符串类型）
    dg_node_keys = [k for k, v in nodes_info.items() if v.get("DG")]

    for cap in tqdm(capacities, desc="问题2：容量模拟中"):
        # 深拷贝nodes_info，避免影响原始数据
        nodes_info_sim = json.loads(json.dumps(nodes_info))
        # 修改DG节点容量
        for k in dg_node_keys:
            nodes_info_sim[k]["power"] = cap

        analyzer = RiskAnalyzer(nodes_info_sim, edges_info)
        total_risk = 0
        # 遍历所有边
        for edge_dict in edges_info:
            (u, v) = list(edge_dict.keys())[0]
            # 只统计与DG节点相关的边
            if u in dg_node_keys or v in dg_node_keys:
                line = (u, v)
                total_risk += analyzer.load_loss_risk(line) + analyzer.overload_risk(line)
        risks.append(total_risk)

    # 输出数据说明
    print("DG容量(kW) 与 系统总风险 数据如下：")
    for cap, risk in zip(capacities, risks):
        print(f"容量: {cap} kW, 系统总风险: {risk}")

    # 绘图
    plt.plot(capacities, risks, 'r-o')
    plt.xlabel("DG 单机容量 (kW)")
    plt.ylabel("系统总风险")
    plt.title("问题2：DG 容量 vs 系统风险")
    plt.grid()
    plt.show()


if __name__ == '__main__':
    problem2()