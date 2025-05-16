# 深圳杯C题 utils 工具包使用说明

## 文件夹结构

```
深圳杯C题/
├── analysis.ipynb           # 分析用Jupyter笔记本
├── code2.py                 # 主要算法代码
├── data_analyser.ipynb      # 数据分析笔记本
├── data_loder.py            # 数据加载脚本
├── problem1.py~4.py         # 各子问题求解脚本
├── usage_doc.md             # 本使用说明文档
├── usage.ipynb              # 使用演示笔记本
├── data_file/               # 数据文件夹
│   ├── edges_info.json      # 边信息数据
│   └── nodes_info.json      # 节点信息数据
├── doc/                     # 题目与资料
│   ├── 题目.md
│   ├── C题：分布式能源接入配电网的风险分析.docx
│   └── C题附件：有源配电网62节点系统基本参数.xlsx
├── image.png                # 图片
└── utils/                   # 工具包
    ├── __init__.py
    ├── data_loder.py        # 数据加载模块
    ├── doc.md               # 工具包说明
    ├── RiskAnalyzer.py      # 风险分析模块
    └── tool.py              # 图结构与分析工具
```

## 主要文件内容说明
- `utils/`：核心工具包，包含图结构、风险分析、数据加载等模块。
- `data_file/`：存放原始数据（节点、边信息）。
- `problem*.py`：各子问题的求解脚本。
- `usage_doc.md`、`usage.ipynb`：工具包使用说明与演示。
- `doc/`：题目描述、附件和相关资料。

## 1. utils.tool

- 提供 `UndirectedGraph` 类，支持无向图的节点、边管理、属性统计、可视化、路径查找、批量操作等。
- 典型用法：

```python
from utils.tool import UndirectedGraph

graph = UndirectedGraph(nodes_info, edges_info)
graph.visualize()
print(graph.get_node_degree(1))
```

## 2. utils.RiskAnalyzer

- 提供 `RiskAnalyzer` 类，用于电力网络的风险分析，包括最大流、失负荷风险、过载风险等。
- 典型用法：

```python
from utils.RiskAnalyzer import RiskAnalyzer

analyzer = RiskAnalyzer(nodes_info, edges_info)
print(analyzer.capacity(1, 2))
print(analyzer.load_loss_risk((1, 2)))
```

## 3. utils.data_loder

- 提供数据加载脚本，自动读取 `data_file` 文件夹下的 `edges_info.json` 和 `nodes_info.json`。
- 典型用法：

```python
from utils import data_loder
print(data_loder.nodes_info)
print(data_loder.edges_info)
```

## 4. 文档与帮助

- 更详细的API文档请见 [build/html/modules.html](../build/html/modules.html) 或 [build/html/utils.html](../build/html/utils.html)，可用浏览器直接点击打开。
- 如需进一步帮助，建议先查阅上述HTML文档，或联系开发者。

---

> 文档自动生成，最后更新：2025-05-16
