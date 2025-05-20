from utils.RiskAnalyzer import RiskAnalyzer
from utils.tool import *
from utils.data_loder import edges_info, nodes_info
from tabulate import tabulate
from loguru import logger
import argparse
import ast
import sys


@logger.catch
def problem1(print_entire_graph=False, instances=None, print_logs=True):
    """问题1：验证一条线路的失负荷与过负荷风险"""
    # nodes, edges = load_data(limit=10)  # 测试用小规模数据
    # grid = PowerGridGraph(nodes, edges)
    analyzer = RiskAnalyzer(nodes_info, edges_info)

    # 默认测试线路
    default_lines = [
        (13, 43),
        (3, 4)
    ]

    # 根据参数选择要分析的线路
    lines_to_analyze = edges_info if print_entire_graph else (instances if instances else default_lines)

    # 配置日志记录
    if not print_logs:
        logger.remove()
        logger.add(lambda _: None)  # 禁用日志输出

    result = []
    for line_info in lines_to_analyze:
        # 计算失负荷和过负荷风险
        if print_entire_graph:
            line = list(line_info.keys())[0]
        else:
            line = line_info

        risk_loss = analyzer.load_loss_risk(line)
        risk_over = analyzer.overload_risk(line)

        if risk_loss < 0:
            result.append((line, 'error', risk_over))
            logger.error(f"{line} cannot calculate load loss risk correctly")
        if risk_over < 0:
            result.append((line, risk_loss, 'error'))
            logger.error(f"{line} cannot calculate overload risk correctly")
        else:
            result.append((line, risk_loss, risk_over))

    # 打印结果
    headers = ["线路", "失负荷风险", "过负荷风险"]
    table = []
    for line, risk_loss, risk_over in result:
        table.append([line, risk_loss, risk_over])
    print(tabulate(table, headers, tablefmt="github"))


def parse_tuple(s):
    """将字符串格式的元组解析为实际元组"""
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        raise argparse.ArgumentTypeError(f"Invalid tuple format: {s}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="电网风险分析工具")
    parser.add_argument("--print_entire_graph", type=lambda x: x.lower() == 'true',
                        default=False, help="是否分析全部节点 (True/False)")
    parser.add_argument("--instances", type=parse_tuple, nargs='+',
                        help="指定要分析的线路，格式为(node1,node2)，可指定多条")
    parser.add_argument("--print_logs", type=lambda x: x.lower() == 'true',
                        default=True, help="是否打印日志 (True/False)")

    args = parser.parse_args()

    problem1(
        print_entire_graph=args.print_entire_graph,
        instances=args.instances,
        print_logs=args.print_logs
    )