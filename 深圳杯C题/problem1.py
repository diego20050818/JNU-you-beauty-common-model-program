from utils.RiskAnalyzer import RiskAnalyzer
from utils.tool import UndirectedGraph
from utils.data_loder import edges_info, nodes_info
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
from tabulate import tabulate
from loguru import logger
import argparse
import ast
import sys
import time

analyzer = RiskAnalyzer(nodes_info=nodes_info,edges_info=edges_info)
graph = UndirectedGraph(node_info=nodes_info,graph_edges=edges_info)


def visualized():
    G = nx.DiGraph()
    
    # ---------- Feeder颜色 ----------
    feeder_color_map = {
        'CB1': 'tomato',
        'CB2': 'mediumseagreen',
        'CB3': 'royalblue',
        'default': 'gray'
    }

    # ---------- 添加节点 ----------
    node_colors = {}
    node_labels = {}
    for node_id, node_info in nodes_info.items():
        feeder = node_info.get('which_substation', 'default')
        color = feeder_color_map.get(feeder, feeder_color_map['default'])
        # 确保节点ID统一类型
        node_key = int(node_id)
        G.add_node(node_key, feeder=feeder)
        node_colors[node_key] = color
        #node_labels[node_key] = f"v{node_id}\n{node_info['type']}\n{node_info['power']}kw\n{feeder}"
        node_labels[node_key] = f"v{node_id}"
    print(f"添加了 {len(G.nodes())} 个节点")
    print(f"节点列表: {list(G.nodes())}")

    # ---------- 添加边 ----------
    edge_labels = {}
    edge_currents = {}
    added_edges_count = 0

    for edge in edges_info:
        begin, end = list(edge.keys())[0]
        info = list(edge.values())[0]
        
        # 确保节点ID类型一致
        begin_int = int(begin)
        end_int = int(end)
        
        # 检查节点是否存在
        if begin_int not in G.nodes():
            print(f"警告：起始节点 {begin_int} 不存在于图中")
            continue
        if end_int not in G.nodes():
            print(f"警告：终止节点 {end_int} 不存在于图中")
            continue

        try:
            risk = analyzer.edge_risk(begin, end)
            capacity = analyzer.calculate_capacity(begin, end)
            current = analyzer.I_ij(begin, end)
            current = max(current, 0.1)  # 避免为0不显示
            
            #label = f"风险:{risk:.3f}\n容量:{capacity:.1f}\n电流:{current:.1f}A\n{info['type']}"
            label = f"风险：{risk:.3f}"
            G.add_edge(begin_int, end_int)
            edge_labels[(begin_int, end_int)] = label
            edge_currents[(begin_int, end_int)] = current
            added_edges_count += 1
            
        except Exception as e:
            print(f"处理边 ({begin}, {end}) 时出错: {e}")
            continue

    print(f"成功添加了 {added_edges_count} 条边")
    print(f"边列表: {list(G.edges())}")
    
    if len(G.edges()) == 0:
        print("错误：没有边被添加到图中！")
        return

    # ---------- 自定义布局（分层） ----------
    '''
    pos = {}
    y_base = {'CB1': 3, 'CB2': 2, 'CB3': 1}
    x_counter = {'CB1': 0, 'CB2': 0, 'CB3': 0, 'default': 0}'''

    #pos = nx.kamada_kawai_layout(G,weight='length',scale=1,dim=2)
    # ---------- 自定义布局 ----------
    pos = {
    1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (3, 0), 5: (4, 0), 6: (5, 0), 7: (6, 0),
    8: (7, 0), 9: (8, 0), 10: (9, 0), 11: (10, 0), 12: (11, 0), 13: (12, 0),
    14: (5, -1), 15: (4, -1), 16: (3, -1),
    17: (2, 1), 18: (3, 1), 19: (4, 1),
    20: (0, -1), 21: (-1, -1), 22: (-2, -1),
    23: (2, 2), 24: (3, 2), 25: (4, 2),
    26: (5, 2), 27: (6, 2), 28: (7, 2),
    29: (8, 2), 30: (9, 2), 31: (10, 2), 32: (11, 2),
    33: (5, 3), 34: (4, 3), 35: (3, 3),
    36: (3, 1), 37: (1, 1), 38: (0, 1), 39: (-1, 1),
    40: (2, 3), 41: (1, 3), 42: (1, 4),
    43: (14, 2), 44: (15, 2), 45: (16, 2), 46: (17, 2), 47: (18, 2), 48: (19, 2),
    49: (15, 1), 50: (16, 1), 51: (17, 1), 52: (18, 1),
    53: (16, 3), 54: (17, 3), 55: (18, 3),
    56: (8, 4), 57: (9, 4), 58: (10, 4), 59: (11, 4), 60: (12, 4), 61: (13, 4), 62: (14, 4)
    }

    for node_id in G.nodes():
        feeder = G.nodes[node_id].get('feeder', 'default')
        #x = x_counter[feeder] * 2
        #y = y_base.get(feeder, 0)
        #pos[node_id] = (x, y)
        #x_counter[feeder] += 1

    # ---------- 画图 ----------
    fig, ax = plt.subplots(figsize=(16, 8))

    # 节点
    nx.draw_networkx_nodes(G, pos,
                           node_color=[node_colors[n] for n in G.nodes()],
                           node_size=100, ax=ax)
    nx.draw_networkx_labels(G, pos, labels=node_labels,
                            font_size=8, font_family='SimHei', ax=ax)

    # 检查边数据
    if not edge_currents:
        print("错误：edge_currents 为空！")
        return
        
    # 所有边
    all_edges = list(G.edges())
    all_currents = [edge_currents[e] for e in all_edges]
    
    if not all_currents:
        print("错误：all_currents 为空！")
        return
        
    edge_vmin = min(edge_currents.values())
    edge_vmax = max(edge_currents.values())
    
    print(f"电流范围: {edge_vmin:.2f} - {edge_vmax:.2f}")

    cmap = plt.cm.coolwarm
    norm = mcolors.Normalize(vmin=edge_vmin, vmax=edge_vmax)

    # 统一绘制所有边
    nx.draw_networkx_edges(G, pos, edgelist=all_edges,
                           edge_color=all_currents,
                           edge_cmap=cmap,
                           edge_vmin=edge_vmin, edge_vmax=edge_vmax,
                           width=2,  # 增加线宽便于观察
                           style='solid', 
                           ax=ax, 
                           alpha=0.8,
                           arrows=False)  # 确保显示方向箭头

    # 边标签
    if edge_labels:
        nx.draw_networkx_edge_labels(G, pos,
                                     edge_labels=edge_labels,
                                     font_size=6, font_family='SimHei',
                                     label_pos=0.5, ax=ax)

    # 色条
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label("current (A)")

    ax.set_title("电网风险可视化（按馈线布局）", fontsize=16,fontfamily='SimHei')
    ax.axis('off')
    
    # 调整图形边界
    ax.margins(0.1)
    
    plt.tight_layout()
    plt.show()




@logger.catch
def problem1(print_entire_graph=False, instances=None, print_logs=True):
    """问题1：验证一条线路的失负荷与过负荷风险，并进行基础分析"""
    begin = 1
    end = 2
    edge_risk = analyzer.edge_risk(begin,end)
    capacity = analyzer.calculate_capacity(begin,end)
    current = analyzer.I_ij(begin,end)
    print(f"线路{begin}->{end}:\nedge_risk\t{edge_risk}\ncapacity:\t{capacity}\ncurrent:\t{current}")
    
    analyzer.print_analysis_summary()
    #graph.visualize_graph_metrics()
    visualized()
    #visualized_matplotlib()

logger.remove()
logger.add(sys.stderr, level="WARNING") 
problem1()