class UndirectedGraph:
    """
    无向图类：用于管理节点属性和边信息，提供图分析功能
    """
    def __init__(self, node_info, graph_edges):
        """
        初始化无向图
        
        参数:
            node_info: 字典，键为节点ID，值为节点属性字典
            graph_edges: 列表，包含边信息字典，格式为[{(from_node,to_node):{边信息}}]
        """
        self.node_info = node_info
        self.graph_edges = graph_edges
        # 构建邻接表，用于路径查找和连通性检查
        self.adjacency_list = self._build_adjacency_list()


    
    def _build_adjacency_list(self):
        """构建邻接表，用于快速查找相邻节点"""
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
                
        return adjacency_list
    
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
            print(f"节点 {node_id} 不存在")
            return None
            
        if attribute is None:
            return self.node_info[node_id]
        elif attribute in self.node_info[node_id]:
            return self.node_info[node_id][attribute]
        else:
            print(f"节点 {node_id} 没有属性 '{attribute}'")
            return None
    
    def get_edge(self, node1, node2):
        """
        查找两个节点之间的边
        
        参数:
            node1, node2: 两个节点的ID
            
        返回:
            边信息字典，如果边不存在则返回None
        """
        # 确保node1 <= node2，因为我们的存储规则是较小节点ID在前
        if node1 > node2:
            node1, node2 = node2, node1
            
        # 查询边信息
        for edge_dict in self.graph_edges:
            if (node1, node2) in edge_dict:
                return edge_dict[(node1, node2)]
                
        return None
    
    def get_edge_attribute(self, node1, node2, attribute=None):
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
        
        if edge_info is None:
            print(f"节点 {node1} 和节点 {node2} 之间没有边")
            return None
            
        if attribute is None:
            return edge_info
        elif attribute in edge_info:
            return edge_info[attribute]
        else:
            print(f"边 ({node1}, {node2}) 没有属性 '{attribute}'")
            return None
    
    def has_edge(self, node1, node2):
        """
        检查两个节点之间是否有边
        
        参数:
            node1, node2: 两个节点的ID
            
        返回:
            布尔值，表示是否存在边
        """
        return self.get_edge(node1, node2) is not None
    
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
            print(f"节点 {start_node} 或节点 {end_node} 不存在")
            return None
            
        if start_node == end_node:
            return [start_node]
            
        # 广度优先搜索
        visited = set()
        queue = [(start_node, [start_node])]  # (当前节点, 路径)
        
        while queue:
            current, path = queue.pop(0)
            
            if current == end_node:
                return path
                
            if current in visited:
                continue
                
            visited.add(current)
            
            for neighbor in self.adjacency_list[current]:
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
                    
        print(f"节点 {start_node} 和节点 {end_node} 之间不连通")
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
            print(f"节点 {node1} 和节点 {node2} 连通")
            print(f"路径: {' -> '.join(map(str, path))}")
            return True
        else:
            print(f"节点 {node1} 和节点 {node2} 不连通")
            return False
    
    def print_graph(self):
        """打印整个图的结构：节点属性和边信息"""
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
            print(f"节点 {node_id} 不存在")
            return
            
        neighbors = self.adjacency_list[node_id]
        if not neighbors:
            print(f"节点 {node_id} 没有邻居")
        else:
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
                
        return matching_nodes
    
    def find_edges_by_attribute(self, attribute, value):
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
        return paths