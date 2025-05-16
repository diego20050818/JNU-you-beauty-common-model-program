import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
from collections import deque 
import json 

# ---------------------- 数据加载与预处理 ----------------------  
# def load_data():  
#     # 加载负荷参数  
#     data = pd.read_excel(file, sheet_name="表1 有源配电网62节点系统负荷参数")  
#     nodes = []  
#     for _, row in data.iterrows():  
#         node = {  
#             "id": row["No."],  
#             "power": row["有功P/kW"],  
#             "type": "居民",  # 默认类型，后续根据DG位置更新  
#             "DG": False  
#         }  
#         nodes.append(node)  

#     # 加载拓扑参数  
#     info = pd.read_excel(file, sheet_name="表2 有源配电网62节点系统拓扑参数")  
#     edges = []  
#     for _, row in info.iterrows():  
#         edge = {  
#             "from": row["起点"],  
#             "to": row["终点"],  
#             "length": row["长度/km"],  
#             "resistor": row["电阻/Ω"],  
#             "reactance": row["电抗/Ω"],  
#             "capacity": 0  # 后续计算  
#         }  
#         edges.append(edge)  

#     # 标记DG节点（题目指定8个）  
#     dg_nodes = [16, 22, 32, 35, 39, 42, 48, 52]  
#     for node in nodes:  
#         if node["id"] in dg_nodes:  
#             node["DG"] = True  
#             node["type"] = "商业"  # 假设DG接入商业区  
#     return nodes, edges  

file = 'E:\\学习\\数模相关\\code_of_argorithm\\深圳杯C题\\C题附件：有源配电网62节点系统基本参数.xlsx'
def load_data(limit=15):
    data = pd.read_excel(file, sheet_name="表1 有源配电网62节点系统负荷参数").head(limit)
    nodes = []
    for _, row in data.iterrows():
        node = {
            "id": row["No."],
            "power": row["有功P/kW"],
            "type": "居民",
            "DG": False
        }
        nodes.append(node)

    info = pd.read_excel(file, sheet_name="表2 有源配电网62节点系统拓扑参数")
    selected_ids = {node["id"] for node in nodes}
    edges = []
    for _, row in info.iterrows():
        if row["起点"] in selected_ids and row["终点"] in selected_ids:
            edge = {
                "from": row["起点"],
                "to": row["终点"],
                "length": row["长度/km"],
                "resistor": row["电阻/Ω"],
                "reactance": row["电抗/Ω"],
                "capacity": 0,
                "original_capacity": 0
            }
            edges.append(edge)

    dg_nodes = [16, 22, 32, 35, 39, 42, 48, 52]
    for node in nodes:
        if node["id"] in dg_nodes:
            node["DG"] = True
            node["type"] = "商业"
    return nodes, edges

# ---------------------- 图结构与网络流模型 ----------------------  
class PowerGridGraph:  
    def __init__(self, nodes, edges):  
        self.nodes = {node["id"]: node for node in nodes}  
        self.edges = {}  
        self.adjacency = {}  

        # 初始化边容量（基于阻抗）  
        for edge in edges:  
            u, v = edge["from"], edge["to"]  
            R = edge["resistor"]  
            X = edge["reactance"]  
            V = 10e3  # 10kV  
            Z = np.sqrt(R**2 + X**2)  
            edge["capacity"] = (V**2 / Z) * 0.9  # 功率因数0.9  
            self.adjacency.setdefault(u, []).append(v)  
            self.adjacency.setdefault(v, []).append(u)  
            self.edges[(u, v)] = edge  
            self.edges[(v, u)] = edge  

    def find_substation(self, node_id):  
        """定位变电站节点（假设CB1~CB3为1, 2, 3）"""  
        if node_id in [1, 2, 3]:  
            return node_id  
        for neighbor in self.adjacency.get(node_id, []):  
            if neighbor in [1, 2, 3]:  
                return neighbor  
        return 0  # 默认返回CB1  

    def reset_capacity(self):
        """恢复所有边的原始容量"""
        for edge in self.edges.values():
            edge["capacity"] = edge["original_capacity"]

    def edmonds_karp(self, source, sink):
        """Edmonds-Karp 算法计算最大流（基于 BFS）"""
        max_flow = 0
        parent = {}

        def bfs():
            parent.clear()
            visited = set()
            queue = deque([source])
            visited.add(source)
            while queue:
                u = queue.popleft()
                for v in self.adjacency.get(u, []):
                    if v not in visited and self.edges[(u, v)]["capacity"] > 0:
                        visited.add(v)
                        parent[v] = u
                        queue.append(v)
                        if v == sink:
                            return True
            return False

        while bfs():
            path_flow = float("inf")
            v = sink
            while v != source:
                u = parent[v]
                path_flow = min(path_flow, self.edges[(u, v)]["capacity"])
                v = u
            max_flow += path_flow
            v = sink
            while v != source:
                u = parent[v]
                self.edges[(u, v)]["capacity"] -= path_flow
                self.edges[(v, u)]["capacity"] += path_flow
                v = u
        return max_flow
'''  

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
'''

# ---------------------- 风险评估模型 ----------------------  
class RiskAnalyzer:  
    def __init__(self, grid):  
        self.grid = grid  
        self.rated_current = 220  # 额定电流220A
        self.user_weights = {
    "居民": 1.0,
    "商业": 2.5,
    "政府和机构": 3.0,
    "办公和建筑": 2.0  # 新增
}


    def failure_probability(self, line):  
        """线路故障率计算"""  
        u, v = line  
        edge = self.grid.edges.get(line, {})  
        line_fault = edge.get("length", 0) * 0.002  
        switch_fault = 0.002  
        dg_fault = 0.005 if self.grid.nodes[u]["DG"] else 0  
        return line_fault + switch_fault + dg_fault  

    def load_loss_risk(self, line):  
        """失负荷风险计算"""  
        u, v = line  
        P_f = self.failure_probability(line)  
        source = self.grid.find_substation(u)  
        sink = self.grid.find_substation(v)  
        L_transfer = self.grid.edmonds_karp(source, sink)  
        L_load = self.grid.nodes[u]["power"] + self.grid.nodes[v]["power"]  
        L_loss = max(L_load - L_transfer, 0)  
        user_type = self.grid.nodes[u]["type"]  
        C_loss = self.user_weights[user_type] * L_loss  
        return P_f * C_loss  

    def overload_risk(self, line):  
        """过负荷风险计算"""  
        u, v = line  
        P_dg = self.grid.nodes[u]["power"] if self.grid.nodes[u]["DG"] else 0  
        P_load = self.grid.nodes[u]["power"]  
        P_net = P_dg - P_load  
        if P_net <= 0:  
            return 0  

        # 计算可转移功率  
        P_transfer_max = 0  
        for neighbor in self.grid.adjacency.get(u, []):  
            edge = self.grid.edges.get((u, neighbor), {})  
            C_ij = edge.get("capacity", 0)  
            P_load_j = self.grid.nodes[neighbor]["power"]  
            P_dg_j = self.grid.nodes[neighbor]["power"] if self.grid.nodes[neighbor]["DG"] else 0  
            available = max(P_load_j - P_dg_j, 0)  
            P_transfer_max += min(C_ij, available)  

        overload = max(P_net - P_transfer_max, 0)  
        I = overload * 1e3 / (10e3 * np.sqrt(3) * 0.9)  # 电流计算  
        C_over = 100 * max(I - 1.1 * self.rated_current, 0)  
        return C_over  

# ---------------------- 问题求解函数 ----------------------  
import numpy as np
import matplotlib.pyplot as plt
from tqdm.rich import tqdm
import copy

# 假设这些类和函数已在其他模块中定义：
# from your_module import load_data, PowerGridGraph, RiskAnalyzer
def problem1():
    """问题1：验证一条线路的失负荷与过负荷风险"""
    nodes, edges = load_data(limit=10)  # 测试用小规模数据
    grid = PowerGridGraph(nodes, edges)
    analyzer = RiskAnalyzer(grid)

    line = (5, 6)
    risk_loss = analyzer.load_loss_risk(line)
    risk_over = analyzer.overload_risk(line)

    print(f"线路 {line} 风险评估：失负荷 = {risk_loss:.2f}，过负荷 = {risk_over:.2f}")


def problem2():
    """问题2：分析 DG 容量从 300 至 900kW 的风险演变曲线"""
    raw_nodes, edges = load_data(limit=10)
    capacities = np.arange(300, 901, 90)
    risks = []

    grid = PowerGridGraph(copy.deepcopy(raw_nodes), edges)
    analyzer = RiskAnalyzer(grid)

    for cap in tqdm(capacities, desc="问题2：容量模拟中"):
        # 修改 DG 节点容量
        for node in grid.nodes.values():
            if node.get("DG"):
                node["power"] = cap

        total_risk = 0
        for line in grid.edges:
            u, v = line
            if grid.nodes[u].get("DG") or grid.nodes[v].get("DG"):
                total_risk += analyzer.load_loss_risk(line) + analyzer.overload_risk(line)

        risks.append(total_risk)

    plt.plot(capacities, risks, 'r-o')
    plt.xlabel("DG 单机容量 (kW)")
    plt.ylabel("系统总风险")
    plt.title("问题2：DG 容量 vs 系统风险")
    plt.grid()
    plt.show()


def problem3():
    """问题3：光伏典型出力下，不同最大接入容量对系统风险影响"""
    nodes, edges = load_data(limit=10)
    grid = PowerGridGraph(copy.deepcopy(nodes), edges)
    analyzer = RiskAnalyzer(grid)

    # 典型光伏出力曲线展示
    t = np.linspace(6, 18, 100)
    P_pv = 300 * np.sin(np.pi * (t - 6) / 12) ** 2

    plt.plot(t, P_pv)
    plt.title("典型光伏出力曲线")
    plt.xlabel("时间 (h)")
    plt.ylabel("出力功率 (kW)")
    plt.grid()
    plt.show()

    node_id = 32  # 示例节点
    capacities = np.linspace(300, 900, 7)
    risks = []

    for cap in tqdm(capacities, desc="问题3：PV容量仿真"):
        grid.nodes[node_id]["power"] = cap
        analyzer = RiskAnalyzer(grid)

        neighbors = grid.adjacency.get(node_id, [])
        if neighbors:
            line = (node_id, neighbors[0])
            risks.append(analyzer.overload_risk(line))
        else:
            risks.append(0)

    plt.plot(capacities, risks, 'b-s')
    plt.xlabel("光伏最大接入容量 (kW)")
    plt.ylabel("过负荷风险")
    plt.title("问题3：PV容量 vs 风险")
    plt.grid()
    plt.show()


def problem4():
    """问题4：在光伏节点配置 15% 储能前后的风险比较"""
    nodes, edges = load_data(limit=10)
    grid = PowerGridGraph(copy.deepcopy(nodes), edges)
    node_id = 32

    def apply_storage(node, ratio=0.15):
        """将原光伏容量削减 ratio 的比例用于储能吸纳"""
        node["power"] *= (1 - ratio)

    capacities = np.arange(300, 901, 90)
    risks_no_storage = []
    risks_with_storage = []

    for cap in tqdm(capacities, desc="问题4：储能对比仿真"):
        grid.nodes[node_id]["power"] = cap
        analyzer = RiskAnalyzer(grid)

        neighbors = grid.adjacency.get(node_id, [])
        if neighbors:
            line = (node_id, neighbors[0])
            risks_no_storage.append(analyzer.overload_risk(line))
        else:
            risks_no_storage.append(0)

        # 配置储能后再评估
        apply_storage(grid.nodes[node_id])
        analyzer = RiskAnalyzer(grid)
        if neighbors:
            risks_with_storage.append(analyzer.overload_risk(line))
        else:
            risks_with_storage.append(0)

    plt.plot(capacities, risks_no_storage, 'r--o', label="无储能")
    plt.plot(capacities, risks_with_storage, 'g-o', label="储能15%")
    plt.xlabel("光伏接入容量 (kW)")
    plt.ylabel("过负荷风险")
    plt.title("问题4：储能对系统风险影响")
    plt.legend()
    plt.grid()
    plt.show()



# ---------------------- 主程序 ----------------------  
if __name__ == "__main__":  
    print("===== 问题1 =====")  
    problem1()

    print("\n===== 问题2 =====")  
    problem2()  
    print("\n===== 问题3 =====")  
    problem3()  
    print("\n===== 问题4 =====")  
    problem4()  