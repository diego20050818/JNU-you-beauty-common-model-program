from utils.RiskAnalyzer import RiskAnalyzer
from utils.data_loder import edges_info, nodes_info

def problem1():
    """问题1：验证一条线路的失负荷与过负荷风险"""
    #nodes, edges = load_data(limit=10)  # 测试用小规模数据
    #grid = PowerGridGraph(nodes, edges)
    analyzer = RiskAnalyzer(nodes_info, edges_info)

    line = (4, 5)
    risk_loss = analyzer.load_loss_risk(line)
    risk_over = analyzer.overload_risk(line)

    print(f"线路 {line} 风险评估：失负荷 = {risk_loss:.2f}，过负荷 = {risk_over:.2f}")

if __name__ == "__main__":
    problem1()