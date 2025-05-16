
"""
RiskAnalyzer.py
本模块定义了 RiskAnalyzer 类，用于对电力网络中的风险进行分析和评估。主要功能包括：
- 计算电网边的容量
- 刷新所有边的容量信息
- 使用 Edmonds-Karp 算法计算网络最大流
- 计算线路的故障概率
- 评估线路的失负荷风险
- 评估线路的过载风险
类:
    RiskAnalyzer
        用于分析电力网络中各类风险，包括失负荷风险和过载风险。
方法:
    __init__(self, nodes_info:dict[str, dict], edges_info:list[dict[tuple,dict]])
        初始化 RiskAnalyzer 实例，加载节点和边的信息，构建无向图。
    capacity(self, u:int, v:int) -> float
        计算并返回指定边 (u, v) 的容量。
    refreash_capacity(self) -> None
        刷新所有边的容量信息。
    edmonds_karp(self, source, sink) -> float
        使用 Edmonds-Karp 算法计算从源点到汇点的最大流。
    failure_probability(self, line:tuple) -> float
        计算指定线路的故障概率。
    load_loss_risk(self, line) -> float
        计算指定线路的失负荷风险。
    overload_risk(self, line) -> float
        计算指定线路的过载风险。
依赖:
    - pandas
    - numpy
    - matplotlib
    - collections.deque
    - json
    - loguru
    - utils.tool (自定义工具模块)
"""
import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
from collections import deque 
import json 

from utils.tool import *

from loguru import logger

class RiskAnalyzer:  
    def __init__(self, nodes_info:dict[str, dict], edges_info:list[dict[tuple,dict]]):
        self.nodes_info = nodes_info.copy()  # 深拷贝节点信息
        self.edges_info = edges_info.copy()  # 深拷贝边信息 
        self.graph = UndirectedGraph(nodes_info, edges_info)  # 创建无向图对象
        self.rated_current = 220  # 额定电流220A
        self.user_weights = {
            "居民": 1.0,
            "商业": 2.5,
            "政府和机构": 3.0,
            "办公和建筑": 2.0  # 新增
        }
        logger.info("RiskAnalyzer初始化完成。")

    def capacity(self, u:int, v:int) -> float:
        logger.info(f"正在计算边({u}, {v})的容量")
        try:
            assert self.graph.get_edge_attribute(u, v, 'Resistor') is not None, "边(u, v)不存在Resistor属性"
            assert self.graph.get_edge_attribute(u, v, 'Reactance') is not None, "边(u, v)不存在Reactance属性"

            R_val = self.graph.get_edge_attribute(u, v, 'Resistor')
            X_val = self.graph.get_edge_attribute(u, v, 'Reactance')

            if R_val is None or isinstance(R_val, dict):
                logger.error(f"边({u}, {v})的Resistor值无效: {R_val}")
                raise ValueError(f"边({u}, {v})的Resistor值无效: {R_val}")
            if X_val is None or isinstance(X_val, dict):
                logger.error(f"边({u}, {v})的Reactance值无效: {X_val}")
                raise ValueError(f"边({u}, {v})的Reactance值无效: {X_val}")
            R = float(R_val)
            X = float(X_val)
            Z = np.sqrt(R**2 + X**2)
            V = 10e3
            capacity = (V**2 / Z) * 0.9 
            logger.info(f"边({u}, {v})的容量为{capacity}")
            return capacity
        except Exception as e:
            logger.error(f"计算边({u}, {v})容量时出错: {e}")
            raise

    def refreash_capacity(self) -> None:
        logger.info("正在刷新所有边的容量...")
        try:
            for edge in self.edges_info:
                edge_tuple = list(edge.keys())[0]
                if isinstance(edge_tuple, tuple) and len(edge_tuple) == 2:
                    u, v = edge_tuple
                else:
                    logger.error(f"边的key不是包含两个元素的元组: {edge_tuple}")
                    raise ValueError(f"边的key不是包含两个元素的元组: {edge_tuple}")
                capacity = self.capacity(u, v)
                edge[(u, v)]['capacity'] = capacity
                logger.info(f"已更新边({u}, {v})的容量: {capacity}")
            logger.info("所有边的容量已刷新。")
        except Exception as e:
            logger.error(f"刷新容量时出错: {e}")
            raise

    def edmonds_karp(self, source, sink) -> float:
        logger.info(f"正在运行Edmonds-Karp算法，源点: {source}，汇点: {sink}")
        max_flow = 0
        parent = {}

        def bfs():
            parent.clear()
            visited = set()
            queue = deque([source])
            visited.add(source)
            while queue:
                u = queue.popleft()
                for v in self.graph.neighbors(u):
                    try:
                        if v not in visited and self.capacity(u, v) > 0:
                            visited.add(v)
                            parent[v] = u
                            queue.append(v)
                            if v == sink:
                                return True
                    except Exception as e:
                        logger.error(f"BFS过程中边({u}, {v})出错: {e}")
                        continue
            return False

        try:
            while bfs():
                path_flow = float("inf")
                v = sink
                while v != source:
                    u = parent[v]
                    path_flow = min(path_flow, self.capacity(u, v))
                    v = u
                max_flow += path_flow
                v = sink
                while v != source:
                    u = parent[v]
                    for edge in self.edges_info:
                        key = list(edge.keys())[0]
                        if key == (u, v):
                            edge[key]["capacity"] -= path_flow
                        elif key == (v, u):
                            edge[key]["capacity"] += path_flow
                    v = u
                logger.info(f"增广路径流量为{path_flow}，当前最大流: {max_flow}")
            logger.info(f"Edmonds-Karp算法结束，最大流: {max_flow}")
            return max_flow
        except Exception as e:
            logger.error(f"Edmonds-Karp算法出错: {e}")
            raise

    def failure_probability(self, line:tuple) -> float:  
        logger.info(f"正在计算线路{line}的故障概率")
        try:
            u, v = line  
            edge = self.graph.get_edge(u, v)
            line_fault = edge['length'] * 0.002  
            switch_fault = 0.002  
            dg_fault = 0.005 if self.nodes_info[str(u)]['DG'] else 0  
            prob = line_fault + switch_fault + dg_fault  
            logger.info(f"线路{line}的故障概率为{prob}")
            return prob
        except Exception as e:
            logger.error(f"计算线路{line}故障概率时出错: {e}")
            raise

    def load_loss_risk(self, line) -> float:  
        logger.info(f"正在计算线路{line}的失负荷风险")
        try:
            u, v = line 
            u = str(u)
            v = str(v) 
            P_f = self.failure_probability(line)  
            source = self.nodes_info[str(u)]["which_substation"]
            sink = self.nodes_info[str(v)]["which_substation"] 
            L_transfer = self.edmonds_karp(source, sink)  
            L_load = self.nodes_info[u]["power"] + self.nodes_info[str(v)]["power"]  
            L_loss = max(L_load - L_transfer, 0)  
            user_type = self.nodes_info[str(u)]["type"]  
            C_loss = self.user_weights[user_type] * L_loss  
            risk = P_f * C_loss  
            logger.info(f"线路{line}的失负荷风险为{risk}")
            return risk
        except Exception as e:
            logger.error(f"计算线路{line}失负荷风险时出错: {e}")
            raise

    def overload_risk(self, line) -> float:  
        logger.info(f"正在计算线路{line}的过载风险")
        try:
            u, v = line
            u = str(u)
            v = str(v)
            P_dg = self.nodes_info[u]["power"] if self.nodes_info[u]["DG"] else 0  
            P_load = self.nodes_info[u]["power"]  
            P_net = P_dg - P_load  
            if P_net <= 0:  
                logger.info(f"线路{line}无过载风险（P_net <= 0）")
                return 0  
            P_transfer_max = 0  
            for neighbor in self.graph.neighbors(int(u)):  
                try:
                    C_ij = self.graph.get_edge_attribute((u, neighbor), "capacity")  
                    P_load_j = self.nodes_info[str(neighbor)]["power"]  
                    P_dg_j = self.nodes_info[str(neighbor)]["power"] if self.nodes_info[str(neighbor)]["DG"] else 0  
                    available = max(P_load_j - P_dg_j, 0)  
                    # Ensure C_ij is a valid number
                    if isinstance(C_ij, (int, float)):
                        P_transfer_max += min(C_ij, available)
                    else:
                        logger.error(f"边({u}, {neighbor})的capacity无效: {C_ij}")
                        continue
                except Exception as e:
                    logger.error(f"计算{u}的邻居{neighbor}转移能力时出错: {e}")
                    continue
            overload = max(P_net - P_transfer_max, 0)  
            I = overload * 1e3 / (10e3 * np.sqrt(3) * 0.9)  
            C_over = 100 * max(I - 1.1 * self.rated_current, 0)  
            logger.info(f"线路{line}的过载风险为{C_over}")
            return C_over  
        except Exception as e:
            logger.error(f"计算线路{line}过载风险时出错: {e}")
            raise