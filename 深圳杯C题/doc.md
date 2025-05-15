Help on module tool:

NAME
    tool

CLASSES
    builtins.object
        UndirectedGraph
    
    class UndirectedGraph(builtins.object)
     |  UndirectedGraph(node_info, graph_edges)
     |  
     |  无向图类：用于管理节点属性和边信息，提供图分析功能，适用于数学建模
     |  
     |  Methods defined here:
     |  
     |  __init__(self, node_info, graph_edges)
     |      初始化无向图
     |      
     |      参数:
     |          node_info: 字典，键为节点ID，值为节点属性字典
     |          graph_edges: 列表，包含边信息字典，格式为[{(from_node,to_node):{边信息}}]
     |  
     |  add_edge(self, node1, node2, attributes=None)
     |      添加边
     |      
     |      参数:
     |          node1, node2: 两个节点的ID
     |          attributes: 边的属性字典
     |      
     |      返回:
     |          布尔值，表示是否成功添加
     |  
     |  add_edges(self, edges_list)
     |      批量添加边
     |      
     |      参数:
     |          edges_list: 列表，元素为 (node1, node2, attributes) 三元组，attributes可选
     |      
     |      返回:
     |          成功添加的边数量
     |  
     |  add_node(self, node_id, attributes=None)
     |      添加新节点
     |      
     |      参数:
     |          node_id: 节点ID
     |          attributes: 节点属性字典
     |      
     |      返回:
     |          布尔值，表示是否成功添加
     |  
     |  add_nodes(self, nodes_dict)
     |      批量添加节点
     |      
     |      参数:
     |          nodes_dict: 字典，键为节点ID，值为节点属性字典
     |      
     |      返回:
     |          成功添加的节点数量
     |  
     |  batch_update_edge_attributes(self, updates)
     |      批量更新多条边的属性
     |      
     |      参数:
     |          updates: 列表，元素为 (node1, node2, attributes) 三元组
     |      
     |      返回:
     |          成功更新的边数量
     |  
     |  batch_update_node_attributes(self, updates)
     |      批量更新多个节点的属性
     |      
     |      参数:
     |          updates: 字典，键为节点ID，值为属性更新字典
     |      
     |      返回:
     |          成功更新的节点数量
     |  
     |  compute_all_metrics(self)
     |      计算图的所有重要指标，返回分析报告
     |      
     |      返回:
     |          字典，包含各种图指标
     |  
     |  export_to_csv(self, nodes_file='nodes.csv', edges_file='edges.csv')
     |      将图数据导出为CSV文件
     |      
     |      参数:
     |          nodes_file: 节点数据的CSV文件名
     |          edges_file: 边数据的CSV文件名
     |  
     |  find_edges_by_attribute(self, attribute: str, value)
     |      查找具有特定属性值的所有边
     |      
     |      参数:
     |          attribute: 属性名
     |          value: 属性值
     |          
     |      返回:
     |          边元组列表 [(node1, node2), ...]
     |  
     |  find_nodes_by_attribute(self, attribute, value)
     |      查找具有特定属性值的所有节点
     |      
     |      参数:
     |          attribute: 属性名
     |          value: 属性值
     |          
     |      返回:
     |          节点ID列表
     |  
     |  find_path(self, start_node, end_node)
     |      查找两个节点之间的路径（使用广度优先搜索）
     |      
     |      参数:
     |          start_node: 起始节点ID
     |          end_node: 目标节点ID
     |          
     |      返回:
     |          如果存在路径，返回节点ID列表；否则返回None
     |  
     |  get_all_degrees(self)
     |      获取所有节点的度
     |      
     |      返回:
     |          字典，键为节点ID，值为度数
     |  
     |  get_all_paths(self, start_node, end_node, max_depth=10)
     |      找出两个节点之间的所有路径（深度优先搜索，限制深度）
     |      
     |      参数:
     |          start_node: 起始节点ID
     |          end_node: 目标节点ID
     |          max_depth: 最大搜索深度，防止路径过长
     |          
     |      返回:
     |          路径列表，每个路径是节点ID的列表
     |  
     |  get_attribute_summary(self, attribute_type='node', attribute=None)
     |      获取属性的统计摘要
     |      
     |      参数:
     |          attribute_type: "node" 或 "edge"，表示节点属性或边属性
     |          attribute: 属性名，若为None则返回所有属性的统计
     |      
     |      返回:
     |          DataFrame，包含属性统计信息
     |  
     |  get_average_degree(self)
     |      计算图的平均度
     |      
     |      返回:
     |          平均度（浮点数）
     |  
     |  get_edge(self, node1, node2)
     |      查找两个节点之间的边
     |      
     |      参数:
     |          node1, node2: 两个节点的ID
     |          
     |      返回:
     |          边信息字典，如果边不存在则返回None
     |  
     |  get_edge_attribute(self, node1, node2, attribute=None)
     |      获取边的属性
     |      
     |      参数:
     |          node1, node2: 两个节点的ID
     |          attribute: 要查询的属性名，若为None则返回该边的所有属性
     |          
     |      返回:
     |          如果attribute为None，返回边的所有属性字典；否则返回指定的属性值
     |          如果边不存在或属性不存在，返回None
     |  
     |  get_edge_attribute_statistics(self, attribute)
     |      统计边特定属性的分布情况
     |      
     |      参数:
     |          attribute: 属性名
     |      
     |      返回:
     |          Counter对象，计数每个属性值的出现次数
     |  
     |  get_node_attribute(self, node_id, attribute=None)
     |      获取节点的属性
     |      
     |      参数:
     |          node_id: 节点ID
     |          attribute: 要查询的属性名，若为None则返回该节点的所有属性
     |          
     |      返回:
     |          如果attribute为None，返回节点的所有属性字典；否则返回指定的属性值
     |          如果节点不存在或属性不存在，返回None
     |  
     |  get_node_attribute_statistics(self, attribute)
     |      统计节点特定属性的分布情况
     |      
     |      参数:
     |          attribute: 属性名
     |      
     |      返回:
     |          Counter对象，计数每个属性值的出现次数
     |  
     |  get_node_degree(self, node_id)
     |      获取节点的度
     |      
     |      参数:
     |          node_id: 节点ID
     |      
     |      返回:
     |          度数（整数）
     |  
     |  has_edge(self, node1, node2)
     |      检查两个节点之间是否有边
     |      
     |      参数:
     |          node1, node2: 两个节点的ID
     |          
     |      返回:
     |          布尔值，表示是否存在边
     |  
     |  is_connected(self, node1, node2)
     |      检查两个节点是否连通，并打印路径
     |      
     |      参数:
     |          node1, node2: 两个节点的ID
     |          
     |      返回:
     |          布尔值，表示两个节点是否连通
     |  
     |  plot_shortest_paths(self, start_node, end_nodes=None, figsize=(12, 10))
     |      可视化从起始节点到一个或多个目标节点的最短路径
     |      
     |      参数:
     |          start_node: 起始节点ID
     |          end_nodes: 目标节点ID列表，若为None则选择距离最远的几个节点
     |          figsize: 图像大小元组 (宽, 高)
     |  
     |  print_graph(self)
     |      打印整个图的结构：节点属性和边信息
     |  
     |  print_metrics_report(self)
     |      打印图的完整分析报告
     |  
     |  print_node_neighbors(self, node_id)
     |      打印指定节点的所有邻居
     |      
     |      参数:
     |          node_id: 节点ID
     |  
     |  remove_edge(self, node1, node2)
     |      删除边
     |      
     |      参数:
     |          node1, node2: 两个节点的ID
     |      
     |      返回:
     |          布尔值，表示是否成功删除
     |  
     |  remove_edges(self, edges_list)
     |      批量删除边
     |      
     |      参数:
     |          edges_list: 列表，元素为 (node1, node2) 元组
     |      
     |      返回:
     |          成功删除的边数量
     |  
     |  remove_node(self, node_id)
     |      删除节点及其相关的所有边
     |      
     |      参数:
     |          node_id: 要删除的节点ID
     |      
     |      返回:
     |          布尔值，表示是否成功删除
     |  
     |  remove_nodes(self, node_ids)
     |      批量删除节点
     |      
     |      参数:
     |          node_ids: 要删除的节点ID列表
     |      
     |      返回:
     |          成功删除的节点数量
     |  
     |  to_networkx(self)
     |      转换为NetworkX图对象（用于高级分析和可视化）
     |      
     |      返回:
     |          NetworkX Graph对象
     |  
     |  to_pandas(self)
     |      将图数据转换为Pandas DataFrames（方便导出和分析）
     |      
     |      返回:
     |          元组 (nodes_df, edges_df)，分别为节点DataFrame和边DataFrame
     |  
     |  update_edge_attribute(self, node1, node2, attribute, value)
     |      更新边属性
     |      
     |      参数:
     |          node1, node2: 两个节点的ID
     |          attribute: 属性名
     |          value: 新的属性值
     |      
     |      返回:
     |          布尔值，表示是否成功更新
     |  
     |  update_edge_attributes(self, node1, node2, attributes)
     |      批量更新边属性
     |      
     |      参数:
     |          node1, node2: 两个节点的ID
     |          attributes: 属性字典
     |      
     |      返回:
     |          布尔值，表示是否成功更新
     |  
     |  update_node_attribute(self, node_id, attribute, value)
     |      更新节点属性
     |      
     |      参数:
     |          node_id: 节点ID
     |          attribute: 属性名
     |          value: 新的属性值
     |      
     |      返回:
     |          布尔值，表示是否成功更新
     |  
     |  update_node_attributes(self, node_id, attributes)
     |      批量更新节点属性
     |      
     |      参数:
     |          node_id: 节点ID
     |          attributes: 属性字典
     |      
     |      返回:
     |          布尔值，表示是否成功更新
     |  
     |  visualize(self, figsize=(10, 8), node_size=300, node_color='skyblue', edge_color='gray', font_size=10, with_labels=True, node_attribute=None, edge_attribute=None, title=None)
     |      可视化图结构
     |      
     |      参数:
     |          figsize: 图像大小元组 (宽, 高)
     |          node_size: 节点大小
     |          node_color: 节点颜色（如果node_attribute不为None，则根据属性映射颜色）
     |          edge_color: 边颜色（如果edge_attribute不为None，则根据属性映射颜色）
     |          font_size: 标签字体大小
     |          with_labels: 是否显示节点标签
     |          node_attribute: 用于节点颜色映射的属性名
     |          edge_attribute: 用于边颜色映射的属性名
     |          title: 图表标题
     |  
     |  visualize_attribute_distribution(self, attribute, attribute_type='node', figsize=(10, 6), plot_type='hist', top_n=None)
     |      可视化属性值分布
     |      
     |      参数:
     |          attribute: 属性名
     |          attribute_type: "node" 或 "edge"，表示节点属性或边属性
     |          figsize: 图像大小元组 (宽, 高)
     |          plot_type: "hist"（直方图）或 "bar"（条形图）
     |          top_n: 对于条形图，只显示前N个最常见的值
     |  
     |  visualize_communities(self, algorithm='louvain', figsize=(12, 10), with_labels=True)
     |      社区检测并可视化
     |      
     |      参数:
     |          algorithm: 社区检测算法名称，"louvain"、"girvan_newman"或"label_propagation"
     |          figsize: 图像大小元组 (宽, 高)
     |          with_labels: 是否显示节点标签
     |  
     |  visualize_degree_distribution(self, figsize=(10, 6), bins=10)
     |      可视化节点度分布
     |      
     |      参数:
     |          figsize: 图像大小元组 (宽, 高)
     |          bins: 直方图的柱数
     |  
     |  visualize_graph_metrics(self, figsize=(15, 10))
     |      可视化图的各种度量指标
     |      
     |      参数:
     |          figsize: 图像大小元组 (宽, 高)
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

FILE
    e:\学习\数模相关\code_of_argorithm\深圳杯c题\utils\tool.py


