
E:\ѧϰ\��ģ���\code_of_argorithm>python.exe -m pydoc ���ڱ�C��\utils\tool.py ���ڱ�C��\utils\RiskAnalyzer.py ���ڱ�C��\utils\data_loder.py 
Help on module tool:

NAME
    tool

CLASSES
    builtins.object
        UndirectedGraph
    
    class UndirectedGraph(builtins.object)
     |  UndirectedGraph(node_info, graph_edges)
     |  
     |  ����ͼ�ࣺ���ڹ���ڵ����Ժͱ���Ϣ���ṩͼ�������ܣ���������ѧ��ģ
     |  
     |  Methods defined here:
     |  
     |  __init__(self, node_info, graph_edges)
     |      ��ʼ������ͼ
     |      
     |      ����:
     |          node_info: �ֵ䣬��Ϊ�ڵ�ID��ֵΪ�ڵ������ֵ�
     |          graph_edges: �б���������Ϣ�ֵ䣬��ʽΪ[{(from_node,to_node):{����Ϣ}}]
     |  
     |  add_edge(self, node1, node2, attributes=None)
     |      ��ӱ�
     |      
     |      ����:
     |          node1, node2: �����ڵ��ID
     |          attributes: �ߵ������ֵ�
     |      
     |      ����:
     |          ����ֵ����ʾ�Ƿ�ɹ����
     |  
     |  add_edges(self, edges_list)
     |      ������ӱ�
     |      
     |      ����:
     |          edges_list: �б�Ԫ��Ϊ (node1, node2, attributes) ��Ԫ�飬attributes��ѡ
     |      
     |      ����:
     |          �ɹ���ӵı�����
     |  
     |  add_node(self, node_id, attributes=None)
     |      ����½ڵ�
     |      
     |      ����:
     |          node_id: �ڵ�ID
     |          attributes: �ڵ������ֵ�
     |      
     |      ����:
     |          ����ֵ����ʾ�Ƿ�ɹ����
     |  
     |  add_nodes(self, nodes_dict)
     |      ������ӽڵ�
     |      
     |      ����:
     |          nodes_dict: �ֵ䣬��Ϊ�ڵ�ID��ֵΪ�ڵ������ֵ�
     |      
     |      ����:
     |          �ɹ���ӵĽڵ�����
     |  
     |  batch_update_edge_attributes(self, updates)
     |      �������¶����ߵ�����
     |      
     |      ����:
     |          updates: �б�Ԫ��Ϊ (node1, node2, attributes) ��Ԫ��
     |      
     |      ����:
     |          �ɹ����µı�����
     |  
     |  batch_update_node_attributes(self, updates)
     |      �������¶���ڵ������
     |      
     |      ����:
     |          updates: �ֵ䣬��Ϊ�ڵ�ID��ֵΪ���Ը����ֵ�
     |      
     |      ����:
     |          �ɹ����µĽڵ�����
     |  
     |  compute_all_metrics(self)
     |      ����ͼ��������Ҫָ�꣬���ط�������
     |      
     |      ����:
     |          �ֵ䣬��������ͼָ��
     |  
     |  export_to_csv(self, nodes_file='nodes.csv', edges_file='edges.csv')
     |      ��ͼ���ݵ���ΪCSV�ļ�
     |      
     |      ����:
     |          nodes_file: �ڵ����ݵ�CSV�ļ���
     |          edges_file: �����ݵ�CSV�ļ���
     |  
     |  find_edges_by_attribute(self, attribute: str, value)
     |      ���Ҿ����ض�����ֵ�����б�
     |      
     |      ����:
     |          attribute: ������
     |          value: ����ֵ
     |          
     |      ����:
     |          ��Ԫ���б� [(node1, node2), ...]
     |  
     |  find_nodes_by_attribute(self, attribute, value)
     |      ���Ҿ����ض�����ֵ�����нڵ�
     |      
     |      ����:
     |          attribute: ������
     |          value: ����ֵ
     |          
     |      ����:
     |          �ڵ�ID�б�
     |  
     |  find_path(self, start_node, end_node)
     |      ���������ڵ�֮���·����ʹ�ù������������
     |      
     |      ����:
     |          start_node: ��ʼ�ڵ�ID
     |          end_node: Ŀ��ڵ�ID
     |          
     |      ����:
     |          �������·�������ؽڵ�ID�б����򷵻�None
     |  
     |  get_all_degrees(self)
     |      ��ȡ���нڵ�Ķ�
     |      
     |      ����:
     |          �ֵ䣬��Ϊ�ڵ�ID��ֵΪ����
     |  
     |  get_all_paths(self, start_node, end_node, max_depth=10)
     |      �ҳ������ڵ�֮�������·�����������������������ȣ�
     |      
     |      ����:
     |          start_node: ��ʼ�ڵ�ID
     |          end_node: Ŀ��ڵ�ID
     |          max_depth: ���������ȣ���ֹ·������
     |          
     |      ����:
     |          ·���б�ÿ��·���ǽڵ�ID���б�
     |  
     |  get_attribute_summary(self, attribute_type='node', attribute=None)
     |      ��ȡ���Ե�ͳ��ժҪ
     |      
     |      ����:
     |          attribute_type: "node" �� "edge"����ʾ�ڵ����Ի������
     |          attribute: ����������ΪNone�򷵻��������Ե�ͳ��
     |      
     |      ����:
     |          DataFrame����������ͳ����Ϣ
     |  
     |  get_average_degree(self)
     |      ����ͼ��ƽ����
     |      
     |      ����:
     |          ƽ���ȣ���������
     |  
     |  get_edge(self, node1, node2) -> dict
     |      ���������ڵ�֮��ı�
     |      
     |      ����:
     |          node1, node2: �����ڵ��ID
     |          
     |      ����:
     |          ����Ϣ�ֵ䣬����߲������򷵻ؿ��ֵ�
     |  
     |  get_edge_attribute(self, node1, node2, attribute=None) -> Union[int, float, str, dict, NoneType]
     |      ��ȡ�ߵ�����
     |      
     |      ����:
     |          node1, node2: �����ڵ��ID
     |          attribute: Ҫ��ѯ������������ΪNone�򷵻ظñߵ���������
     |          
     |      ����:
     |          ���attributeΪNone�����رߵ����������ֵ䣻���򷵻�ָ��������ֵ
     |          ����߲����ڻ����Բ����ڣ�����None
     |  
     |  get_edge_attribute_statistics(self, attribute)
     |      ͳ�Ʊ��ض����Եķֲ����
     |      
     |      ����:
     |          attribute: ������
     |      
     |      ����:
     |          Counter���󣬼���ÿ������ֵ�ĳ��ִ���
     |  
     |  get_node_attribute(self, node_id, attribute=None)
     |      ��ȡ�ڵ������
     |      
     |      ����:
     |          node_id: �ڵ�ID
     |          attribute: Ҫ��ѯ������������ΪNone�򷵻ظýڵ����������
     |          
     |      ����:
     |          ���attributeΪNone�����ؽڵ�����������ֵ䣻���򷵻�ָ��������ֵ
     |          ����ڵ㲻���ڻ����Բ����ڣ�����None
     |  
     |  get_node_attribute_statistics(self, attribute)
     |      ͳ�ƽڵ��ض����Եķֲ����
     |      
     |      ����:
     |          attribute: ������
     |      
     |      ����:
     |          Counter���󣬼���ÿ������ֵ�ĳ��ִ���
     |  
     |  get_node_degree(self, node_id)
     |      ��ȡ�ڵ�Ķ�
     |      
     |      ����:
     |          node_id: �ڵ�ID
     |      
     |      ����:
     |          ������������
     |  
     |  has_edge(self, node1, node2)
     |      ��������ڵ�֮���Ƿ��б�
     |      
     |      ����:
     |          node1, node2: �����ڵ��ID
     |          
     |      ����:
     |          ����ֵ����ʾ�Ƿ���ڱ�
     |  
     |  is_connected(self, node1, node2)
     |      ��������ڵ��Ƿ���ͨ������ӡ·��
     |      
     |      ����:
     |          node1, node2: �����ڵ��ID
     |          
     |      ����:
     |          ����ֵ����ʾ�����ڵ��Ƿ���ͨ
     |  
     |  neighbors(self, node_id: int) -> list[int]
     |      ��ȡָ���ڵ�������ھӽڵ�
     |      
     |      ����:
     |          node_id: �ڵ�ID
     |          
     |      ����:
     |          �ھӽڵ�ID�б�
     |  
     |  plot_shortest_paths(self, start_node, end_nodes=None, figsize=(12, 10))
     |      ���ӻ�����ʼ�ڵ㵽һ������Ŀ��ڵ�����·��
     |      
     |      ����:
     |          start_node: ��ʼ�ڵ�ID
     |          end_nodes: Ŀ��ڵ�ID�б���ΪNone��ѡ�������Զ�ļ����ڵ�
     |          figsize: ͼ���СԪ�� (��, ��)
     |  
     |  print_graph(self)
     |      ��ӡ����ͼ�Ľṹ���ڵ����Ժͱ���Ϣ
     |  
     |  print_metrics_report(self)
     |      ��ӡͼ��������������
     |  
     |  print_node_neighbors(self, node_id)
     |      ��ӡָ���ڵ�������ھ�
     |      
     |      ����:
     |          node_id: �ڵ�ID
     |  
     |  remove_edge(self, node1, node2)
     |      ɾ����
     |      
     |      ����:
     |          node1, node2: �����ڵ��ID
     |      
     |      ����:
     |          ����ֵ����ʾ�Ƿ�ɹ�ɾ��
     |  
     |  remove_edges(self, edges_list)
     |      ����ɾ����
     |      
     |      ����:
     |          edges_list: �б�Ԫ��Ϊ (node1, node2) Ԫ��
     |      
     |      ����:
     |          �ɹ�ɾ���ı�����
     |  
     |  remove_node(self, node_id)
     |      ɾ���ڵ㼰����ص����б�
     |      
     |      ����:
     |          node_id: Ҫɾ���Ľڵ�ID
     |      
     |      ����:
     |          ����ֵ����ʾ�Ƿ�ɹ�ɾ��
     |  
     |  remove_nodes(self, node_ids)
     |      ����ɾ���ڵ�
     |      
     |      ����:
     |          node_ids: Ҫɾ���Ľڵ�ID�б�
     |      
     |      ����:
     |          �ɹ�ɾ���Ľڵ�����
     |  
     |  to_networkx(self)
     |      ת��ΪNetworkXͼ�������ڸ߼������Ϳ��ӻ���
     |      
     |      ����:
     |          NetworkX Graph����
     |  
     |  to_pandas(self)
     |      ��ͼ����ת��ΪPandas DataFrames�����㵼���ͷ�����
     |      
     |      ����:
     |          Ԫ�� (nodes_df, edges_df)���ֱ�Ϊ�ڵ�DataFrame�ͱ�DataFrame
     |  
     |  update_edge_attribute(self, node1, node2, attribute, value)
     |      ���±�����
     |      
     |      ����:
     |          node1, node2: �����ڵ��ID
     |          attribute: ������
     |          value: �µ�����ֵ
     |      
     |      ����:
     |          ����ֵ����ʾ�Ƿ�ɹ�����
     |  
     |  update_edge_attributes(self, node1, node2, attributes)
     |      �������±�����
     |      
     |      ����:
     |          node1, node2: �����ڵ��ID
     |          attributes: �����ֵ�
     |      
     |      ����:
     |          ����ֵ����ʾ�Ƿ�ɹ�����
     |  
     |  update_node_attribute(self, node_id, attribute, value)
     |      ���½ڵ�����
     |      
     |      ����:
     |          node_id: �ڵ�ID
     |          attribute: ������
     |          value: �µ�����ֵ
     |      
     |      ����:
     |          ����ֵ����ʾ�Ƿ�ɹ�����
     |  
     |  update_node_attributes(self, node_id, attributes)
     |      �������½ڵ�����
     |      
     |      ����:
     |          node_id: �ڵ�ID
     |          attributes: �����ֵ�
     |      
     |      ����:
     |          ����ֵ����ʾ�Ƿ�ɹ�����
     |  
     |  visualize(self, figsize=(10, 8), node_size=300, node_color='skyblue', edge_color='gray', font_size=10, with_labels=True, node_attribute=None, edge_attribute=None, title=None)
     |      ���ӻ�ͼ�ṹ
     |      
     |      ����:
     |          figsize: ͼ���СԪ�� (��, ��)
     |          node_size: �ڵ��С
     |          node_color: �ڵ���ɫ�����node_attribute��ΪNone�����������ӳ����ɫ��
     |          edge_color: ����ɫ�����edge_attribute��ΪNone�����������ӳ����ɫ��
     |          font_size: ��ǩ�����С
     |          with_labels: �Ƿ���ʾ�ڵ��ǩ
     |          node_attribute: ���ڽڵ���ɫӳ���������
     |          edge_attribute: ���ڱ���ɫӳ���������
     |          title: ͼ�����
     |  
     |  visualize_attribute_distribution(self, attribute, attribute_type='node', figsize=(10, 6), plot_type='hist', top_n=None)
     |      ���ӻ�����ֵ�ֲ�
     |      
     |      ����:
     |          attribute: ������
     |          attribute_type: "node" �� "edge"����ʾ�ڵ����Ի������
     |          figsize: ͼ���СԪ�� (��, ��)
     |          plot_type: "hist"��ֱ��ͼ���� "bar"������ͼ��
     |          top_n: ��������ͼ��ֻ��ʾǰN�������ֵ
     |  
     |  visualize_communities(self, algorithm='louvain', figsize=(12, 10), with_labels=True)
     |      ������Ⲣ���ӻ�
     |      
     |      ����:
     |          algorithm: ��������㷨���ƣ�"louvain"��"girvan_newman"��"label_propagation"
     |          figsize: ͼ���СԪ�� (��, ��)
     |          with_labels: �Ƿ���ʾ�ڵ��ǩ
     |  
     |  visualize_degree_distribution(self, figsize=(10, 6), bins=10)
     |      ���ӻ��ڵ�ȷֲ�
     |      
     |      ����:
     |          figsize: ͼ���СԪ�� (��, ��)
     |          bins: ֱ��ͼ������
     |  
     |  visualize_graph_metrics(self, figsize=(15, 10))
     |      ���ӻ�ͼ�ĸ��ֶ���ָ��
     |      
     |      ����:
     |          figsize: ͼ���СԪ�� (��, ��)
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

DATA
    Optional = typing.Optional
        Optional type.
        
        Optional[X] is equivalent to Union[X, None].
    
    Union = typing.Union
        Union type; Union[X, Y] means either X or Y.
        
        To define a union, use e.g. Union[int, str].  Details:
        - The arguments must be types and there must be at least one.
        - None as an argument is a special case and is replaced by
          type(None).
        - Unions of unions are flattened, e.g.::
        
            Union[Union[int, str], float] == Union[int, str, float]
        
        - Unions of a single argument vanish, e.g.::
        
            Union[int] == int  # The constructor actually returns int
        
        - Redundant arguments are skipped, e.g.::
        
            Union[int, str, int] == Union[int, str]
        
        - When comparing unions, the argument order is ignored, e.g.::
        
            Union[int, str] == Union[str, int]
        
        - You cannot subclass or instantiate a union.
        - You can use Optional[X] as a shorthand for Union[X, None].
    
    logger = <loguru.logger handlers=[(id=0, level=10, sink=<stderr>)]>

FILE
    e:\ѧϰ\��ģ���\code_of_argorithm\���ڱ�c��\utils\tool.py


problem in ���ڱ�C��\utils\RiskAnalyzer.py - ModuleNotFoundError: No module named 'utils'
Help on module data_loder:

NAME
    data_loder

DESCRIPTION
    # �����ݼ��ص��ڴ���
    ���ݸ�ʽΪjson

DATA
    edges_file = r'E:\ѧϰ\��ģ���\code_of_argorithm\���ڱ�C��\data_file\edges_info...
    edges_info = [{(1, 2): {'Reactance': 0.0021, 'Resistor': 0.0031, 'leng...
    f = <_io.TextIOWrapper name='E:\\ѧϰ\\��ģ���\\code_of_a...file\\nodes_inf...
    logger = <loguru.logger handlers=[(id=0, level=10, sink=<stderr>)]>
    nodes_file = r'E:\ѧϰ\��ģ���\code_of_argorithm\���ڱ�C��\data_file\nodes_info...
    nodes_info = {'1': {'DG': False, 'power': 40.0, 'type': '����', 'which_s...

FILE
    e:\ѧϰ\��ģ���\code_of_argorithm\���ڱ�c��\utils\data_loder.py


