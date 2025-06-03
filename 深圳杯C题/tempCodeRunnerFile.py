    # 构建DataFrame
    data = []
    for cap, result in zip(capacities, details):
        data.append({
            "容量(kW)": cap,
            "系统总风险": result['total_risk'],
            "失效概率": result.get('failure_probability', None),
            "失负荷后果": result.get('load_loss_consequence', None),
            "失负荷风险": result.get('load_loss_risk', None),
            "过载概率": result.get('overload_probability', None),
            "过载后果": result.get('overload_consequence', None)
        })
    df = pd.DataFrame(data)
    pd.set_option('display.float_format', '{:.6f}'.format)
    print("DG容量(kW) 与 系统总风险及详细风险参数 数据如下：")
    print(df)