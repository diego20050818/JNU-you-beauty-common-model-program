from utils.RiskAnalyzer import RiskAnalyzer
from utils.data_loder import edges_info, nodes_info

import numpy as np  
import matplotlib.pyplot as plt  
import json 
from tqdm.rich import tqdm

def problem3():
    """问题3：光伏典型出力下，不同最大接入容量对系统风险影响"""

    # 典型光伏出力曲线展示
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
    plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号
    t = np.linspace(6, 18, 100)
    P_pv = 300 * np.sin(np.pi * (t - 6) / 12) ** 2

    plt.plot(t, P_pv)
    plt.title("典型光伏出力曲线")
    plt.xlabel("时间 (h)")
    plt.ylabel("出力功率 (kW)")
    plt.grid()
    plt.show()

    node_id = "32"  # 注意：nodes_info 的 key 是字符串
    capacities = np.linspace(300, 900, 7)
    risks = []

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

    for cap in tqdm(capacities, desc="问题3：PV容量仿真"):
        # 深拷贝nodes_info，避免影响原始数据
        nodes_info_sim = json.loads(json.dumps(nodes_info))
        nodes_info_sim[node_id]["power"] = cap

        analyzer = RiskAnalyzer(nodes_info_sim, edges_info)
        if neighbor is not None:
            line = (int(node_id), int(neighbor))
            risks.append(analyzer.overload_risk(line))
        else:
            risks.append(0)

    plt.plot(capacities, risks, 'b-s')
    plt.xlabel("光伏最大接入容量 (kW)")
    plt.ylabel("过负荷风险")
    plt.title("问题3：PV容量 vs 风险")
    plt.grid()
    plt.show()

if __name__ == '__main__':
    problem3()