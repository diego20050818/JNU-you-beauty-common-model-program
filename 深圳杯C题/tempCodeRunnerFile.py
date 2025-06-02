def problem1(print_entire_graph=False, instances=None, print_logs=True):
    """问题1：验证一条线路的失负荷与过负荷风险"""
    try:
        # 创建分析器实例
        analyzer = RiskAnalyzer(nodes_info=nodes_info, edges_info=edges_info)

        # 配置日志记录
        if not print_logs:
            logger.remove()
            logger.add(lambda _: None)  # 禁用日志输出

        print("开始电网风险分析...")

        # 默认测试线路
        default_lines = [
            (13, 43),
            (3, 4)
        ]

        # 根据参数选择要分析的线路
        lines_to_analyze = edges_info if print_entire_graph else (instances if instances else default_lines)

        result = []
        for line_info in lines_to_analyze:
            if print_entire_graph:
                line = list(line_info.keys())[0]
            else:
                line = line_info

            try:
                # 基础计算
                edge_risk = analyzer.edge_risk(*line)
                capacity = analyzer.calculate_capacity(*line)
                current = analyzer.I_ij(*line)
                risk_loss = analyzer.load_loss_risk(line)
                risk_over = analyzer.overload_risk(line)
                result.append((line, edge_risk, capacity, current, risk_loss, risk_over))
            except Exception as e:
                logger.error(f"{line} 分析异常: {e}")
                result.append((line, 'error', 'error', 'error', 'error', 'error'))

        # 打印结果
        headers = ["线路", "edge_risk", "capacity", "current", "失负荷风险", "过负荷风险"]
        table = []
        for row in result:
            table.append(list(row))
        print(tabulate(table, headers, tablefmt="github"))
        analyzer.print_analysis_summary()
    except Exception as e:
        logger.error(e)