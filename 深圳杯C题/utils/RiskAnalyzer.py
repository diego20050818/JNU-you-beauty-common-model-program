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
        # 深拷贝节点和边的信息，防止外部修改影响内部数据
        self.nodes_info = nodes_info.copy()  
        self.edges_info = edges_info.copy()  
        # 创建无向图对象，便于后续图算法操作
        self.graph = UndirectedGraph(nodes_info, edges_info)  
        self.rated_current = 220  # 额定电流220A
        # 用户类型权重，用于失负荷风险评估
        self.user_weights = {
            "居民": 1.0,
            "商业": 2.5,
            "政府和机构": 3.0,
            "办公和建筑": 2.0  # 新增
        }
        logger.info("RiskAnalyzer初始化完成。")

    def _capacity(self, u:int, v:int) -> float:
        """
        计算并返回指定边 (u, v) 的容量。
        容量计算公式：(V^2 / Z) * 0.9，Z为阻抗，V为电压
        """
        logger.info(f"正在计算边({u}, {v})的容量")
        try:
            # 检查边是否有Resistor和Reactance属性
            assert self.graph.get_edge_attribute(u, v, 'Resistor') is not None, "边(u, v)不存在Resistor属性"
            assert self.graph.get_edge_attribute(u, v, 'Reactance') is not None, "边(u, v)不存在Reactance属性"

            R_val = self.graph.get_edge_attribute(u, v, 'Resistor')
            X_val = self.graph.get_edge_attribute(u, v, 'Reactance')

            # 检查属性值有效性
            if R_val is None or isinstance(R_val, dict):
                logger.error(f"边({u}, {v})的Resistor值无效: {R_val}")
                raise ValueError(f"边({u}, {v})的Resistor值无效: {R_val}")
            if X_val is None or isinstance(X_val, dict):
                logger.error(f"边({u}, {v})的Reactance值无效: {X_val}")
                raise ValueError(f"边({u}, {v})的Reactance值无效: {X_val}")
            # 计算阻抗Z
            R = float(R_val)
            X = float(X_val)
            Z = np.sqrt(R**2 + X**2)
            V = 10e3  # 电压10kV
            capacity = (V**2 / Z) * 0.9  # 乘以0.9为安全系数
            cos = 0.95 # 功率因数
            capacity = capacity * cos / 10e6 # 考虑功率因数
            # 检查容量是否有效
            if capacity <= 0:
                logger.error(f"计算的边({u}, {v})容量无效: {capacity}")
                raise ValueError(f"计算的边({u}, {v})容量无效: {capacity}")
            
            logger.info(f"边({u}, {v})的容量为{capacity:4f}MW")
            return capacity
        except Exception as e:
            logger.error(f"计算边({u}, {v})容量时出错: {e}")
            raise

    def capacity(self, u: int, v: int) -> float:
        """
        计算并返回指定边 (u, v) 的容量。
        容量计算公式：sqrt(3) * V * (I_0 * Z_0 / Z) * cos(phi)，其中 V 为线电压，I_0 为基准电流，Z_0 为基准阻抗，Z 为实际阻抗，cos(phi) 为功率因数
        """
        logger.info(f"正在计算边({u}, {v})的容量")
        try:
            # 检查边是否有Resistor和Reactance属性
            assert self.graph.get_edge_attribute(u, v, 'Resistor') is not None, "边(u, v)不存在Resistor属性"
            assert self.graph.get_edge_attribute(u, v, 'Reactance') is not None, "边(u, v)不存在Reactance属性"

            R_val = self.graph.get_edge_attribute(u, v, 'Resistor')
            X_val = self.graph.get_edge_attribute(u, v, 'Reactance')

            # 检查属性值有效性
            if R_val is None or isinstance(R_val, dict):
                logger.error(f"边({u}, {v})的Resistor值无效: {R_val}")
                raise ValueError(f"边({u}, {v})的Resistor值无效: {R_val}")
            if X_val is None or isinstance(X_val, dict):
                logger.error(f"边({u}, {v})的Reactance值无效: {X_val}")
                raise ValueError(f"边({u}, {v})的Reactance值无效: {X_val}")

            # 计算阻抗 Z
            R = float(R_val)
            X = float(X_val)
            Z = np.sqrt(R**2 + X**2)

            # 参数定义
            V = 10e3       # 电压 10kV
            cos = 0.95     # 功率因数
            I_0 = 231.5    # 基准电流 231.5A（基于 3.81 MW 反推）
            Z_0 = 0.0592   # 基准阻抗 0.0592Ω（边 (15, 16) 的阻抗）

            # 容量计算：P = sqrt(3) * V * (I_0 * Z_0 / Z) * cos(phi) / 10^6
            capacity = (np.sqrt(3) * V * (I_0 * Z_0 / Z) * cos) / 10e3

            # 检查容量是否有效
            if capacity <= 0:
                logger.error(f"计算的边({u}, {v})容量无效: {capacity}")
                raise ValueError(f"计算的边({u}, {v})容量无效: {capacity}")
            
            logger.info(f"边({u}, {v})的容量为{capacity:.4f} kW")
            return capacity
        except Exception as e:
            logger.error(f"计算边({u}, {v})容量时出错: {e}")
            raise

    def refreash_capacity(self) -> None:
        """
        刷新所有边的容量信息，将最新容量写入每条边的属性中
        """
        logger.info("正在刷新所有边的容量...")
        try:
            for edge in self.edges_info:
                edge_tuple = list(edge.keys())[0]
                # 检查边的key格式
                if isinstance(edge_tuple, tuple) and len(edge_tuple) == 2:
                    u, v = edge_tuple
                else:
                    logger.error(f"边的key不是包含两个元素的元组: {edge_tuple}")
                    raise ValueError(f"边的key不是包含两个元素的元组: {edge_tuple}")
                # 计算容量并写入
                capacity = self.capacity(u, v)
                edge[(u, v)]['capacity'] = capacity
                logger.info(f"已更新边({u}, {v})的容量: {capacity}")
            logger.info("所有边的容量已刷新。")
        except Exception as e:
            logger.error(f"刷新容量时出错: {e}")
            raise



    def edmonds_karp(self, source, sink) -> float:
        """
        使用Edmonds-Karp算法计算从源点到汇点的最大流
        """

        # 映射电站名称到其连接的数字节点编号
        substation_map = {
            'CB1': '1',
            'CB2': '43',
            'CB3': '23',
        }

        # 映射 source 和 sink（如果是字符串）
        source = substation_map.get(source, source)
        sink = substation_map.get(sink, sink)


        logger.info(f"正在运行Edmonds-Karp算法，源点: {source}，汇点: {sink}")

        # 不允许源点和汇点相同
        if source == sink:
            logger.warning(f"[跳过最大流] 源点和汇点相同（{source}），无跨馈线转供")
            return 0.0

        max_flow = 0
        parent = {}

        def bfs():
            """
            广度优先搜索，寻找一条增广路径
            """
            parent.clear()
            visited = set()
            queue = deque([source])
            visited.add(source)

            while queue:
                u = queue.popleft()
                if u is None:
                    continue
                for v in self.graph.neighbors(int(u)):
                    try:
                        if v not in visited and self.capacity(int(u), v) > 0:
                            parent[v] = u
                            visited.add(v)
                            queue.append(str(v))
                            if v == sink:
                                return True
                    except Exception as e:
                        logger.error(f"[BFS出错] 边({u}, {v}): {e}")
            return False

        try:
            # 主循环：不断寻找增广路径，直到没有
            while bfs():
                path_flow = float("inf")
                v = sink

                # 回溯路径，确定最小残余容量
                while v != source:
                    u = parent[v]
                    # 确保u和v都是int类型且不为None
                    u_int = int(u) if u is not None else 0
                    v_int = int(v) if v is not None else 0
                    path_flow = min(path_flow, self.capacity(u_int, v_int))
                    v = u

                # 更新流量
                max_flow += path_flow

                # 更新残余图
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

                logger.info(f"增广路径流量: {path_flow:.2f}，累计最大流: {max_flow:.2f}")

            logger.info(f"Edmonds-Karp算法完成，总最大流: {max_flow:.2f}")
            return max_flow

        except Exception as e:
            logger.error(f"[最大流计算异常] {e}")
            raise


    def failure_probability(self, line:tuple) -> float:  
        """
        计算指定线路的故障概率
        故障概率 = 线路长度*0.002 + 开关故障概率 + DG故障概率
        """
        logger.info(f"正在计算线路{line}的故障概率")
        try:
            u, v = line  
            edge = self.graph.get_edge(u, v)
            line_fault = edge['length'] * 0.002  # 线路长度相关故障概率
            switch_fault = 0.002  # 开关故障概率
            dg_fault = 0.005 if self.nodes_info[str(u)]['DG'] else 0  # DG故障概率
            prob = line_fault + switch_fault + dg_fault  
            logger.info(f"线路{line}的故障概率为{prob}")
            return prob
        except Exception as e:

            logger.error(f"计算线路{line}故障概率时出错: {e}")
            return -1.0

    def load_loss_risk(self, line:tuple) -> float:  
        """
        计算指定线路的失负荷风险
        风险 = 故障概率 * 失负荷损失
        """
        logger.info(f"正在计算线路{line}的失负荷风险")
        try:
            u, v = line 
            u = str(u)
            v = str(v) 
            P_f = self.failure_probability(line)  # 故障概率
            # 获取源点和汇点（所属变电站）
            source = self.nodes_info[str(u)]["which_substation"]
            sink = self.nodes_info[str(v)]["which_substation"] 
            L_transfer = self.edmonds_karp(source, sink)  # 最大可转移负荷
            L_load = self.nodes_info[u]["power"] + self.nodes_info[str(v)]["power"]  # 总负荷
            L_loss = max(L_load - L_transfer, 0)  # 失负荷
            user_type = self.nodes_info[str(u)]["type"]  # 用户类型
            C_loss = self.user_weights[user_type] * L_loss  # 损失权重
            risk = P_f * C_loss  # 风险值
            logger.info(f"线路{line}的失负荷风险为{risk}")
            return risk
        except Exception as e:
            logger.error(f"计算线路{line}失负荷风险时出错: {e}")
            raise

    def _overload_risk(self, line) -> float:  
        """
        计算指定线路的过载风险
        """
        logger.info(f"正在计算线路{line}的过载风险")
        try:
            u, v = line
            u = str(u)
            v = str(v)
            # 计算DG出力
            P_dg = self.nodes_info[u]["power"] if self.nodes_info[u]["DG"] else 0  
            P_load = self.nodes_info[u]["power"]  # 节点负荷
            P_net = P_dg - P_load  # 节点净出力
            if P_net <= 0:  
                logger.info(f"线路{line}无过载风险（P_net <= 0）")
                return 0  
            P_transfer_max = 0  
            # 遍历邻居，计算最大可转移能力
            for neighbor in self.graph.neighbors(int(u)):  
                try:
                    C_ij = self.graph.get_edge_attribute((u, neighbor), "capacity")  
                    P_load_j = self.nodes_info[str(neighbor)]["power"]  
                    P_dg_j = self.nodes_info[str(neighbor)]["power"] if self.nodes_info[str(neighbor)]["DG"] else 0  
                    available = max(P_load_j - P_dg_j, 0)  
                    # 确保容量有效
                    if isinstance(C_ij, (int, float)):
                        P_transfer_max += min(C_ij, available)
                    else:
                        logger.error(f"边({u}, {neighbor})的capacity无效: {C_ij}")
                        continue
                except Exception as e:
                    logger.error(f"计算{u}的邻居{neighbor}转移能力时出错: {e}")
                    continue
            overload = max(P_net - P_transfer_max, 0)  # 过载量
            # 计算过载电流
            I = overload * 1e3 / (10e3 * np.sqrt(3) * 0.9)  
            # 计算过载风险指标
            C_over = 100 * max(I - 1.1 * self.rated_current, 0)  
            logger.info(f"线路{line}的过载风险为{C_over}")
            return C_over  
        except Exception as e:
            logger.error(f"计算线路{line}过载风险时出错: {e}")
            raise

    def overload_risk(self, line) -> float:
        """
        计算指定线路的过载风险，考虑馈线间功率转移，禁止向变电站倒送。
        过载定义：线路电流超过额定载流量 10% 以上。

        ### 公式推导

        #### 1. 功率流计算
        - **节点净出力**：
        $$
        P_{\text{net}} = P_{\text{dg}} - P_{\text{load}}
        $$
        - \( P_{\text{dg}} \): 分布式电源出力，若 `DG = True`，则 \( P_{\text{dg}} = 0.3 \, \text{MW} \)；否则 0。
        - \( P_{\text{load}} \): 节点负荷功率，从 `nodes_info[u]["power"]` 获取（kW，转换为 MW）。
        - **线路功率流**：
        $$
        P_{\text{flow}} = P_{\text{net}}
        $$
        - 假设功率从节点 \( u \) 流向 \( v \)，简化模型，未进行潮流分析。
        - **倒送检查**：
        - 若节点 \( v \) 连接变电站（`which_substation in ["CB1", "CB2", "CB3"]`）且 \( P_{\text{flow}} > 0 \)，视为倒送，风险为 0。

        #### 2. 馈线间功率转移
        - 对于节点 \( u \) 的邻居 \( j \)（通过联络线，`联络开关 != "None"`）：
        - **负荷余量**：
            $$
            \text{available}_j = \max(P_{\text{load},j} - P_{\text{dg},j}, 0)
            $$
        - **可转移功率**：
            $$
            P_{\text{transfer},j} = \min(C_{ij}, \text{available}_j)
            $$
            - \( C_{ij} \): 边 (u, j) 或 (j, u) 的容量（MW）。
        - **总转移功率**：
            $$
            P_{\text{transfer_max}} = \sum_j P_{\text{transfer},j}
            $$

        #### 3. 过载量
        - $$
        \text{overload} = \max(P_{\text{flow}} - P_{\text{transfer_max}}, 0)
        $$
        - 单位：MW。

        #### 4. 线路电流
        - $$
        I = \frac{\text{overload} \cdot 10^3}{\sqrt{3} \cdot V \cdot \cos\phi}
        $$
        - \( \text{overload} \): MW，转换为 kW (\( \cdot 10^3 \)).
        - \( V = 10,000 \, \text{V} \)，\( \cos\phi = 0.95 \)。
        - \( I \): 安培。

        #### 5. 过载风险
        - 额定电流：\( I_{\text{rated}} = 220 \, \text{A} \).
        - 风险指标：
        $$
        C_{\text{over}} = 100 \cdot \max(I - 1.1 \cdot I_{\text{rated}}, 0)
        $$
        - 乘以 100 为放大系数。

        ### 参数
        - `line`: 元组 (u, v)，表示线路的起点和终点。
        - 返回：过载风险值 \( C_{\text{over}} \)。
        """
        logger.info(f"正在计算线路{line}的过载风险")
        try:
            u, v = line
            u = str(u)
            v = str(v)
            # 计算节点 u 的净出力，单位 MW
            P_dg = 0.3 if self.nodes_info[u]["DG"] else 0  # DG 固定 0.3 MW
            P_load = self.nodes_info[u]["power"] / 1000  # 负荷 kW 转 MW
            P_net = P_dg - P_load  # 净出力（MW）

            # 估算线路 (u, v) 的功率流
            P_flow = P_net  # 假设功率从 u 流向 v
            # 检查是否倒送至变电站
            if "which_substation" in self.nodes_info[v] and self.nodes_info[v]["which_substation"] in ["CB1", "CB2", "CB3"]:
                if P_flow > 0:  # 正向流向变电站（倒送）
                    logger.info(f"线路{line}功率倒送至变电站，忽略过载风险")
                    return 0

            # 计算可转移功率（通过联络线）
            P_transfer_max = 0
            for neighbor in self.graph.neighbors(int(u)):
                try:
                    #neighbor = str(neighbor)
                    #edge = (u, neighbor) if self.graph.get_edge_attribute(u, neighbor, "capacity") is not None else (neighbor, u)
                    _neighbor,_u = int(neighbor),int(u)
                    # 检查是否为联络线
                    if self.graph.get_edge_attribute(_neighbor,_u, "联络开关") != "None":
                        C_ij = self.graph.get_edge_attribute(_neighbor,_u, "capacity")
                        P_load_j = self.nodes_info[neighbor]["power"] / 1000  # kW 转 MW
                        P_dg_j = 0.3 if self.nodes_info[neighbor]["DG"] else 0
                        available = max(P_load_j - P_dg_j, 0)  # 邻居负荷余量
                        if isinstance(C_ij, (int, float)):
                            P_transfer_max += min(C_ij, available)
                        else:
                            logger.error(f"边{neighbor,u}的capacity无效: {C_ij}")
                            continue
                except Exception as e:
                    logger.error(f"计算{u}的邻居{neighbor}转移能力时出错: {e}")
                    continue

            # 计算过载量
            overload = max(P_flow - P_transfer_max, 0)  # 单位 MW
            # 计算线路电流
            I = overload * 1e3 / (10e3 * np.sqrt(3) * 0.95)  # 单位：安培
            # 过载风险（额定电流 220 A）
            rated_current = 220.0
            C_over = 100 * max(I - 1.1 * rated_current, 0)
            logger.info(f"线路{line}的过载风险为{C_over:.4f}")
            return C_over
        except Exception as e:
            logger.error(f"计算线路{line}过载风险时出错: {e}")
            raise