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
    capacities = np.arange(300, 901,10)
    risks = []
    details = []
    failure_probability = []
    load_loss_consequence = []
    load_loss_risk = []
    overload_probability = []
    overload_consequence = []

    # 设置中文和图像风格
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 8

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

    # 构建表格展示数据
    table = PrettyTable()
    table.field_names = [
        "容量(kW)", "系统总风险", "失效概率", "失负荷后果", "失负荷风险", "过载概率", "过载后果"
    ]
    for cap, result in zip(capacities, details):
        table.add_row([
            cap,
            f"{result['total_risk']:.6f}",
            f"{result.get('failure_probability', 0):.6f}",
            f"{result.get('load_loss_consequence', 0):.6f}",
            f"{result.get('load_loss_risk', 0):.6f}",
            f"{result.get('overload_probability', 0):.6f}",
            f"{result.get('overload_consequence', 0):.6f}"
        ])

    print("DG容量(kW) 与 系统总风险及详细风险参数 数据如下：")
    print(table)

    # 绘图部分
    fig, axs = plt.subplots(3, 2, figsize=(14, 12))
    axs = axs.flatten()

    # 自定义配色（RGB -> HEX）
    colors = ['#545969', '#A4757D', '#E7987C', '#8B91B6', '#7771A4', '#C0C0C0']
    titles = ['系统总风险', '失效概率', '失负荷后果', '失负荷风险', '过载概率', '过载后果']
    ylabels = ['系统总风险', '失效概率', '失负荷后果', '失负荷风险', '过载概率', '过载后果']
    data_series = [
        risks,
        failure_probability,
        load_loss_consequence,
        load_loss_risk,
        overload_probability,
        overload_consequence
    ]

    for i in range(6):
        axs[i].plot(
            capacities,
            data_series[i],
            marker='o',
            linestyle='-',
            color=colors[i],
            linewidth=2,
            label=titles[i]
        )
        axs[i].set_title(titles[i], fontsize=8, fontweight='bold')
        axs[i].set_xlabel('DG 单机容量 (kW)', fontsize=8)
        axs[i].set_ylabel(ylabels[i], fontsize=8)
        axs[i].grid(True, linestyle='--', alpha=0.6)
        axs[i].legend()
        # 在节点上显示数字
        for x, y in zip(capacities, data_series[i]):
            axs[i].text(x, y, f"{y:.2f}", fontsize=6, ha='center', va='bottom', rotation=45)

    plt.suptitle("问题2：DG 容量变化下的系统风险演变", fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()



if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level="ERROR") 
    problem2()