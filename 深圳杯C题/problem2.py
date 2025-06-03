from utils.RiskAnalyzer import RiskAnalyzer
from utils.data_loder import edges_info, nodes_info

import numpy as np  
import matplotlib.pyplot as plt  
from collections import deque 
import json 
from tqdm.rich import tqdm
from loguru import logger
import sys
from prettytable import PrettyTable

def problem2():
    """问题2：分析 DG 容量从 300 至 900kW 的风险演变曲线"""
    capacities = np.arange(300, 901, 10)
    risks = []
    details = []
    failure_probability = []
    load_loss_consequence = []
    load_loss_risk = []
    overload_probability = []
    overload_consequence = []

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
    plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

    for cap in tqdm(capacities, desc="问题2：容量模拟中"):
        analyse = RiskAnalyzer(nodes_info=nodes_info, edges_info=edges_info)
        analyse.dg_capacity = cap
        result = analyse.comprehensive_risk_analysis()
        risks.append(result['total_risk'])
        details.append(result)
        failure_probability.append(result['failure_probability'])
        load_loss_consequence.append(result['load_loss_consequence'])
        load_loss_risk.append(result['load_loss_risk'])
        overload_probability.append(result['overload_probability'])
        overload_consequence.append(result['overload_consequence'])

    # 输出数据说明
    # 构建表格
    table = PrettyTable()
    table.field_names = [
        "容量(kW)", "系统总风险", "失效概率", "失负荷后果", "失负荷风险", "过载概率", "过载后果"
    ]

    for cap, result in zip(capacities, details):
        table.add_row([
            cap,
            f"{result['total_risk']:.6f}",
            f"{result.get('failure_probability', 0):.6f}" if result.get('failure_probability') is not None else "",
            f"{result.get('load_loss_consequence', 0):.6f}" if result.get('load_loss_consequence') is not None else "",
            f"{result.get('load_loss_risk', 0):.6f}" if result.get('load_loss_risk') is not None else "",
            f"{result.get('overload_probability', 0):.6f}" if result.get('overload_probability') is not None else "",
            f"{result.get('overload_consequence', 0):.6f}" if result.get('overload_consequence') is not None else ""
        ])

    print("DG容量(kW) 与 系统总风险及详细风险参数 数据如下：")
    print(table)

    # 绘制折线图
    fig, axs = plt.subplots(3, 2, figsize=(14, 12))
    axs = axs.flatten()

    axs[0].plot(capacities, risks, marker='o', linestyle='-', color='r')
    axs[0].set_title('系统总风险')
    axs[0].set_xlabel('DG 单机容量 (kW)')
    axs[0].set_ylabel('系统总风险')

    axs[1].plot(capacities, failure_probability, marker='s', linestyle='--', color='b')
    axs[1].set_title('失效概率')
    axs[1].set_xlabel('DG 单机容量 (kW)')
    axs[1].set_ylabel('失效概率')

    axs[2].plot(capacities, load_loss_consequence, marker='^', linestyle='-.', color='g')
    axs[2].set_title('失负荷后果')
    axs[2].set_xlabel('DG 单机容量 (kW)')
    axs[2].set_ylabel('失负荷后果')

    axs[3].plot(capacities, load_loss_risk, marker='v', linestyle=':', color='c')
    axs[3].set_title('失负荷风险')
    axs[3].set_xlabel('DG 单机容量 (kW)')
    axs[3].set_ylabel('失负荷风险')

    axs[4].plot(capacities, overload_probability, marker='d', linestyle='-', color='m')
    axs[4].set_title('过载概率')
    axs[4].set_xlabel('DG 单机容量 (kW)')
    axs[4].set_ylabel('过载概率')

    axs[5].plot(capacities, overload_consequence, marker='x', linestyle='--', color='y')
    axs[5].set_title('过载后果')
    axs[5].set_xlabel('DG 单机容量 (kW)')
    axs[5].set_ylabel('过载后果')

    for ax in axs:
        ax.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()
    plt.xlabel("DG 单机容量 (kW)")
    plt.ylabel("系统总风险")
    plt.title("问题2：DG 容量 vs 系统风险")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level="ERROR") 
    problem2()