from utils.RiskAnalyzer import RiskAnalyzer
from utils.tool import *
from utils.data_loder import edges_info, nodes_info
from tabulate import tabulate


def problem1():
    """问题1：验证一条线路的失负荷与过负荷风险"""
    #nodes, edges = load_data(limit=10)  # 测试用小规模数据
    #grid = PowerGridGraph(nodes, edges)
    analyzer = RiskAnalyzer(nodes_info, edges_info)

    # 添加多条线路，节点范围1-62
    
    lines = [
        (4, 5),
        (1, 2),
        (10, 11),
        (20, 21),
        (30, 31),
        (40, 41),
        (50, 51),
        (60, 61),
        (15, 16),
        (25, 26),
        (23,62)
    ]
    
    result = []
    for line_info in edges_info:
        # 计算失负荷和过负荷风险
        line = list(line_info.keys())[0]
        
        risk_loss = analyzer.load_loss_risk(line)
        risk_over = analyzer.overload_risk(line)

        if risk_loss < 0:
            result.append((line, 'error',risk_over))
            logger.error(f"{line} cannot calculate load loss risk currectly")
        if risk_over < 0:
            result.append((line, risk_loss,'error'))
            logger.error(f"{line} cannot calculate overload risk currectly")
        else:
            result.append((line, risk_loss, risk_over))

    # 打印结果
    headers = ["线路", "失负荷风险", "过负荷风险"]
    table = []
    for line, risk_loss, risk_over in result:
        table.append([line, risk_loss, risk_over])
    print(tabulate(table, headers, tablefmt="github"))
    #print(f"线路 {line} 风险评估：失负荷 = {risk_loss:.2f}，过负荷 = {risk_over:.2f}")


if __name__ == "__main__":
    problem1()