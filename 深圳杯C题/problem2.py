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

step = 50

def problem2():
    """问题2：分析 DG 容量从 300 至 900kW 的风险演变曲线，并绘制每个风险参数的导数变化线"""
    capacities = np.arange(300, 901,step)
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

    # ====== 可配置的参数列表 ======
    # 在这里修改需要显示的参数，格式：(参数名称, 数据数组, 主曲线颜色, 导数曲线颜色)
    plot_params = [
        ('系统总风险', risks, '#545969', '#FF0000'),
        ('失效概率', failure_probability, '#A4757D', '#FF7F0E'),
        ('失负荷后果', load_loss_consequence, '#E7987C', '#2CA02C'),
        ('失负荷风险', load_loss_risk, '#8B91B6', '#1F77B4'),
        ('过载概率', overload_probability, '#7771A4', '#9467BD'),
        ('过载后果', overload_consequence, '#C0C0C0', '#8C564B'),
    ]
    
    # 计算子图布局
    n_params = len(plot_params)
    n_cols = 2  # 每行显示2个参数（原始值和导数各一个子图）
    n_rows = n_params  # 每个参数占一行
    
    # 创建子图
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 4*n_rows))
    fig.suptitle("问题2：DG 容量变化下的系统风险及导数演变", fontsize=16, fontweight='bold')
    
    # 如果只有一个参数，确保axes是二维数组
    if n_params == 1:
        axes = axes.reshape(1, -1)
    
    # 绘制每个参数的原始值和导数
    for i, (param_name, data, main_color, diff_color) in enumerate(plot_params):
        # 计算导数（差分）
        data_diff = np.gradient(data)
        
        # 左侧子图：原始值
        ax_main = axes[i, 0]
        ax_main.plot(capacities, data, linestyle='-', color=main_color, linewidth=2, markersize=4)
        # 在图像内部左下角添加标题
        """         ax_main.text(
            0.02, 0.02, f"{param_name}",
            transform=ax_main.transAxes,
            fontsize=13, fontweight='bold',
            va='bottom', ha='left',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2')
        ) """
        ax_main.set_xlabel('DG 单机容量 (kW)', fontsize=10)
        ax_main.set_ylabel(f'{param_name}值', fontsize=10)
        ax_main.grid(True, linestyle='--', alpha=0.6)
        ax_main.tick_params(axis='both', which='major', labelsize=8)
        
        # 右侧子图：导数
        ax_diff = axes[i, 1]
        ax_diff.plot(capacities, data_diff, linestyle='--', color=diff_color, linewidth=2, markersize=4)
        # 在图像内部左下角添加标题
        """        ax_diff.text(
            0.02, 0.02, f"{param_name}导数（变化率）",
            transform=ax_diff.transAxes,
            fontsize=13, fontweight='bold',
            va='bottom', ha='left',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2')
        ) """
        ax_diff.set_xlabel('DG 单机容量 (kW)', fontsize=10)
        ax_diff.set_ylabel(f'{param_name}变化率', fontsize=10)
        ax_diff.grid(True, linestyle='--', alpha=0.6)
        ax_diff.tick_params(axis='both', which='major', labelsize=8)
        
        # 在导数图上添加零点线
        ax_diff.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


def problem2_compact():
    """问题2的紧凑版本：只显示选定的几个重要参数"""
    capacities = np.arange(300, 901, step)
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
    plt.rcParams['font.size'] = 10

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

    # ====== 紧凑版本的参数配置 ======
    # 只显示最重要的几个参数
    plot_params = [
        ('系统总风险', risks, '#545969', '#FF0000'),
        ('过载后果', overload_consequence, '#8B91B6', '#1F77B4'),
    ]
    
    # 创建2x2的子图布局
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("问题2：DG 容量变化下的关键风险参数演变", fontsize=16, fontweight='bold')
    
    # 绘制选定参数
    for i, (param_name, data, main_color, diff_color) in enumerate(plot_params):
        data_diff = np.gradient(data)
        
        # 原始值（左列）
        ax_main = axes[i, 0]
        ax_main.plot(capacities, data, linestyle='-', color=main_color, linewidth=2.5, markersize=1)
        ax_main.set_title(f"{param_name}", fontsize=14, fontweight='bold')
        ax_main.set_xlabel('DG 单机容量 (kW)', fontsize=12)
        ax_main.set_ylabel(f'{param_name}值', fontsize=12)
        ax_main.grid(True, linestyle='--', alpha=0.6)
        
        # 导数（右列）
        ax_diff = axes[i, 1]
        ax_diff.plot(capacities, data_diff, linestyle='--', color=diff_color, linewidth=2.5, markersize=1)
        ax_diff.set_title(f"{param_name}变化率", fontsize=14, fontweight='bold')
        ax_diff.set_xlabel('DG 单机容量 (kW)', fontsize=12)
        ax_diff.set_ylabel(f'{param_name}变化率', fontsize=12)
        ax_diff.grid(True, linestyle='--', alpha=0.6)
        ax_diff.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level="ERROR") 
    
    # 选择运行哪个版本
    print("选择运行版本：")
    print("1. 完整版本（显示所有参数）")
    print("2. 紧凑版本（显示关键参数）")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "2":
        problem2_compact()
    else:
        problem2()