import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter
import networkx as nx
from loguru import logger
from typing import Union, Optional

class UndirectedGraph:
    """
    无向图类：用于管理节点属性和边信息，提供图分析功能，适用于数学建模
    """
    def __init__(self, node_info, graph_edges):
        """
        初始化无向图
        
        参数:
            node_info: 字典，键为节点ID，值为节点属性字典
            graph_edges: 列表，包含边信息字典，格式为[{(from_node,to_node):{边信息}}]
        """
        logger.info("初始化UndirectedGraph，节点数: {}, 边数: {}".format(len(node_info), len(graph_edges)))
        self.node_info = node_info
        self.graph_edges = graph_edges
        # 构建邻接表，用于路径查找和连通性检查
        self.adjacency_list = self._build_adjacency_list()
        
    def _build_adjacency_list(self):
        """构建邻接表，用于快速查找相邻节点"""
        logger.info("构建邻接表")
        adjacency_list = {}
        
        # 初始化所有节点的邻接列表为空列表
        for node_id in self.node_info:
            adjacency_list[node_id] = []
        
        # 遍历所有边，添加到邻接表
        for edge_dict in self.graph_edges:
            for (node1, node2) in edge_dict:
                if node1 not in adjacency_list:
                    adjacency_list[node1] = []
                if node2 not in adjacency_list:
                    adjacency_list[node2] = []
                    
                adjacency_list[node1].append(node2)
                adjacency_list[node2].append(node1)  # 因为是无向图，所以两个方向都添加
                
        logger.info("邻接表构建完成")
        return adjacency_list
    
    def neighbors(self, node_id: int) -> list[int]:
        """
        获取指定节点的所有邻居节点
        
        参数:
            node_id: 节点ID
            
        返回:
            邻居节点ID列表
        """
        if node_id not in self.adjacency_list:
            logger.error(f"节点 {node_id} 不存在")
            print(f"节点 {node_id} 不存在")
            return []
        
        logger.info(f"获取节点 {node_id} 的邻居: {self.adjacency_list[node_id]}")
        return self.adjacency_list[node_id]
    
    def get_node_attribute(self, node_id, attribute=None):
        """
        获取节点的属性
        
        参数:
            node_id: 节点ID
            attribute: 要查询的属性名，若为None则返回该节点的所有属性
            
        返回:
            如果attribute为None，返回节点的所有属性字典；否则返回指定的属性值
            如果节点不存在或属性不存在，返回None
        """
        if node_id not in self.node_info:
            logger.error(f"节点 {node_id} 不存在")
            print(f"节点 {node_id} 不存在")
            return None
            
        if attribute is None:
            logger.info(f"获取节点 {node_id} 的所有属性: {self.node_info[node_id]}")
            return self.node_info[node_id]
        elif attribute in self.node_info[node_id]:
            logger.info(f"获取节点 {node_id} 的属性 '{attribute}': {self.node_info[node_id][attribute]}")
            return self.node_info[node_id][attribute]
        else:
            logger.error(f"节点 {node_id} 没有属性 '{attribute}'")
            print(f"节点 {node_id} 没有属性 '{attribute}'")
            return None
    
    def get_edge(self, node1:int, node2:int) -> dict:
        """
        查找两个节点之间的边
        
        参数:
            node1, node2: 两个节点的ID
            
        返回:
            边信息字典，如果边不存在则返回空字典
        """
        # 确保node1 <= node2，因为我们的存储规则是较小节点ID在前
        if node1 > node2:
            node1, node2 = node2, node1
            
        # 查询边信息
        for edge_dict in self.graph_edges:
            if (node1, node2) in edge_dict:
                logger.info(f"获取边 ({node1}, {node2}) 信息: {edge_dict[(node1, node2)]}")
                return edge_dict[(node1, node2)]
                
        logger.error(f"边 ({node1}, {node2}) 不存在")
        return {}
    
    def get_edge_attribute(self, node1:int, node2:int, attribute=None) -> Optional[Union[int, float, str, dict]]:
        """
        获取边的属性
        
        参数:
            node1, node2: 两个节点的ID
            attribute: 要查询的属性名，若为None则返回该边的所有属性
            
        返回:
            如果attribute为None，返回边的所有属性字典；否则返回指定的属性值
            如果边不存在或属性不存在，返回None
        """
        edge_info = self.get_edge(node1, node2)
        
        if not edge_info:
            logger.error(f"节点 {node1} 和节点 {node2} 之间没有边")
            return None
            
        if attribute is None:
            logger.info(f"获取边 ({node1}, {node2}) 的所有属性: {edge_info}")
            return edge_info
        elif attribute in edge_info:
            logger.info(f"获取边 ({node1}, {node2}) 的属性 '{attribute}': {edge_info[attribute]}")
            return edge_info[attribute]
        else:
            logger.error(f"边 ({node1}, {node2}) 没有属性 '{attribute}'")
            return None
    
    def has_edge(self, node1, node2):
        """
        检查两个节点之间是否有边
        
        参数:
            node1, node2: 两个节点的ID
            
        返回:
            布尔值，表示是否存在边
        """
        result = self.get_edge(node1, node2) != {}
        logger.info(f"检查边 ({node1}, {node2}) 是否存在: {result}")
        return result
    
    def find_path(self, start_node, end_node):
        """
        查找两个节点之间的路径（使用广度优先搜索）
        
        参数:
            start_node: 起始节点ID
            end_node: 目标节点ID
            
        返回:
            如果存在路径，返回节点ID列表；否则返回None
        """
        if start_node not in self.adjacency_list or end_node not in self.adjacency_list:
            logger.error(f"节点 {start_node} 或节点 {end_node} 不存在")
            return None
            
        if start_node == end_node:
            logger.info(f"起点和终点相同: {start_node}")
            return [start_node]
            
        # 广度优先搜索
        visited = set()
        queue = [(start_node, [start_node])]  # (当前节点, 路径)
        
        while queue:
            current, path = queue.pop(0)
            
            if current == end_node:
                logger.info(f"找到路径: {path}")
                return path
                
            if current in visited:
                continue
                
            visited.add(current)
            
            for neighbor in self.adjacency_list[current]:
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
                    
        logger.error(f"节点 {start_node} 和节点 {end_node} 之间不连通")
        return None
    
    def is_connected(self, node1, node2):
        """
        检查两个节点是否连通，并打印路径
        
        参数:
            node1, node2: 两个节点的ID
            
        返回:
            布尔值，表示两个节点是否连通
        """
        path = self.find_path(node1, node2)
        
        if path:
            logger.info(f"节点 {node1} 和节点 {node2} 连通，路径: {path}")
            print(f"节点 {node1} 和节点 {node2} 连通")
            print(f"路径: {' -> '.join(map(str, path))}")
            return True
        else:
            logger.info(f"节点 {node1} 和节点 {node2} 不连通")
            print(f"节点 {node1} 和节点 {node2} 不连通")
            return False
    
    def print_graph(self):
        """打印整个图的结构：节点属性和边信息"""
        logger.info("打印整个图的结构")
        print("=" * 20 + " 节点信息 " + "=" * 20)
        for node_id, info in self.node_info.items():
            print(f"节点 {node_id}: {info}")
            
        print("\n" + "=" * 20 + " 边信息 " + "=" * 20)
        for edge_dict in self.graph_edges:
            for edge, info in edge_dict.items():
                print(f"边 {edge}: {info}")
    
    def print_node_neighbors(self, node_id):
        """
        打印指定节点的所有邻居
        
        参数:
            node_id: 节点ID
        """
        if node_id not in self.adjacency_list:
            logger.error(f"节点 {node_id} 不存在")
            print(f"节点 {node_id} 不存在")
            return
            
        neighbors = self.adjacency_list[node_id]
        if not neighbors:
            logger.info(f"节点 {node_id} 没有邻居")
            print(f"节点 {node_id} 没有邻居")
        else:
            logger.info(f"节点 {node_id} 的邻居: {neighbors}")
            print(f"节点 {node_id} 的邻居: {', '.join(map(str, neighbors))}")
    
    def find_nodes_by_attribute(self, attribute, value):
        """
        查找具有特定属性值的所有节点
        
        参数:
            attribute: 属性名
            value: 属性值
            
        返回:
            节点ID列表
        """
        matching_nodes = []
        
        for node_id, info in self.node_info.items():
            if attribute in info and info[attribute] == value:
                matching_nodes.append(node_id)
                
        logger.info(f"查找属性 {attribute}={value} 的节点: {matching_nodes}")
        return matching_nodes
    
    def find_edges_by_attribute(self, attribute: str, value):
        """
        查找具有特定属性值的所有边
        
        参数:
            attribute: 属性名
            value: 属性值
            
        返回:
            边元组列表 [(node1, node2), ...]
        """
        matching_edges = []
        
        for edge_dict in self.graph_edges:
            for edge, info in edge_dict.items():
                if attribute in info and info[attribute] == value:
                    matching_edges.append(edge)
                    
        logger.info(f"查找属性 {attribute}={value} 的边: {matching_edges}")
        return matching_edges
    
    def get_all_paths(self, start_node, end_node, max_depth=10):
        """
        找出两个节点之间的所有路径（深度优先搜索，限制深度）
        
        参数:
            start_node: 起始节点ID
            end_node: 目标节点ID
            max_depth: 最大搜索深度，防止路径过长
            
        返回:
            路径列表，每个路径是节点ID的列表
        """
        if start_node not in self.adjacency_list or end_node not in self.adjacency_list:
            logger.error(f"节点 {start_node} 或节点 {end_node} 不存在")
            print(f"节点 {start_node} 或节点 {end_node} 不存在")
            return []
            
        paths = []
        
        def dfs(current, path, depth):
            if depth > max_depth:
                return
                
            if current == end_node:
                paths.append(path[:])
                return
                
            for neighbor in self.adjacency_list[current]:
                if neighbor not in path:  # 避免环路
                    path.append(neighbor)
                    dfs(neighbor, path, depth + 1)
                    path.pop()  # 回溯
        
        dfs(start_node, [start_node], 0)
        logger.info(f"所有路径从 {start_node} 到 {end_node}: {paths}")
        return paths
    
    # =============== 新增功能 ===============
    
    def add_node(self, node_id, attributes=None):
        """
        添加新节点
        
        参数:
            node_id: 节点ID
            attributes: 节点属性字典
        
        返回:
            布尔值，表示是否成功添加
        """
        if node_id in self.node_info:
            logger.error(f"节点 {node_id} 已存在")
            print(f"节点 {node_id} 已存在")
            return False
        
        self.node_info[node_id] = attributes or {}
        self.adjacency_list[node_id] = []
        logger.info(f"添加节点 {node_id}，属性: {attributes}")
        return True
    
    def add_nodes(self, nodes_dict):
        """
        批量添加节点
        
        参数:
            nodes_dict: 字典，键为节点ID，值为节点属性字典
        
        返回:
            成功添加的节点数量
        """
        count = 0
        for node_id, attributes in nodes_dict.items():
            if self.add_node(node_id, attributes):
                count += 1
        
        logger.info(f"批量添加节点，成功数量: {count}")
        print(f"成功添加 {count} 个节点")
        return count
    
    def add_edge(self, node1, node2, attributes=None):
        """
        添加边
        
        参数:
            node1, node2: 两个节点的ID
            attributes: 边的属性字典
        
        返回:
            布尔值，表示是否成功添加
        """
        # 确保两个节点都存在
        if node1 not in self.node_info:
            logger.error(f"节点 {node1} 不存在")
            print(f"节点 {node1} 不存在")
            return False
        if node2 not in self.node_info:
            logger.error(f"节点 {node2} 不存在")
            print(f"节点 {node2} 不存在")
            return False
        
        # 确保边不存在
        if self.has_edge(node1, node2):
            logger.error(f"边 ({node1}, {node2}) 已存在")
            print(f"边 ({node1}, {node2}) 已存在")
            return False
        
        # 确保node1 <= node2
        if node1 > node2:
            node1, node2 = node2, node1
        
        # 添加边信息
        edge_dict = {(node1, node2): attributes or {}}
        self.graph_edges.append(edge_dict)
        
        # 更新邻接表
        self.adjacency_list[node1].append(node2)
        self.adjacency_list[node2].append(node1)
        
        logger.info(f"添加边 ({node1}, {node2})，属性: {attributes}")
        return True
    
    def add_edges(self, edges_list):
        """
        批量添加边
        
        参数:
            edges_list: 列表，元素为 (node1, node2, attributes) 三元组，attributes可选
        
        返回:
            成功添加的边数量
        """
        count = 0
        for edge in edges_list:
            if len(edge) == 2:
                node1, node2 = edge
                attributes = {}
            else:
                node1, node2, attributes = edge
            
            if self.add_edge(node1, node2, attributes):
                count += 1
        
        logger.info(f"批量添加边，成功数量: {count}")
        print(f"成功添加 {count} 条边")
        return count
    
    def remove_node(self, node_id):
        """
        删除节点及其相关的所有边
        
        参数:
            node_id: 要删除的节点ID
        
        返回:
            布尔值，表示是否成功删除
        """
        if node_id not in self.node_info:
            logger.error(f"节点 {node_id} 不存在")
            print(f"节点 {node_id} 不存在")
            return False
        
        # 删除与该节点相关的所有边
        edges_to_remove = []
        for edge_dict in self.graph_edges:
            for (n1, n2) in edge_dict.keys():
                if n1 == node_id or n2 == node_id:
                    edges_to_remove.append(edge_dict)
        
        for edge_dict in edges_to_remove:
            self.graph_edges.remove(edge_dict)
        
        # 从所有邻居的邻接表中删除该节点
        for neighbor in self.adjacency_list[node_id]:
            self.adjacency_list[neighbor].remove(node_id)
        
        # 删除节点信息和邻接表条目
        del self.node_info[node_id]
        del self.adjacency_list[node_id]
        
        logger.info(f"删除节点 {node_id} 及其相关边")
        return True
    
    def remove_nodes(self, node_ids):
        """
        批量删除节点
        
        参数:
            node_ids: 要删除的节点ID列表
        
        返回:
            成功删除的节点数量
        """
        count = 0
        for node_id in node_ids:
            if self.remove_node(node_id):
                count += 1
        
        logger.info(f"批量删除节点，成功数量: {count}")
        print(f"成功删除 {count} 个节点")
        return count
    
    def remove_edge(self, node1, node2):
        """
        删除边
        
        参数:
            node1, node2: 两个节点的ID
        
        返回:
            布尔值，表示是否成功删除
        """
        # 确保node1 <= node2
        if node1 > node2:
            node1, node2 = node2, node1
        
        # 查找并删除边信息
        edge_dict_to_remove = None
        for edge_dict in self.graph_edges:
            if (node1, node2) in edge_dict:
                edge_dict_to_remove = edge_dict
                break
        
        if edge_dict_to_remove is None:
            logger.error(f"边 ({node1}, {node2}) 不存在")
            print(f"边 ({node1}, {node2}) 不存在")
            return False
        
        self.graph_edges.remove(edge_dict_to_remove)
        
        # 更新邻接表
        self.adjacency_list[node1].remove(node2)
        self.adjacency_list[node2].remove(node1)
        
        logger.info(f"删除边 ({node1}, {node2})")
        return True
    
    def remove_edges(self, edges_list):
        """
        批量删除边
        
        参数:
            edges_list: 列表，元素为 (node1, node2) 元组
        
        返回:
            成功删除的边数量
        """
        count = 0
        for node1, node2 in edges_list:
            if self.remove_edge(node1, node2):
                count += 1
        
        logger.info(f"批量删除边，成功数量: {count}")
        print(f"成功删除 {count} 条边")
        return count
    
    def update_node_attribute(self, node_id, attribute, value):
        """
        更新节点属性
        
        参数:
            node_id: 节点ID
            attribute: 属性名
            value: 新的属性值
        
        返回:
            布尔值，表示是否成功更新
        """
        if node_id not in self.node_info:
            logger.error(f"节点 {node_id} 不存在")
            print(f"节点 {node_id} 不存在")
            return False
        
        self.node_info[node_id][attribute] = value
        logger.info(f"更新节点 {node_id} 的属性 {attribute}={value}")
        return True
    
    def update_node_attributes(self, node_id, attributes):
        """
        批量更新节点属性
        
        参数:
            node_id: 节点ID
            attributes: 属性字典
        
        返回:
            布尔值，表示是否成功更新
        """
        if node_id not in self.node_info:
            logger.error(f"节点 {node_id} 不存在")
            print(f"节点 {node_id} 不存在")
            return False
        
        self.node_info[node_id].update(attributes)
        logger.info(f"批量更新节点 {node_id} 的属性: {attributes}")
        return True
    
    def batch_update_node_attributes(self, updates):
        """
        批量更新多个节点的属性
        
        参数:
            updates: 字典，键为节点ID，值为属性更新字典
        
        返回:
            成功更新的节点数量
        """
        count = 0
        for node_id, attributes in updates.items():
            if self.update_node_attributes(node_id, attributes):
                count += 1
        
        logger.info(f"批量更新多个节点属性，成功数量: {count}")
        print(f"成功更新 {count} 个节点的属性")
        return count
    
    def update_edge_attribute(self, node1, node2, attribute, value):
        """
        更新边属性
        
        参数:
            node1, node2: 两个节点的ID
            attribute: 属性名
            value: 新的属性值
        
        返回:
            布尔值，表示是否成功更新
        """
        # 确保node1 <= node2
        if node1 > node2:
            node1, node2 = node2, node1
        
        # 查找边信息
        for edge_dict in self.graph_edges:
            if (node1, node2) in edge_dict:
                edge_dict[(node1, node2)][attribute] = value
                logger.info(f"更新边 ({node1}, {node2}) 的属性 {attribute}={value}")
                return True
        
        logger.error(f"边 ({node1}, {node2}) 不存在")
        print(f"边 ({node1}, {node2}) 不存在")
        return False
    
    def update_edge_attributes(self, node1, node2, attributes):
        """
        批量更新边属性
        
        参数:
            node1, node2: 两个节点的ID
            attributes: 属性字典
        
        返回:
            布尔值，表示是否成功更新
        """
        # 确保node1 <= node2
        if node1 > node2:
            node1, node2 = node2, node1
        
        # 查找边信息
        for edge_dict in self.graph_edges:
            if (node1, node2) in edge_dict:
                edge_dict[(node1, node2)].update(attributes)
                logger.info(f"批量更新边 ({node1}, {node2}) 的属性: {attributes}")
                return True
        
        logger.error(f"边 ({node1}, {node2}) 不存在")
        print(f"边 ({node1}, {node2}) 不存在")
        return False
    
    def batch_update_edge_attributes(self, updates):
        """
        批量更新多条边的属性
        
        参数:
            updates: 列表，元素为 (node1, node2, attributes) 三元组
        
        返回:
            成功更新的边数量
        """
        count = 0
        for update in updates:
            node1, node2, attributes = update
            if self.update_edge_attributes(node1, node2, attributes):
                count += 1
        
        logger.info(f"批量更新多条边属性，成功数量: {count}")
        print(f"成功更新 {count} 条边的属性")
        return count
    
    def get_node_degree(self, node_id):
        """
        获取节点的度
        
        参数:
            node_id: 节点ID
        
        返回:
            度数（整数）
        """
        if node_id not in self.adjacency_list:
            logger.error(f"节点 {node_id} 不存在")
            print(f"节点 {node_id} 不存在")
            return 0
        else:
            logger.info(f"节点 {node_id} 的度: {len(self.adjacency_list[node_id])}")
            print(f"节点 {node_id} 的度: {len(self.adjacency_list[node_id])}")
        
        return len(self.adjacency_list[node_id])
    
    def get_all_degrees(self):
        """
        获取所有节点的度
        
        返回:
            字典，键为节点ID，值为度数
        """
        logger.info("获取所有节点的度")
        return {node: len(neighbors) for node, neighbors in self.adjacency_list.items()}
    
    def get_average_degree(self):
        """
        计算图的平均度
        
        返回:
            平均度（浮点数）
        """
        if not self.node_info:
            logger.error("节点信息为空，无法计算平均度")
            return 0
        
        degrees = self.get_all_degrees()
        avg = sum(degrees.values()) / len(degrees)
        logger.info(f"平均度: {avg}")
        return avg
    
    def get_node_attribute_statistics(self, attribute):
        """
        统计节点特定属性的分布情况
        
        参数:
            attribute: 属性名
        
        返回:
            Counter对象，计数每个属性值的出现次数
        """
        values = []
        for node_id, info in self.node_info.items():
            if attribute in info:
                values.append(info[attribute])
        
        logger.info(f"节点属性 {attribute} 的统计: {Counter(values)}")
        return Counter(values)
    
    def get_edge_attribute_statistics(self, attribute):
        """
        统计边特定属性的分布情况
        
        参数:
            attribute: 属性名
        
        返回:
            Counter对象，计数每个属性值的出现次数
        """
        values = []
        for edge_dict in self.graph_edges:
            for edge, info in edge_dict.items():
                if attribute in info:
                    values.append(info[attribute])
        
        logger.info(f"边属性 {attribute} 的统计: {Counter(values)}")
        return Counter(values)
    
    def get_attribute_summary(self, attribute_type="node", attribute=None):
        """
        获取属性的统计摘要
        
        参数:
            attribute_type: "node" 或 "edge"，表示节点属性或边属性
            attribute: 属性名，若为None则返回所有属性的统计
        
        返回:
            DataFrame，包含属性统计信息
        """
        if attribute_type == "node":
            items = self.node_info.items()
        else:
            items = [(edge, info) for edge_dict in self.graph_edges for edge, info in edge_dict.items()]
        
        # 收集所有属性名（如果attribute为None）
        if attribute is None:
            attributes = set()
            for _, info in items:
                attributes.update(info.keys())
            attributes = list(attributes)
        else:
            attributes = [attribute]
        
        # 收集数据
        stats = []
        for attr in attributes:
            values = []
            for _, info in items:
                if attr in info:
                    value = info[attr]
                    if isinstance(value, (int, float)):
                        values.append(value)
            
            if values:
                stat = {
                    'attribute': attr,
                    'count': len(values),
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    '25%': np.percentile(values, 25),
                    'median': np.median(values),
                    '75%': np.percentile(values, 75),
                    'max': np.max(values)
                }
                stats.append(stat)
        
        df = pd.DataFrame(stats) if stats else pd.DataFrame()
        logger.info(f"属性统计摘要: \n{df}")
        return df
    
    def to_networkx(self):
        """
        转换为NetworkX图对象（用于高级分析和可视化）
        
        返回:
            NetworkX Graph对象
        """
        G = nx.Graph()
        
        # 添加节点和属性
        for node_id, attrs in self.node_info.items():
            G.add_node(node_id, **attrs)
        
        # 添加边和属性
        for edge_dict in self.graph_edges:
            for (node1, node2), attrs in edge_dict.items():
                G.add_edge(node1, node2, **attrs)
        
        logger.info("转换为NetworkX图对象")
        return G
    
    def visualize(self, figsize=(10, 8), node_size=300, node_color="skyblue", 
                  edge_color="gray", font_size=10, with_labels=True, 
                  node_attribute=None, edge_attribute=None, title=None):
        """
        可视化图结构
        
        参数:
            figsize: 图像大小元组 (宽, 高)
            node_size: 节点大小
            node_color: 节点颜色（如果node_attribute不为None，则根据属性映射颜色）
            edge_color: 边颜色（如果edge_attribute不为None，则根据属性映射颜色）
            font_size: 标签字体大小
            with_labels: 是否显示节点标签
            node_attribute: 用于节点颜色映射的属性名
            edge_attribute: 用于边颜色映射的属性名
            title: 图表标题
        """
        logger.info("可视化图结构")
        G = self.to_networkx()
        
        # 设置Seaborn风格
        sns.set_style("whitegrid")
        
        plt.figure(figsize=figsize)
        pos = nx.spring_layout(G, seed=42)  # 位置布局
        
        # 节点颜色映射
        if node_attribute:
            node_colors = []
            for node in G.nodes():
                attr_value = self.get_node_attribute(node, node_attribute)
                if attr_value is not None:
                    if isinstance(attr_value, (int, float)):
                        node_colors.append(attr_value)
                    else:
                        # 对非数值属性进行哈希处理
                        node_colors.append(hash(str(attr_value)) % 1000)
                else:
                    node_colors.append(0)
            
            # 绘制节点
            nodes = nx.draw_networkx_nodes(G, pos, node_size=node_size, 
                                         node_color=node_colors, cmap=plt.cm.viridis)
            plt.colorbar(nodes, label=f'节点属性: {node_attribute}')
        else:
            # 使用单一颜色
            nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color=node_color)
        
        # 边颜色映射
        if edge_attribute:
            edge_colors = []
            for u, v in G.edges():
                # 确保u <= v
                if u > v:
                    u, v = v, u
                attr_value = self.get_edge_attribute(u, v, edge_attribute)
                if attr_value is not None:
                    if isinstance(attr_value, (int, float)):
                        edge_colors.append(attr_value)
                    else:
                        # 对非数值属性进行哈希处理
                        edge_colors.append(hash(str(attr_value)) % 1000)
                else:
                    edge_colors.append(0)
            
            # 绘制边
            edges = nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=1.5, 
                                         edge_cmap=plt.cm.cool)
            plt.colorbar(edges, label=f'边属性: {edge_attribute}')
        else:
            # 使用单一颜色
            nx.draw_networkx_edges(G, pos, edge_color=edge_color, width=1.5)
        
        # 绘制标签
        if with_labels:
            nx.draw_networkx_labels(G, pos, font_size=font_size, font_family="sans-serif")
        
        # 设置标题
        if title:
            plt.title(title, fontsize=15)
        
        plt.axis("off")
        plt.tight_layout()
        plt.show()
    
    def visualize_degree_distribution(self, figsize=(10, 6), bins=10):
        """
        可视化节点度分布
        
        参数:
            figsize: 图像大小元组 (宽, 高)
            bins: 直方图的柱数
        """
        logger.info("可视化节点度分布")
        degrees = list(self.get_all_degrees().values())
        
        plt.figure(figsize=figsize)
        sns.histplot(degrees, bins=bins, kde=True)
        plt.title("节点度分布", fontsize=15)
        plt.xlabel("度")
        plt.ylabel("频数")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
        
        # 打印统计信息
        print(f"平均度: {np.mean(degrees):.2f}")
        print(f"中位数度: {np.median(degrees):.2f}")
        print(f"最大度: {np.max(degrees)}")
        print(f"最小度: {np.min(degrees)}")
        print(f"度标准差: {np.std(degrees):.2f}")
    
    def visualize_attribute_distribution(self, attribute, attribute_type="node", figsize=(10, 6), 
                                         plot_type="hist", top_n=None):
        """
        可视化属性值分布
        
        参数:
            attribute: 属性名
            attribute_type: "node" 或 "edge"，表示节点属性或边属性
            figsize: 图像大小元组 (宽, 高)
            plot_type: "hist"（直方图）或 "bar"（条形图）
            top_n: 对于条形图，只显示前N个最常见的值
        """
        logger.info(f"可视化属性 {attribute_type} '{attribute}' 分布")
        if attribute_type == "node":
            values = []
            for _, info in self.node_info.items():
                if attribute in info:
                    values.append(info[attribute])
            title_prefix = "节点属性"
        else:
            values = []
            for edge_dict in self.graph_edges:
                for _, info in edge_dict.items():
                    if attribute in info:
                        values.append(info[attribute])
            title_prefix = "边属性"
        
        if not values:
            logger.error(f"没有找到 {attribute_type} 的 '{attribute}' 属性数据")
            print(f"没有找到 {attribute_type} 的 '{attribute}' 属性数据")
            return
        
        plt.figure(figsize=figsize)
        
        if plot_type == "hist" and all(isinstance(x, (int, float)) for x in values):
            # 数值型数据用直方图
            sns.histplot(values, kde=True)
            plt.title(f"{title_prefix} '{attribute}' 分布", fontsize=15)
            plt.xlabel(attribute)
            plt.ylabel("频数")
        else:
            # 分类数据用条形图
            counter = Counter(values)
            if top_n:
                most_common = counter.most_common(top_n)
                keys = [x[0] for x in most_common]
                counts = [x[1] for x in most_common]
            else:
                keys = list(counter.keys())
                counts = list(counter.values())
            
            plt.bar(range(len(keys)), counts, color=sns.color_palette("viridis", len(keys)))
            plt.xticks(range(len(keys)), keys, rotation=45 if len(str(keys[0])) > 10 else 0)
            plt.title(f"{title_prefix} '{attribute}' 分布 TOP {len(keys)}", fontsize=15)
            plt.xlabel(attribute)
            plt.ylabel("频数")
        
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
    
    def visualize_graph_metrics(self, figsize=(15, 10)):
        """
        可视化图的各种度量指标
        
        参数:
            figsize: 图像大小元组 (宽, 高)
        """
        logger.info("可视化图的各种度量指标")
        G = self.to_networkx()
        metrics = {}
        
        # 计算各种中心性指标
        try:
            metrics['度中心性'] = nx.degree_centrality(G)
            metrics['介数中心性'] = nx.betweenness_centrality(G)
            metrics['接近中心性'] = nx.closeness_centrality(G)
            metrics['特征向量中心性'] = nx.eigenvector_centrality(G, max_iter=1000)
            
            # 准备绘图数据
            df = pd.DataFrame(metrics)
            
            # 绘制中心性指标对比图
            plt.figure(figsize=figsize)
            
            # 创建2x2子图
            fig, axes = plt.subplots(2, 2, figsize=figsize)
            
            # 度中心性分布
            sns.histplot(df['度中心性'], kde=True, ax=axes[0, 0])
            axes[0, 0].set_title('度中心性分布')
            axes[0, 0].grid(True, linestyle='--', alpha=0.7)
            
            # 介数中心性分布
            sns.histplot(df['介数中心性'], kde=True, ax=axes[0, 1])
            axes[0, 1].set_title('介数中心性分布')
            axes[0, 1].grid(True, linestyle='--', alpha=0.7)
            
            # 接近中心性分布
            sns.histplot(df['接近中心性'], kde=True, ax=axes[1, 0])
            axes[1, 0].set_title('接近中心性分布')
            axes[1, 0].grid(True, linestyle='--', alpha=0.7)
            
            # 特征向量中心性分布
            sns.histplot(df['特征向量中心性'], kde=True, ax=axes[1, 1])
            axes[1, 1].set_title('特征向量中心性分布')
            axes[1, 1].grid(True, linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            plt.show()
            
            # 打印重要节点信息
            print("每种中心性指标的TOP 5节点:")
            for metric_name in metrics:
                sorted_nodes = sorted(metrics[metric_name].items(), key=lambda x: x[1], reverse=True)[:5]
                print(f"\n{metric_name} TOP 5:")
                for i, (node, value) in enumerate(sorted_nodes, 1):
                    print(f"  {i}. 节点 {node}: {value:.4f}")
                    
        except nx.NetworkXError as e:
            logger.error(f"无法计算部分中心性指标: {e}")
            print(f"无法计算部分中心性指标: {e}")
    
    def visualize_communities(self, algorithm="louvain", figsize=(12, 10), with_labels=True):
        """
        社区检测并可视化
        
        参数:
            algorithm: 社区检测算法名称，"louvain"、"girvan_newman"或"label_propagation"
            figsize: 图像大小元组 (宽, 高)
            with_labels: 是否显示节点标签
        """
        logger.info(f"社区检测并可视化，算法: {algorithm}")
        G = self.to_networkx()
        communities = {}
        
        try:
            if algorithm == "louvain":
                import community as community_louvain
                partition = community_louvain.best_partition(G)
                communities = {}
                for node, comm_id in partition.items():
                    if comm_id not in communities:
                        communities[comm_id] = []
                    communities[comm_id].append(node)
                
            elif algorithm == "girvan_newman":
                comp = nx.community.girvan_newman(G)
                # 只取第一个分解级别
                communities_set = tuple(sorted(c) for c in next(comp))
                communities = {i: list(comm) for i, comm in enumerate(communities_set)}
                
            elif algorithm == "label_propagation":
                communities_set = nx.community.label_propagation_communities(G)
                communities = {i: list(comm) for i, comm in enumerate(communities_set)}
            
            # 可视化社区结构
            plt.figure(figsize=figsize)
            pos = nx.spring_layout(G, seed=42)
            
            # 为不同社区选择不同颜色
            cmap = plt.cm.get_cmap("viridis", len(communities))
            
            for i, comm in communities.items():
                nx.draw_networkx_nodes(G, pos, nodelist=comm, 
                                     node_color=[cmap(i)] * len(comm), 
                                     node_size=300, alpha=0.8)
            
            nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
            
            if with_labels:
                nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
            
            plt.title(f"社区检测结果 ({algorithm})", fontsize=15)
            plt.axis("off")
            
            # 添加图例
            handles = [plt.Rectangle((0,0), 1, 1, color=cmap(i)) for i in range(len(communities))]
            labels = [f"社区 {i+1} (节点数: {len(comm)})" for i, comm in communities.items()]
            plt.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                     ncol=min(5, len(communities)))
            
            plt.tight_layout()
            plt.show()
            
            # 打印社区信息
            print(f"共检测到 {len(communities)} 个社区:")
            for i, comm in communities.items():
                print(f"社区 {i+1}: {len(comm)} 个节点")
            
        except ImportError:
            logger.error(f"无法使用所选社区检测算法，请安装相应的包")
            print(f"无法使用所选社区检测算法，请安装相应的包")
            if algorithm == "louvain":
                print("使用Louvain算法需要安装python-louvain包: pip install python-louvain")
        except Exception as e:
            logger.error(f"社区检测过程中出错: {e}")
            print(f"社区检测过程中出错: {e}")
    
    def plot_shortest_paths(self, start_node, end_nodes=None, figsize=(12, 10)):
        """
        可视化从起始节点到一个或多个目标节点的最短路径
        
        参数:
            start_node: 起始节点ID
            end_nodes: 目标节点ID列表，若为None则选择距离最远的几个节点
            figsize: 图像大小元组 (宽, 高)
        """
        logger.info(f"可视化最短路径，起始节点: {start_node}，目标节点: {end_nodes}")
        if start_node not in self.node_info:
            logger.error(f"起始节点 {start_node} 不存在")
            print(f"起始节点 {start_node} 不存在")
            return
        
        G = self.to_networkx()
        
        # 如果没有指定目标节点，选择距离最远的几个节点
        if end_nodes is None:
            # 计算从起始节点到所有其他节点的最短路径长度
            path_lengths = nx.single_source_shortest_path_length(G, start_node)
            # 按照路径长度排序，选择最远的5个节点（或更少）
            sorted_lengths = sorted(path_lengths.items(), key=lambda x: x[1], reverse=True)
            end_nodes = [node for node, _ in sorted_lengths[:5]]
        elif isinstance(end_nodes, (str, int)):
            # 如果只传入了一个节点，转换为列表
            end_nodes = [end_nodes]
        
        plt.figure(figsize=figsize)
        pos = nx.spring_layout(G, seed=42)
        
        # 绘制所有节点和边（灰色，作为背景）
        nx.draw_networkx_nodes(G, pos, node_color='lightgray', node_size=300, alpha=0.6)
        nx.draw_networkx_edges(G, pos, edge_color='lightgray', width=1.0, alpha=0.3)
        
        # 获取并绘制所有路径
        paths = []
        path_edges = []
        
        for end_node in end_nodes:
            if end_node in self.node_info and end_node != start_node:
                try:
                    path = nx.shortest_path(G, source=start_node, target=end_node)
                    paths.append(path)
                    
                    # 收集路径中的边
                    for i in range(len(path) - 1):
                        path_edges.append((path[i], path[i + 1]))
                except nx.NetworkXNoPath:
                    logger.error(f"节点 {start_node} 和节点 {end_node} 之间不连通")
                    print(f"节点 {start_node} 和节点 {end_node} 之间不连通")
        
        # 绘制路径上的节点和边
        if paths:
            # 提取所有路径中的所有节点
            path_nodes = set()
            for path in paths:
                path_nodes.update(path)
            
            # 突出显示起始节点和目标节点
            nx.draw_networkx_nodes(G, pos, nodelist=[start_node], 
                                 node_color='green', node_size=500, alpha=1.0)
            nx.draw_networkx_nodes(G, pos, nodelist=end_nodes, 
                                 node_color='red', node_size=400, alpha=1.0)
            
            # 其他路径中的节点
            other_path_nodes = path_nodes - set([start_node] + end_nodes)
            if other_path_nodes:
                nx.draw_networkx_nodes(G, pos, nodelist=list(other_path_nodes), 
                                     node_color='blue', node_size=300, alpha=0.8)
            
            # 绘制路径边
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                                 edge_color='blue', width=2.0, alpha=1.0)
            
            # 绘制标签
            nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
            
            # 添加图例
            handles = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=15),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=15),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=15),
                plt.Line2D([0], [0], color='blue', lw=2)
            ]
            labels = ['起始节点', '目标节点', '路径中间节点', '最短路径']
            plt.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4)
            
            plt.title(f"从节点 {start_node} 出发的最短路径", fontsize=15)
            plt.axis("off")
            plt.tight_layout()
            plt.show()
            
            # 打印路径信息
            for i, (end_node, path) in enumerate(zip(end_nodes, paths)):
                print(f"路径 {i+1}: {start_node} -> {end_node}")
                print(f"  节点序列: {' -> '.join(map(str, path))}")
                print(f"  路径长度: {len(path) - 1}")
        else:
            logger.info("未找到任何路径")
            print("未找到任何路径")
    
    def to_pandas(self):
        """
        将图数据转换为Pandas DataFrames（方便导出和分析）
        
        返回:
            元组 (nodes_df, edges_df)，分别为节点DataFrame和边DataFrame
        """
        logger.info("转换为Pandas DataFrame")
        # 创建节点数据框
        nodes_data = []
        for node_id, attributes in self.node_info.items():
            node_data = {'node_id': node_id}
            node_data.update(attributes)
            nodes_data.append(node_data)
        
        # 创建边数据框
        edges_data = []
        for edge_dict in self.graph_edges:
            for (node1, node2), attributes in edge_dict.items():
                edge_data = {'source': node1, 'target': node2}
                edge_data.update(attributes)
                edges_data.append(edge_data)
        
        return pd.DataFrame(nodes_data), pd.DataFrame(edges_data)
    
    def export_to_csv(self, nodes_file='nodes.csv', edges_file='edges.csv'):
        """
        将图数据导出为CSV文件
        
        参数:
            nodes_file: 节点数据的CSV文件名
            edges_file: 边数据的CSV文件名
        """
        logger.info(f"导出图数据到CSV: {nodes_file}, {edges_file}")
        nodes_df, edges_df = self.to_pandas()
        
        nodes_df.to_csv(nodes_file, index=False)
        edges_df.to_csv(edges_file, index=False)
        
        print(f"节点数据已导出到 {nodes_file}")
        print(f"边数据已导出到 {edges_file}")
    
    def compute_all_metrics(self):
        """
        计算图的所有重要指标，返回分析报告
        
        返回:
            字典，包含各种图指标
        """
        logger.info("计算图的所有重要指标")
        G = self.to_networkx()
        metrics = {}
        
        # 基本信息
        metrics['节点数'] = G.number_of_nodes()
        metrics['边数'] = G.number_of_edges()
        
        # 度相关指标
        degrees = [d for _, d in G.degree()]
        metrics['平均度'] = np.mean(degrees)
        metrics['最大度'] = np.max(degrees)
        metrics['最小度'] = np.min(degrees)
        metrics['度标准差'] = np.std(degrees)
        
        # 连通性
        metrics['连通分量数'] = nx.number_connected_components(G)
        
        try:
            # 其他图指标
            metrics['平均聚类系数'] = nx.average_clustering(G)
            metrics['图密度'] = nx.density(G)
            
            # 尝试计算可能会失败的指标
            try:
                try:
                    metrics['直径'] = nx.diameter(G)
                except nx.NetworkXError:
                    # If the graph is not connected, calculate the diameter of the largest connected component
                    largest_cc = max(nx.connected_components(G), key=len)
                    subgraph = G.subgraph(largest_cc)
                    metrics['直径 (最大连通分量)'] = nx.diameter(subgraph)
            except nx.NetworkXError:
                # 图不连通时会出错
                largest_cc = max(nx.connected_components(G), key=len)
                subgraph = G.subgraph(largest_cc)
                metrics['直径 (最大连通分量)'] = nx.diameter(subgraph)
            
            try:
                metrics['平均最短路径长度'] = nx.average_shortest_path_length(G)
            except nx.NetworkXError:
                largest_cc = max(nx.connected_components(G), key=len)
                subgraph = G.subgraph(largest_cc)
                metrics['平均最短路径长度 (最大连通分量)'] = nx.average_shortest_path_length(subgraph)
        
        except Exception as e:
            logger.error(f"计算部分图指标时出错: {e}")
            print(f"计算部分图指标时出错: {e}")
        
        return metrics
    
    def print_metrics_report(self):
        """
        打印图的完整分析报告
        """
        logger.info("打印图的完整分析报告")
        metrics = self.compute_all_metrics()
        
        print("=" * 50)
        print(" " * 15 + "图分析报告")
        print("=" * 50)
        
        # 基本信息
        print("\n--- 基本信息 ---")
        print(f"节点数: {metrics.get('节点数', 'N/A')}")
        print(f"边数: {metrics.get('边数', 'N/A')}")
        print(f"图密度: {metrics.get('图密度', 'N/A'):.4f}")
        
        # 度分布
        print("\n--- 度分布 ---")
        print(f"平均度: {metrics.get('平均度', 'N/A'):.2f}")
        print(f"最大度: {metrics.get('最大度', 'N/A')}")
        print(f"最小度: {metrics.get('最小度', 'N/A')}")
        print(f"度标准差: {metrics.get('度标准差', 'N/A'):.2f}")
        
        # 连通性和路径
        print("\n--- 连通性和路径 ---")
        print(f"连通分量数: {metrics.get('连通分量数', 'N/A')}")
        
        if '直径' in metrics:
            print(f"直径: {metrics['直径']}")
        elif '直径 (最大连通分量)' in metrics:
            print(f"直径 (最大连通分量): {metrics['直径 (最大连通分量)']}")
        
        if '平均最短路径长度' in metrics:
            print(f"平均最短路径长度: {metrics['平均最短路径长度']:.4f}")
        elif '平均最短路径长度 (最大连通分量)' in metrics:
            print(f"平均最短路径长度 (最大连通分量): {metrics['平均最短路径长度 (最大连通分量)']:.4f}")
        
        # 聚类
        print("\n--- 聚类 ---")
        print(f"平均聚类系数: {metrics.get('平均聚类系数', 'N/A'):.4f}")
        
        # 补充说明
        print("\n" + "=" * 50)
        print("注: 部分指标可能因图结构而无法计算或只针对最大连通分量计算")
        print("=" * 50)
