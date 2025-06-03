import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import deque, defaultdict
import json
import copy
from typing import Optional, Dict, List, Tuple, Set

from utils.tool import UndirectedGraph
from utils.data_loder import nodes_info, edges_info
from loguru import logger

class RiskAnalyzer:
    """
    电网风险分析器类

    用于对电力网络中的风险进行分析和评估，支持失负荷风险、过载风险等多种指标的计算。
    支持灵活配置参数，便于扩展和维护。

    主要功能：
    1. 电网拓扑分析
    2. 潮流计算和线路电流分析（考虑分布式能源）
    3. 故障概率计算
    4. 失负荷风险评估
    5. 过载风险评估

    版本：2025年6月3日
    """

    def __init__(self, nodes_info: Dict[str, Dict], edges_info: List[Dict[Tuple, Dict]], rated_current: float = 220.0):
        """
        初始化 RiskAnalyzer 实例

        Args:
            nodes_info: 节点信息字典，格式为 {node_id: {type, power, DG, which_substation}}
            edges_info: 边信息列表，格式为 [{(begin, end): {length, type, 分段开关, 联络开关, Resistor, Reactance}}]
            rated_current: 额定电流，默认 220A
        """
        # 基础数据初始化
        self._nodes_info = nodes_info.copy()
        self._edges_info = edges_info.copy()
        self._graph = UndirectedGraph(self._nodes_info, self._edges_info)
        self._rated_current = rated_current

        # 深圳市用户类型负荷波动权重参数表
        self._user_weights = {
            "居民": 0.05,
            "商业": 0.12,
            "政府和机构": 0.10,
            "办公和建筑": 0.08
        }

        # 用户类型危害度权重系数
        self._damage_weights = {
            "居民": 1.0,
            "商业": 2.5,
            "政府和机构": 3.0,
            "办公和建筑": 2.5
        }

        # 线路过载危害系数
        self._line_overload_damage_weights = {
            "居民": 1.0,
            "商业": 2.5,
            "政府和机构": 3.0,
            "办公和建筑": 2.5
        }

        # 故障率参数设置
        self.node_risk = 0.005              # 每个用户节点的故障率
        self.dg_risk = 0.005                # 每个分布式能源的故障概率
        self.switch_risk = 0.002            # 每个开关的故障率
        self.edge_each_length_risk = 0.002  # 配电线路单位长度故障率

        # 电网参数设置
        self.feeder_capacity = 2200         # 馈线额定容量 (kW)
        self.feeder_current_limit = 220     # 馈线额定电流 (A)
        self.voltage = 10e2                 # 电压等级 (V) - 10kV
        self.dg_capacity = 3e4              # 分布式能源容量 (kW) - 300kW
        self.cos = 0.9                      # 功率因数

        # 变电站映射表
        self._substation_map = {
            "CB1": '1',
            "CB2": '43',
            "CB3": '23'
        }

        # 缓存潮流计算结果
        self._power_flow_cache = {}

        # 初始化边-用户类型映射
        self._initialize_edge_user_types()

        logger.info("RiskAnalyzer 初始化完成")

    def _initialize_edge_user_types(self):
        """
        初始化边与用户类型的映射关系
        """
        self.edge_user_types = {}
        for edge in self._edges_info:
            if isinstance(edge, dict):
                edge_id, edge_info = list(edge.items())[0]
                begin, end = edge_id
                begin_type = self._nodes_info.get(str(begin), {}).get('type', None)
                end_type = self._nodes_info.get(str(end), {}).get('type', None)
                types = set()
                if begin_type:
                    types.add(begin_type)
                if end_type:
                    types.add(end_type)
                self.edge_user_types[edge_id] = types
            else:
                begin, end = edge
                begin_type = self._nodes_info.get(str(begin), {}).get('type', None)
                end_type = self._nodes_info.get(str(end), {}).get('type', None)
                types = set()
                if begin_type:
                    types.add(begin_type)
                if end_type:
                    types.add(end_type)
                self.edge_user_types[(begin, end)] = types

    # ==================== 属性访问器 ====================

    @property
    def nodes_info(self) -> Dict:
        """获取节点信息"""
        return self._nodes_info

    @property
    def edges_info(self) -> List:
        """获取边信息"""
        return self._edges_info

    @property
    def rated_current(self) -> float:
        """获取额定电流"""
        return self._rated_current

    @property
    def dg_capacity(self) -> float:
        """获取分布式能源容量"""
        return self._dg_capacity

    @dg_capacity.setter
    def dg_capacity(self, value: float):
        """设置分布式能源容量"""
        self._dg_capacity = value
        # 清空相关缓存，确保新值生效
        self._power_flow_cache = {}

    # ==================== 基础计算方法 ====================

    def edge_risk(self, begin: int, end: int) -> float:
        """
        计算指定边的故障概率

        Args:
            begin: 起始节点
            end: 终止节点

        Returns:
            该边的故障概率
        """
        try:
            length = self._graph.get_edge_attribute(begin, end, 'length')
            return float(length) * self.edge_each_length_risk
        except Exception as e:
            logger.error(f"计算边({begin}, {end})故障概率时出错: {e}")
            return 0.0

    def calculate_capacity(self, begin: int, end: int) -> float:
        """
        计算两个节点间线路的传输容量，考虑分布式能源的贡献

        Args:
            begin: 起始节点
            end: 终止节点

        Returns:
            线路传输容量 (kW)
        """
        try:
            R = self._graph.get_edge_attribute(begin, end, 'Resistor')
            X = self._graph.get_edge_attribute(begin, end, 'Reactance')
            Z = complex(float(R), float(X))
            Z_abs = np.abs(Z)

            if Z_abs == 0:
                logger.warning(f"边({begin}, {end})阻抗为0")
                return 0.0

            capacity = np.square(self.voltage) / (Z_abs * self.cos) / 10e2  # 转换为 kW

            # 如果任一节点为 DG 节点，增加 DG 容量
            begin_is_dg = self._graph.get_node_attribute(str(begin), 'DG')
            end_is_dg = self._graph.get_node_attribute(str(end), 'DG')
            if begin_is_dg or end_is_dg:
                capacity += self.dg_capacity

            return min(capacity, self.feeder_capacity)  # 不超过馈线额定容量
        except Exception as e:
            logger.error(f"计算边({begin}, {end})容量时出错: {e}")
            return 0.0

    # ==================== 潮流分析相关方法 ====================

    def _get_edge_key(self, begin: int, end: int) -> Tuple[int, int]:
        """
        获取边的标准化键值（小节点在前）

        Args:
            begin: 起始节点
            end: 终止节点

        Returns:
            标准化的边键值元组
        """
        return (min(begin, end), max(begin, end))

    def _find_shortest_path_to_substation(self, start_node: str) -> Tuple[Optional[List[str]], float]:
        """
        使用 BFS 找到从指定节点到最近变电站的最短路径

        Args:
            start_node: 起始节点 ID

        Returns:
            (路径列表, 总距离) 或 (None, inf)
        """
        substations = ['1', '23', '43']
        if start_node in substations:
            return [start_node], 0.0

        queue = deque([(start_node, [start_node], 0.0)])
        visited = set()

        while queue:
            current, path, distance = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            if current in substations:
                return path, distance

            try:
                for neighbor in self._graph.neighbors(int(current)):
                    neighbor_str = str(neighbor)
                    if neighbor_str not in visited:
                        edge_length = self._graph.get_edge_attribute(int(current), neighbor, 'length')
                        new_path = path + [neighbor_str]
                        new_distance = distance + edge_length
                        queue.append((neighbor_str, new_path, new_distance))
            except Exception as e:
                logger.error(f"搜索节点 {current} 的邻居时出错: {e}")
                continue

        return None, float('inf')

    def calculate_power_flow_simple(self) -> Dict[Tuple[int, int], float]:
        """
        简化的潮流计算方法，考虑分布式能源的供电能力

        Returns:
            字典，键为边的标准化元组，值为该边承载的功率 (kW)
        """
        if self._power_flow_cache:
            return self._power_flow_cache

        edge_powers = defaultdict(float)

        for node_id, node_info in self._nodes_info.items():
            power_demand = node_info.get('power', 0)
            is_dg = node_info.get('DG', False)

            # 如果是 DG 节点，减少功率需求
            if is_dg and power_demand > 0:
                power_demand = max(power_demand - self.dg_capacity, 0)

            if power_demand > 0:
                path, min_distance = self._find_shortest_path_to_substation(node_id)
                if path and len(path) > 1:
                    for i in range(len(path) - 1):
                        edge_key = self._get_edge_key(int(path[i]), int(path[i+1]))
                        edge_powers[edge_key] += power_demand
                else:
                    logger.warning(f"节点 {node_id} 无法找到到变电站的路径")

        self._power_flow_cache = dict(edge_powers)
        return self._power_flow_cache

    # ==================== 最大流算法 ====================

    def edmons_krap(self, source: str, sink: str, use_tie: Tuple = (0, 0)) -> float:
        """
        使用 Edmonds-Karp 算法计算网络最大流，考虑分布式能源的贡献

        Args:
            source: 源点（变电站代码或节点 ID）
            sink: 汇点（节点 ID）
            use_tie: 是否启用联络线，默认 (0,0) 表示不启用

        Returns:
            最大流值 (kW)
        """
        source = self._substation_map.get(source, source)
        sink = self._substation_map.get(sink, sink)

        if source == sink:
            logger.warning(f"源点 {source} 和汇点 {sink} 相同，返回 0")
            return 0.0

        residual_capacity = {}
        for edge in self._edges_info:
            edge_id, edge_info = list(edge.items())[0]
            begin, end = edge_id
            capacity = self.calculate_capacity(begin, end)

            # 如果任一节点为 DG 节点，增加容量
            begin_is_dg = self._graph.get_node_attribute(str(begin), 'DG')
            end_is_dg = self._graph.get_node_attribute(str(end), 'DG')
            if begin_is_dg or end_is_dg:
                capacity += self.dg_capacity

            residual_capacity[(begin, end)] = capacity
            residual_capacity[(end, begin)] = capacity

        def bfs_find_path() -> Optional[List[str]]:
            parents = {}
            visited = set([source])
            queue = deque([source])
            while queue:
                u = queue.popleft()
                for v in self._graph.neighbors(int(u)):
                    v_str = str(v)
                    if v_str not in visited and residual_capacity.get((int(u), v), 0) > 0:
                        if (use_tie == (0, 0) and
                                self._graph.get_edge_attribute(int(u), v, "type") == "馈线间联络线"):
                            continue
                        parents[v_str] = u
                        visited.add(v_str)
                        queue.append(v_str)
                        if v_str == sink:
                            path = []
                            current = sink
                            while current is not None:
                                path.append(current)
                                current = parents.get(current)
                            return path[::-1]
            return None

        max_flow = 0.0
        try:
            while True:
                path = bfs_find_path()
                if not path:
                    break
                path_flow = float("inf")
                for i in range(len(path) - 1):
                    u, v = int(path[i]), int(path[i + 1])
                    path_flow = min(path_flow, residual_capacity.get((u, v), 0))
                if path_flow == 0:
                    break
                for i in range(len(path) - 1):
                    u, v = int(path[i]), int(path[i + 1])
                    residual_capacity[(u, v)] -= path_flow
                    residual_capacity[(v, u)] += path_flow
                max_flow += path_flow
            return max_flow
        except Exception as e:
            logger.error(f"最大流计算异常: {e}")
            return 0.0

    # ==================== 故障概率计算 ====================

    def P_f(self) -> float:
        """
        计算全网故障概率

        Returns:
            全网故障概率
        """
        total_failure_prob = 0.0
        for edge in self.edges_info:
            edge_id, edge_info = list(edge.items())[0]
            begin, end = edge_id
            line_prob = edge_info['length'] * self.edge_each_length_risk
            if edge_info.get('分段开关') not in [None, 'None', '']:
                line_prob += self.switch_risk
            begin_has_dg = self._graph.get_node_attribute(str(begin), 'DG')
            end_has_dg = self._graph.get_node_attribute(str(end), 'DG')
            if begin_has_dg or end_has_dg:
                line_prob += self.dg_risk
            total_failure_prob += line_prob
        return total_failure_prob

    # ==================== 失负荷风险计算 ====================

    def C_ll(self) -> float:
        """
        计算失负荷危害度

        Returns:
            失负荷危害度
        """
        total_consequence = 0.0
        for node_id, node_data in self.nodes_info.items():
            node_type = node_data.get('type', '居民')
            weight = self._damage_weights.get(node_type, 1.0)
            load_demand = node_data.get('power', 0)
            if not node_data.get('DG', False) and load_demand > 0:
                max_transferable = 0.0
                for substation in ['CB1', 'CB2', 'CB3']:
                    try:
                        flow = self.edmons_krap(source=substation, sink=node_id)
                        max_transferable = max(max_transferable, flow)
                    except Exception as e:
                        logger.error(f"计算节点 {node_id} 到 {substation} 最大流时出错: {e}")
                        continue
                load_loss = max(load_demand - max_transferable, 0)
                consequence = weight * load_loss
                total_consequence += consequence
        return total_consequence

    def load_loss_risk(self) -> float:
        """
        计算全网失负荷风险，考虑分布式能源的供电能力

        Returns:
            失负荷风险值
        """
        total_risk = 0.0
        for node_id, node_data in self._nodes_info.items():
            power_demand = node_data.get('power', 0)
            if power_demand <= 0:
                continue
            failure_prob = self.dg_risk if node_data.get('DG', False) else self.node_risk
            effective_demand = power_demand
            if node_data.get('DG', False):
                effective_demand = max(power_demand - self.dg_capacity, 0)
            max_transfer = 0.0
            for substation in ['CB1', 'CB2', 'CB3']:
                try:
                    flow = self.edmons_krap(source=substation, sink=node_id)
                    max_transfer = max(max_transfer, flow)
                except Exception as e:
                    logger.error(f"计算节点 {node_id} 最大转移负荷时出错: {e}")
                    continue
            load_loss = max(effective_demand - max_transfer, 0)
            node_risk = failure_prob * load_loss
            total_risk += node_risk
        return total_risk

    # ==================== 过载风险计算 ====================

    def I_ij(self, begin: int, end: int) -> float:
        """
        计算指定线路的电流值

        Args:
            begin: 起始节点编号
            end: 终止节点编号

        Returns:
            线路电流值 (A)
        """
        try:
            edge_powers = self.calculate_power_flow_simple()
            edge_key = self._get_edge_key(begin, end)
            line_power = edge_powers.get(edge_key, 0.0)
            if line_power <= 0:
                return 0.0
            voltage_kv = self.voltage / 1000
            current = line_power / (np.sqrt(3) * voltage_kv * self.cos)
            return current
        except Exception as e:
            logger.error(f"计算线路 ({begin}, {end}) 电流时出错: {e}")
            return 0.0

    def P_ol_all(self) -> float:
        """
        计算全网过载线路比例

        Returns:
            过载线路比例 (0-1 之间)
        """
        total_lines = 0
        overloaded_lines = 0
        threshold = 1.1 * self.feeder_current_limit
        for edge in self._edges_info:
            begin, end = list(edge.keys())[0]
            try:
                current = self.I_ij(begin, end)
                if current > threshold:
                    overloaded_lines += 1
                total_lines += 1
            except Exception as e:
                logger.error(f"检查线路 ({begin}, {end}) 过载状态时出错: {e}")
                continue
        return overloaded_lines / total_lines if total_lines > 0 else 0.0

    def C_ol(self) -> float:
        """
        计算过载线路危害度，考虑分布式能源的减载效果

        Returns:
            过载危害度
        """
        total_consequence = 0.0
        threshold = 1.1 * self.feeder_current_limit
        for edge in self._edges_info:
            begin, end = list(edge.keys())[0]
            try:
                current = self.I_ij(begin, end)
                if current > threshold:
                    begin_type = self._graph.get_node_attribute(str(begin), 'type') or '居民'
                    end_type = self._graph.get_node_attribute(str(end), 'type') or '居民'
                    begin_weight = self._damage_weights.get(begin_type, 1.0)
                    end_weight = self._damage_weights.get(end_type, 1.0)
                    avg_weight = (begin_weight + end_weight) / 2
                    begin_is_dg = self._graph.get_node_attribute(str(begin), 'DG')
                    end_is_dg = self._graph.get_node_attribute(str(end), 'DG')
                    dg_factor = 0.8 if (begin_is_dg or end_is_dg) else 1.0
                    overload_severity = (current - threshold) * dg_factor
                    consequence = avg_weight * overload_severity
                    total_consequence += consequence
            except Exception as e:
                logger.error(f"计算线路 ({begin}, {end}) 过载危害度时出错: {e}")
                continue
        return total_consequence

    # ==================== 综合分析方法 ====================

    def comprehensive_risk_analysis(self) -> Dict[str, float]:
        """
        综合风险分析

        Returns:
            包含各种风险指标的字典
        """
        try:
            results = {
                'failure_probability': self.P_f(),
                'load_loss_consequence': self.C_ll(),
                'load_loss_risk': self.load_loss_risk(),
                'overload_probability': self.P_ol_all(),
                'overload_consequence': self.C_ol(),
            }
            results['total_risk'] = (results['load_loss_risk'] * results['load_loss_consequence'] +
                                     results['overload_probability'] * results['overload_consequence'])
            return results
        except Exception as e:
            logger.error(f"综合风险分析时出错: {e}")
            return {}

    def get_critical_lines(self, top_n: int = 5) -> List[Tuple[Tuple[int, int], float]]:
        """
        获取最关键的线路（基于电流负载）

        Args:
            top_n: 返回前 N 条关键线路

        Returns:
            [(边, 电流值), ...] 按电流从大到小排序
        """
        line_currents = []
        for edge in self._edges_info:
            begin, end = list(edge.keys())[0]
            try:
                current = self.I_ij(begin, end)
                line_currents.append(((begin, end), current))
            except Exception as e:
                logger.error(f"获取线路 ({begin}, {end}) 电流时出错: {e}")
                continue
        line_currents.sort(key=lambda x: x[1], reverse=True)
        return line_currents[:top_n]

    # ==================== 调试和测试方法 ====================

    def print_analysis_summary(self):
        """打印分析结果摘要"""
        print("=" * 50)
        print("电网风险分析结果摘要")
        print("=" * 50)
        try:
            results = self.comprehensive_risk_analysis()
            print(f"全网故障概率: {results.get('failure_probability', 0):.6f}")
            print(f"失负荷危害度: {results.get('load_loss_consequence', 0):.2f} kW")
            print(f"失负荷风险: {results.get('load_loss_risk', 0):.6f}")
            print(f"过载线路比例: {results.get('overload_probability', 0):.2%}")
            print(f"过载危害度: {results.get('overload_consequence', 0):.2f}")
            print(f"综合风险指标: {results.get('total_risk', 0):.6f}")
            print("\n线路:")
            critical_lines = self.get_critical_lines(62)
            for i, (edge, current) in enumerate(critical_lines, 1):
                if current == 0:
                    status = "失负荷"
                elif current > 1.1 * self.feeder_current_limit:
                    status = "过载"
                else:
                    status = "正常"
                print(f"{i}. 线路 {edge}: {current:.2f}A ({status})")
        except Exception as e:
            logger.error(f"打印分析摘要时出错: {e}")

def main():
    """主函数 - 演示分析器的使用"""
    try:
        analyzer = RiskAnalyzer(nodes_info=nodes_info, edges_info=edges_info)
        print("开始电网风险分析...")
        begin = 1
        end = 2
        edge_risk = analyzer.edge_risk(begin, end)
        capacity = analyzer.calculate_capacity(begin, end)
        current = analyzer.I_ij(begin, end)
        print(f"线路 {begin}->{end}:\nedge_risk\t{edge_risk}\ncapacity:\t{capacity}\ncurrent:\t{current}")
        analyzer.print_analysis_summary()
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, level="WARNING")
    main()