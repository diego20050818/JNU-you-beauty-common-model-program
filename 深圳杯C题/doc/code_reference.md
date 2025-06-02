下面给出更加深入、逐行分析 `RiskAnalyzer.py` 中各方法的实现原理与参数来源，并结合数学模型和代码细节展开说明。报告分为以下几部分：

1. 模块与数据结构
2. 初始化与参数设置
3. 潮流分析与电流计算
4. 最大流算法实现
5. 故障概率与失负荷风险计算
6. 过载风险计算
7. 综合风险指标与关键线路识别
8. 总结与可拓展方向


---

## 一、模块与数据结构

### 1.1 文件说明与依赖关系

```python
# 文件开头的注释（版本2025年6月2日）
"""
RiskAnalyzer.py
改进版电网风险分析模块
...
"""
```

* 该模块的版本标注在“2025年6月2日”，正好与你报告撰写的时间一致。
* 依赖了若干外部包：`pandas, numpy, matplotlib, collections, json, copy, typing, loguru`，以及自定义工具模块 `utils.tool`、`utils.data_loder`。
* `utils.data_loder` 中提供了 `nodes_info`、`edges_info` 两个全局变量，分别存储节点信息和线路信息；`utils.tool` 中的 `UndirectedGraph` 类封装了图操作（邻居查询、属性获取等）。

我们先明确一下“输入数据”的格式与含义：

* **nodes\_info**：一个字典，示例格式（来源于 `utils.data_loder`）：

  ```python
  {
      "1": {"type": "变电站", "power": 0, "DG": False, "which_substation": None},
      "2": {"type": "居民",   "power": 50, "DG": False, "which_substation": "CB1"},
      "3": {"type": "商业",   "power": 120, "DG": True, "which_substation": "CB2"},
      ...
  }
  ```

  * **键**：节点 ID（字符串形式）；
  * **value**：一个包含多个字段的字典：

    * `type`：节点类型（居民/商业/政府和机构/办公和建筑等）；
    * `power`：该节点的有功负荷需求，单位为 kW；
    * `DG`：是否接入分布式能源（Distributed Generation），布尔值；
    * `which_substation`：该节点所属的变电站编号（如“CB1”），用于潮流分析。

* **edges\_info**：一个列表，列表中每个元素也是一个字典，形如：

  ```python
  [
      { (1, 2): {"length": 3.5, "type": "馈线", "分段开关": "SW12", "联络开关": "", "Resistor": 0.1, "Reactance": 0.05} },
      { (2, 3): {"length": 2.1, "type": "馈线", "分段开关": None, "联络开关": "LC23", "Resistor": 0.08, "Reactance": 0.04} },
      ...
  ]
  ```

  * **键**：一个二元元组 `(begin, end)`，表示线路两端的节点 ID（整数）；
  * **value**：该条线路的属性：

    * `length`：线路长度，单位通常为 km；
    * `type`：线路类型（如“馈线”或“馈线间联络线”）；
    * `分段开关`、`联络开关`：字符串，若存在开关则填写相应编号，否则为 `None` 或空字符串；
    * `Resistor`、`Reactance`：电阻和电抗，单位为 Ω（欧姆）。

**UndirectedGraph** 类将上述输入封装为无向图结构，常见方法包括 `.neighbors(node_id)`, `.get_edge_attribute(u, v, attr_name)`, `.get_node_attribute(node_id, attr_name)` 等。我们后续调用时，将依赖它来遍历邻居、读取线路属性或节点属性。

---

## 二、初始化与参数设置

```python
class RiskAnalyzer:
    def __init__(self, nodes_info: Dict[str, Dict], edges_info: List[Dict[Tuple, Dict]], rated_current: float = 220.0):
        # 基础数据初始化
        self._nodes_info = nodes_info.copy()
        self._edges_info = edges_info.copy()
        self._graph = UndirectedGraph(self._nodes_info, self._edges_info)
        self._rated_current = rated_current
```

### 2.1 深入解析 `__init__`

1. **浅拷贝输入数据**

   * `nodes_info.copy()` 和 `edges_info.copy()`：防止在后续计算中意外修改外部传入的原始数据。
   * 注：这里是浅拷贝，如果后续需要对嵌套字典做深度更改，应谨慎。但当前代码中，节点与线路属性仅读取，不会对原字典做深度赋值。

2. **构造图对象**

   * `self._graph = UndirectedGraph(self._nodes_info, self._edges_info)`
   * 假设 `UndirectedGraph` 内部会把每个键 `(u, v)` 加入邻接表，同时保存每条边的属性字典，方便后续调用 `get_edge_attribute(u, v, attr)`、`neighbors(u)` 等。
   * 这种做法将图的逻辑与风险计算逻辑分离，利于模块化和单元测试：若要替换图的实现，只要满足相同接口即能无缝对接。

3. **额定电流 `rated_current`**

   * 默认值 `220.0` A，代表配电网中常见的 10kV 线路的**额定电流限值**。2025年已有许多城市配电网的馈线评级约为 200–250 A，因此取值合情合理。
   * 后续在过载判断中，用到 1.1 倍该值作为“过载阈值”——留有 10% 安全裕度。

4. **用户类型波动权重与危害度权重**

   ```python
   # 用户类型负荷波动权重（用于考虑用户类型对实际负荷波动的估计）
   self._user_weights = {
       "居民": 0.05,
       "商业": 0.12,
       "政府和机构": 0.10,
       "办公和建筑": 0.08
   }
   # 用户类型危害度权重（用于计算失负荷与过载危害度时的加权系数）
   self._damage_weights = {
       "居民": 1.0,
       "商业": 2.5,
       "政府和机构": 3.0,
       "办公和建筑": 2.5
   }
   ```

   * **来源猜测**：

     * 这些参数一般由电力公司或电网规划部门通过历史数据统计、专家打分或实地调研得到。例如：

       * 居民用电对社会影响较小，给出较低的权重；
       * 政府和机构、商业负荷一旦中断，造成的经济与社会损失更大，因此分配更高的危害度权重。
   * **后续用法**：

     * 在失负荷危害度 $C_{LL}$ 计算时，每个节点的“荷损后果”会乘以对应的 `damage_weights[node_type]`；
     * 在过载危害度 $C_{OL}$ 计算时，取过载线路两端节点权重的平均值作为该线路的权重因子。

5. **故障率参数**

   ```python
   self.node_risk = 0.005              # 每个用户节点的故障率
   self.dg_risk = 0.005                # 每个分布式能源（DG）的故障概率
   self.switch_risk = 0.002            # 每个开关的故障率
   self.edge_each_length_risk = 0.002  # 配电线路单位长度故障率 (per km)
   ```

   * **含义**：

     * `node_risk=0.005`：假设每个普通节点（非DG）的单次事故概率为 0.5%；
     * `dg_risk=0.005`：每个分布式能源装置的故障概率同样取 0.5%；
     * `switch_risk=0.002`：每个分段开关或联络开关的故障概率取 0.2%；
     * `edge_each_length_risk=0.002`：线路每公里发生故障的概率为 0.2%。
   * **数据来源猜测**：此类参数往往基于电网历史运行统计：例如每年每公里平均故障次数、断路器跳闸概率等归一化得到。这里只给了一个统一水平，但在实际应用中可根据不同线路虚拟环境、气候、维护周期进行差异化设定。

6. **电网基础参数**

   ```python
   self.feeder_capacity = 2200         # 馈线额定容量 (kW)，对应 10kV、220A 时的理论极限 P = √3·U·I≈ 3807kVA，大约取 2200kW 作下限
   self.feeder_current_limit = 220     # 馈线额定电流 (A)
   self.voltage = 10e3                 # 电压等级 (V) - 10 kV
   self.dg_capacity = 3e2              # 分布式能源容量 (kW) - 300 kW
   self.cos = 0.9                      # 功率因数，一般取 0.9
   ```

   * **关系**：

     * 10kV、220A，若按 $P = \sqrt{3} U I \cos\phi$ 计算：

       $$
       P_{\max} = \sqrt{3} \times 10\,\text{kV} \times 220\,\text{A} \times 0.9 \approx 3430\,\text{kW}
       $$

       但为了留有余量，代码中将馈线容量定为 2200 kW 左右，用来约束单条线路的最大可输送功率。
   * 未来如果换成 35kV 线路或 110kV，`voltage` 这个参数能灵活调整。

7. **变电站映射**

   ```python
   self._substation_map = {
       "CB1": '1',
       "CB2": '2', 
       "CB3": '3'
   }
   ```

   * 在最大流算法中，输入源点一般写“CB1”，此处映射为节点 ID `'1'`。这种做法方便调用者以“变电站代码”描述网络。
   * 假设在 `nodes_info` 中，节点 ID 1、2、3 正好对应三个变电站。

8. **缓存机制**

   ```python
   self._power_flow_cache = {}
   ```

   * 用于缓存潮流计算结果，避免重复多次计算。由于潮流计算（基于最短路径搜索）相对耗时，有了缓存后，一旦调用过 `calculate_power_flow_simple()`，后续再次调用直接返回上次结果。

9. **初始化边—用户类型映射**

   ```python
   self._initialize_edge_user_types()
   ```

   * 该函数遍历每条边 `(u, v)`，查看两端节点的 `type`，将其收集到 `self.edge_user_types[(u,v)] = {type_u, type_v}`。
   * 在后续计算中，若要对某条线路所连用户类型进行统计、加权或筛选，就可以直接从 `edge_user_types` 中获取节点类型集合。

初始化结束后，`RiskAnalyzer` 的内部状态已准备就绪，接下来各种方法将基于以上参数进行计算。

---

## 三、潮流分析与电流计算

### 3.1 最短路径搜索：`_find_shortest_path_to_substation`

这一方法用于“从某个节点出发，找到距离最近的变电站”的最短路径（按线路长度累加）。

```python
def _find_shortest_path_to_substation(self, start_node: str) -> Tuple[Optional[List[str]], float]:
    # 变电站列表
    substations = ['1', '2', '3']
    ...
    queue = deque([(start_node, [start_node], 0.0)])
    visited = set()
    while queue:
        current, path, distance = queue.popleft()
        ...
        if current in substations:
            return path, distance
        for neighbor in self._graph.neighbors(int(current)):
            neighbor_str = str(neighbor)
            if neighbor_str not in visited:
                edge_length = self._graph.get_edge_attribute(int(current), neighbor, 'length')
                new_path = path + [neighbor_str]
                new_distance = distance + edge_length
                queue.append((neighbor_str, new_path, new_distance))
    return None, float('inf')
```

#### 数学模型

* 该方法本质是**无权图的 BFS + 累加边长度**，寻找节点到任意一个变电站的“最短路径”。
* 如果图较大，BFS 的空间复杂度与节点数成正比；最坏情况下需要把所有分支都走一遍，但这里多源 BFS（3 个变电站）合并于一次遍历中，效率较高。

#### 代码细节

1. **输入参数**

   * `start_node`: 字符串类型，如 `"5"`；
   * 先检查 `start_node` 是否本身就是变电站，如果是就直接返回 `[start_node], 0.0`。

2. **队列元素设计**

   * 队列中每个元素为 `(current_node, path_list, distance_sum)`，其中 `path_list` 是到当前节点的路径（以字符串列表形式存储），`distance_sum` 为累计长度。
   * `visited` 集合防止回路。

3. **邻居遍历**

   * `self._graph.neighbors(int(current))` 返回一个整数列表，需要转为字符串比较。
   * `edge_length` 通过 `self._graph.get_edge_attribute(u, v, 'length')` 获取，保证了动态读取线路属性。

4. **返回值**

   * 若找到第一个变电站，就返回当前 `path` 与 `distance`；否则队列耗尽，返回 `(None, ∞)`。

### 3.2 简化潮流计算：`calculate_power_flow_simple`

```python
def calculate_power_flow_simple(self) -> Dict[Tuple[int, int], float]:
    if self._power_flow_cache:
        return self._power_flow_cache
    
    edge_powers = defaultdict(float)
    for node_id, node_info in self._nodes_info.items():
        power_demand = node_info.get('power', 0)
        if power_demand > 0:
            path, min_distance = self._find_shortest_path_to_substation(node_id)
            if path and len(path) > 1:
                for i in range(len(path) - 1):
                    edge_key = self._get_edge_key(int(path[i]), int(path[i+1]))
                    edge_powers[edge_key] += power_demand
            else:
                logger.warning(f"节点{node_id}无法找到到变电站的路径")
    self._power_flow_cache = dict(edge_powers)
    return self._power_flow_cache
```

#### 数学模型与假设

1. **近似思想**：

   * 假设每个有功负荷点 $i$ 的负荷需求 $P_i$（kW）直接从“最近变电站”一路输送过来，不考虑电压降、节点注入、潮流分支比率等复杂因素。
   * 换句话说，如果节点 5 要 100 kW，它一定选择从距离最近的变电站，例如经过路径 2→3→5，把 100 kW 累加到每条经过的边上。

2. **数学表示**：

   * 对节点 $i$，令最近变电站集合 $\mathcal{S}=\{s_1,s_2,s_3\}$，最短路径为 $i \rightarrow v_1 \rightarrow v_2 \rightarrow \dots \rightarrow s_k$，令该路径上第 $j$ 条边为 $(v_{j-1}, v_j)$。
   * 则在这条路径上每条边的功率 $P_{v_{j-1},v_j} $ 增加 $P_i$。
   * 最终得到一个累加后的功率分布：

     $$
       P_{edge}(u,v) \;=\; \sum_{\{ i \mid (u,v) \in \text{shortestPath}(i \to \text{nearestSubstation}) \}} P_i.
     $$

#### 代码实现亮点

1. **缓存机制**

   * `if self._power_flow_cache: return self._power_flow_cache`：若之前已经计算过并且中间没有修改节点功率、拓扑等，则直接复用结果。
   * 减少了在后续多次调用电流计算函数 `I_ij` 时重复计算开销。

2. **路径求取与功率累加**

   * 先判断 `power_demand > 0`，过滤掉没有负荷的节点（如变电站、纯 DG 节点可能为零负荷）。
   * `path` 为字符串形式的节点列表，先转为整数再构造标准化边键：

     ```python
     edge_key = self._get_edge_key(int(path[i]), int(path[i+1]))
     ```

     其中 `_get_edge_key` 保证 `(u,v)` 总是按照 `(min, max)` 的顺序，从而把 `(2,5)` 和 `(5,2)` 识别为同一条边。
   * 每次累加 `edge_powers[edge_key] += power_demand`。

3. **可扩展性**

   * 如果未来需要考虑更精细的潮流（如基于牛顿-拉夫森法或快速分布式潮流），只需在此函数基础上替换 `calculate_power_flow_simple`，其他依赖 `I_ij`、`P_ol_all` 的方法调用不变。

### 3.3 电流计算：`I_ij`

此函数基于上述潮流结果计算“线路实际电流”（单位 A）：

```python
def I_ij(self, begin: int, end: int) -> float:
    edge_powers = self.calculate_power_flow_simple()
    edge_key = self._get_edge_key(begin, end)
    line_power = edge_powers.get(edge_key, 0.0)  # kW
    if line_power <= 0:
        return 0.0
    voltage_kv = self.voltage / 1000  # 转换为 kV，即10kV->10
    current = line_power / (np.sqrt(3) * voltage_kv * self.cos)  # A
    return current
```

#### 数学推导

* 线路上某条边 $(i,j)$ 的累积功率负载为 $P_{ij}$ kW。
* 若线路为三相交流，定标电压为 $U = 10\,\text{kV}$，功率因数 $\cos\phi = 0.9$，则电流计算公式：

  $$
    I_{ij} \;=\; \frac{P_{ij}}{\sqrt{3}\,U\,\cos\phi}.
  $$

  * 这里的 $U$ 需换算成 kV 参与公式。
  * 例如：若某边 P=500 kW，则

    $$
      I = \frac{500}{\sqrt{3} \times 10 \times 0.9} \approx 32.0\,\text{A}.
    $$

#### 代码逐行解释

1. **调用潮流结果**

   * `edge_powers = self.calculate_power_flow_simple()`：先获取所有边的功率分布。

2. **获取当前边的功率**

   * `edge_key = self._get_edge_key(begin, end)` 标准化元组。
   * `line_power = edge_powers.get(edge_key, 0.0)`：若该边未被任何负荷路径覆盖，则为 0。

3. **过滤无功率**

   * 若 `line_power <= 0`，直接返回 0 A，避免除零或负值干扰。

4. **换算并计算电流**

   * `voltage_kv = self.voltage / 1000`：把 `10e3` V（即 10000 V）换算为 10 kV。
   * `current = line_power / (np.sqrt(3) * voltage_kv * self.cos)`：得到 A 值。

5. **异常处理**

   * 整个函数包裹在 `try/except` 中，一旦出现异常（如字典 KeyError、类型错误等），不会抛出，而是记录日志并返回 0.0。

---

## 四、最大流算法实现

### 4.1 计算线路容量：`calculate_capacity`

```python
def calculate_capacity(self, begin: int, end: int) -> float:
    R = self._graph.get_edge_attribute(begin, end, 'Resistor')
    X = self._graph.get_edge_attribute(begin, end, 'Reactance')
    Z = complex(R, X)
    Z_abs = np.abs(Z)
    if Z_abs == 0:
        return self.feeder_capacity
    capacity = np.square(self.voltage) / Z_abs * self.cos / 1000  # kW
    return min(capacity, self.feeder_capacity)
```

#### 数学原理

* 对于一条输电线路，其阻抗 $Z = R + jX$，阻抗模长 $\lvert Z \rvert = \sqrt{R^2 + X^2}$。
* 在忽略电压降、视在功率限制的粗略估算下，可以用简单公式：

  $$
    P_{\max} \approx \frac{U^2}{|Z|} \cos\phi,
  $$

  其中：

  * $U$：线电压，10 kV；
  * $\cos\phi$：功率因数，0.9；
  * 单位换算：$\frac{U^2}{Z}$ 的结果为 VA（视在功率），除以 1000 转为 kW。
* 同时限制在 `feeder_capacity`（2200 kW）以内，不超过馈线设计容量。

#### 代码实现要点

1. **从图结构中读取 R、X**

   * `R = self._graph.get_edge_attribute(begin, end, 'Resistor')`；
   * `X = self._graph.get_edge_attribute(begin, end, 'Reactance')`；
   * 注意：可能某些边的 R、X 未配置，若返回 `None`，整个计算会抛异常， 由外层 `try/except` 捕获并返回 0.0。

2. **阻抗模长**

   * `Z = complex(R, X)` 构造复数；
   * `Z_abs = np.abs(Z)` 计算 $\sqrt{R^2 + X^2}$。

3. **零阻抗特殊处理**

   * 若 `Z_abs == 0`（理论上不太可能，但若出现缺省或异常数据），日志警告后直接返回最大 `feeder_capacity`。

4. **容量公式**

   * `np.square(self.voltage)` 计算 $U^2$，
   * 整个分子为 $\,U^2 \cdot \cos\phi$，再除以 `Z_abs`、再除以 1000。

5. **上限约束**

   * 最后 `return min(capacity, self.feeder_capacity)`：防止计算值超过馈线设计值。

### 4.2 Edmonds-Karp 实现：`edmons_krap`

```python
def edmons_krap(self, source: str, sink: str, use_tie: Tuple = (0, 0)) -> float:
    source = self._substation_map.get(source, source)
    sink = self._substation_map.get(sink, sink)
    if source == sink: return 0.0

    # 构造残余网络容量字典
    residual_capacity = {}
    for edge in self._edges_info:
        (begin, end), edge_info = list(edge.items())[0]
        capacity = self.calculate_capacity(begin, end)
        residual_capacity[(begin, end)] = capacity
        residual_capacity[(end, begin)] = capacity  # 无向图 => 双向容量相同

    def bfs_find_path() -> Optional[List[str]]:
        parents = {}
        visited = set([source])
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in self._graph.neighbors(int(u)):
                v_str = str(v)
                if v_str not in visited and residual_capacity.get((int(u), v), 0) > 0:
                    # 联络线使用策略
                    if (use_tie == (0, 0) and 
                        self._graph.get_edge_attribute(int(u), v, "type") == "馈线间联络线"):
                        continue
                    parents[v_str] = u
                    visited.add(v_str)
                    queue.append(v_str)
                    if v_str == sink:
                        # 重构路径
                        path = []
                        curr = sink
                        while curr is not None:
                            path.append(curr)
                            curr = parents.get(curr)
                        return path[::-1]
        return None

    max_flow = 0.0
    while True:
        path = bfs_find_path()
        if not path: break
        path_flow = inf
        for i in range(len(path) - 1):
            u, v = int(path[i]), int(path[i+1])
            path_flow = min(path_flow, residual_capacity.get((u, v), 0))
        if path_flow == 0: break
        # 更新残余网络
        for i in range(len(path) - 1):
            u, v = int(path[i]), int(path[i+1])
            residual_capacity[(u, v)] -= path_flow
            residual_capacity[(v, u)] += path_flow
        max_flow += path_flow
    return max_flow
```

#### 数学模型

* **最大流问题**（Maximum Flow）：给定一个网络 $ G = (V,E)$，每条有向边 $(u,v)$ 有容量 $c_{uv}$，寻找从源点 $s$ 到汇点 $t$ 的最大可达流量。
* **Edmonds-Karp 算法**：基于“广度优先搜索”（BFS）寻找增广路径，每次找到一条增广路径，按路径上最小剩余容量推送流量，然后更新残量网络，直到无法找到新的增广路径为止。复杂度 $O(V E^2)$。

#### 在 `RiskAnalyzer` 中的具体适用

* 这里“网络”基于**无向图**，所以将每个无向边 $(u,v)$ 同时视作两个有向边 $(u \to v)$ 与 $(v \to u)$，容量相同。
* 残余图 `residual_capacity[(u, v)]` 字典保存当前剩余容量，初始即是 `calculate_capacity(u, v)`。
* `use_tie` 参数：若为 `(0,0)`，则表示“不使用馈线间联络线”，即若某条边属性 `type=="馈线间联络线"`，则在搜索增广路径时跳过，不作为候选边。这样能模拟断开联络开关或不启用联络线的情形。

#### 代码实现细节

1. **映射变电站名称**

   ```python
   source = self._substation_map.get(source, source)
   sink = self._substation_map.get(sink, sink)
   ```

   * 若调用时传入的 `source="CB1"`，映射为 `'1'`；否则若传入的是节点 ID 字符串，就原样使用。

2. **构造残余容量字典**

   ```python
   for edge in self._edges_info:
       (begin, end), edge_info = list(edge.items())[0]
       capacity = self.calculate_capacity(begin, end)
       residual_capacity[(begin, end)] = capacity
       residual_capacity[(end, begin)] = capacity
   ```

   * 对于每条边 `(begin, end)`，计算其理论最大容量（kW），并将有向 `begin->end` 和 `end->begin` 初始残余容量都设置为相同值。

3. **增广路径搜索**

   ```python
   parents = {}
   visited = set([source])
   queue = deque([source])
   while queue:
       u = queue.popleft()
       for v in self._graph.neighbors(int(u)):
           v_str = str(v)
           if v_str not in visited and residual_capacity.get((int(u), v), 0) > 0:
               # 如果是不允许使用联络线，则跳过此边
               if (use_tie == (0, 0) and 
                   self._graph.get_edge_attribute(int(u), v, "type") == "馈线间联络线"):
                   continue
               parents[v_str] = u
               visited.add(v_str)
               queue.append(v_str)
               if v_str == sink:
                   # 重构从源到汇的完整路径
                   path = []
                   curr = sink
                   while curr is not None:
                       path.append(curr)
                       curr = parents.get(curr)
                   return path[::-1]
   return None
   ```

   * 典型 BFS：`parents` 记录某个节点是从哪个父节点扩展而来，便于最后回溯出完整路径。
   * 每次从 `u` 扩展到 `v` 之前，都要判断 `residual_capacity[(u,v)] > 0`，否则不满足剩余容量约束。
   * 同时，如果 `use_tie=(0,0)`，那么若边的 `type` 属性为“馈线间联络线”，则跳过，不允许从主馈线走到联络线。
   * 一旦 `v_str == sink`，就立刻回溯返回完整路径（字符串列表），如 `['1','5','7','10']`。

4. **增广与更新残量网络**

   ```python
   path_flow = float("inf")
   for i in range(len(path) - 1):
       u, v = int(path[i]), int(path[i+1])
       path_flow = min(path_flow, residual_capacity[(u, v)])
   for i in range(len(path) - 1):
       u, v = int(path[i]), int(path[i+1])
       residual_capacity[(u, v)] -= path_flow
       residual_capacity[(v, u)] += path_flow
   max_flow += path_flow
   ```

   * 首先遍历路径上每条边 `(u,v)`，找到最小的剩余容量 `path_flow`——即该条增广路径上可以推送的最大流量。
   * 然后对路径上的每条有向边作“减法”操作：`residual_capacity[(u,v)] -= path_flow`，并对反向边“加法”：`residual_capacity[(v,u)] += path_flow`。这样保证后续可以沿反向边“退回”这部分流。
   * 将得到的 `path_flow` 累加到 `max_flow` 中。

5. **停止条件**

   * 当 `bfs_find_path()` 返回 `None` 时，表示当前残量网络无法再找到一条从 `source` 到 `sink` 的增广路径，算法结束。

6. **注意**

   * 由于网络是无向图、并且 `calculate_capacity` 原始返回的是 kW 单位，`max_flow` 最终结果也是 kW 单位，代表在理想情况下、无电压降，某一时刻能从变电站给节点输送的最大有功功率。

---

## 五、故障概率与失负荷风险计算

### 5.1 单条线路故障概率：`edge_risk`

```python
def edge_risk(self, begin: int, end: int) -> float:
    length = self._graph.get_edge_attribute(begin, end, 'length')
    return float(length) * self.edge_each_length_risk
```

* **含义**：假设一条线路上每公里故障概率为 `edge_each_length_risk = 0.002`，长度为 $L$ km，则整条线路的基础故障概率为 $0.002\times L$。
* 这里没有考虑“分段开关”与“DG”对该条线路的故障影响，后续 `P_f` 方法会在此基础上做更全面的累加。
* 若 `length` 为 None 或者 `get_edge_attribute` 抛异常，则返回 0.0，并在日志中记录错误。

### 5.2 全网故障概率：`P_f`

```python
def P_f(self) -> float:
    total_failure_prob = 0.0
    for edge in self.edges_info:
        (begin, end), edge_info = list(edge.items())[0]
        # 基础线路故障概率
        line_prob = edge_info['length'] * self.edge_each_length_risk
        # 分段开关故障概率
        if edge_info.get('分段开关') not in [None, 'None', '']:
            line_prob += self.switch_risk
        # 分布式能源故障概率
        begin_has_dg = self._graph.get_node_attribute(str(begin), 'DG')
        end_has_dg = self._graph.get_node_attribute(str(end), 'DG')
        if begin_has_dg or end_has_dg:
            line_prob += self.dg_risk
        total_failure_prob += line_prob
    return total_failure_prob
```

#### 数学涵义

* **逐条线路累加**：对于每条线路 $(i,j)$，其故障概率

  $$
    P_{ij} = L_{ij}\lambda + \delta_{\text{SW}}\,p_{\text{SW}} + \delta_{\text{DG}}\,p_{\text{DG}},
  $$

  其中：

  * $L_{ij}$：线路长度（km）；
  * $\lambda = 0.002$（单位长度故障率）；
  * $\delta_{\text{SW}} = 1$ 若该条线路含“分段开关”，否则 0；
  * $p_{\text{SW}} = 0.002$（单个分段开关故障率）；
  * $\delta_{\text{DG}} = 1$ 若两端任意一端存在 DG，表示 DG 侧线路联动风险，否者 0；
  * $p_{\text{DG}} = 0.005$（DG 故障概率）。
* 整个网络的故障概率近似定义为各条线路故障概率之和：

  $$
    P_f = \sum_{(i,j)\in E} P_{ij}.
  $$

  * 这种简单累加忽略了“多条线路同时故障的联合概率”以及节点故障、开关故障对全网连通性的联动影响，是一种“线性叠加”的近似。

#### 代码特色

1. **开关故障检测**

   * `if edge_info.get('分段开关') not in [None, 'None', '']:`：只要该字段不为空，就默认此线路有一个“分段开关”，故障概率加上 `self.switch_risk=0.002`。
   * 若一条线路上有多个开关，此处代码只加了一次，但可视为“近似”视角——认为一个线路分段开关故障就足以隔离。

2. **DG 故障累加**

   * 先通过 `self._graph.get_node_attribute(str(begin), 'DG')`、`get_node_attribute` 方法查询该节点是否为 DG；
   * 若两端任意一端 `DG=True`，则加上 `0.005`；如果两端都是 DG，实际上仍只加一次。

3. **日志与健壮性**

   * 整个循环没有显式 `try/except`，但如果某条边 `length` 字段缺失，会 `KeyError` 异常导致 `P_f` 异常退出。这时，除非上层包裹了异常，否则会抛到控制台。
   * 如果希望更健壮，可在内部加上 `try/except`，但作者选择让缺失数据直接暴露错误，以便排查。

### 5.3 失负荷危害度：`C_ll`

```python
def C_ll(self) -> float:
    total_consequence = 0.0
    for node_id, node_data in self.nodes_info.items():
        node_type = node_data.get('type', '居民')
        weight = self._damage_weights.get(node_type, 1.0)
        load_demand = node_data.get('power', 0)
        if not node_data.get('DG', False) and load_demand > 0:
            max_transferable = 0.0
            for substation in ['CB1', 'CB2', 'CB3']:
                flow = self.edmons_krap(source=substation, sink=node_id)
                max_transferable = max(max_transferable, flow)
            load_loss = max(load_demand - max_transferable, 0)
            consequence = weight * load_loss
            total_consequence += consequence
    return total_consequence
```

#### 数学表达

* **定义**：失负荷危害度 $C_{LL}$＝对所有用户节点（非 DG 节点）计算

  $$
    C_{LL} \;=\; \sum_{i \in V_{\text{load}}} w_i \cdot \max\bigl(P_i - F_i,\, 0\bigr),
  $$

  其中：

  * $P_i$：“节点 $i$”的原始负荷需求；
  * $F_i = \max_{\text{过哪一站}} f_{\text{maxflow}}(\text{station}\to i)$，表示从任意变电站输送到节点 $i$ 的最大可转移功率（kW）；
  * $w_i$：节点类型对应的危害度权重；
  * 只对 `DG=False` 且 `power>0` 的节点计算（DG 节点本身有自供电能力，不计入失负荷）。

* **解释**：如果节点原来需要 100 kW，却最大只能供给 60 kW 才能到达（此时可能因为中间线路限流），那么缺口为 40 kW，按权重 $w_i$ 计算其带来的社会经济损失。

#### 代码实现要点

1. **过滤条件**

   * `if not node_data.get('DG', False) and load_demand > 0:`：

     * 排除 DG 节点（因为 DG 自带发电，不计入失负荷）；
     * 排除零负荷（如变电站节点本身）。

2. **多站最大流计算**

   ```python
   max_transferable = 0.0
   for substation in ['CB1', 'CB2', 'CB3']:
       flow = self.edmons_krap(source=substation, sink=node_id)
       max_transferable = max(max_transferable, flow)
   ```

   * 针对同一个节点 `node_id`，从三个变电站分别尝试计算“最大流”能输送到此处的功率，取其中最大的一个。
   * 这种做法隐式模拟了“重新布电”的逻辑：若 CB1→i 的通路容量不足，CB2→i 的通路可能更通畅，则优先选择之。

3. **缺口与加权**

   * `load_loss = max(load_demand - max_transferable, 0)`：若最大流能覆盖 `load_demand`，则缺口为 0；否则为差值。
   * `consequence = weight * load_loss` 加上了节点类型的“危害度权重”。

4. **累加**

   * 对所有合规节点循环叠加，得到全网的  **失负荷危害度** 量化值。

### 5.4 失负荷风险：`load_loss_risk`

```python
def load_loss_risk(self) -> float:
    total_risk = 0.0
    for node_id, node_data in self.nodes_info.items():
        power_demand = node_data.get('power', 0)
        if power_demand <= 0: continue
        if node_data.get('DG', False):
            failure_prob = self.dg_risk
        else:
            failure_prob = self.node_risk
        max_transfer = 0.0
        for substation in ['CB1', 'CB2', 'CB3']:
            flow = self.edmons_krap(source=substation, sink=node_id)
            max_transfer = max(max_transfer, flow)
        load_loss = max(power_demand - max_transfer, 0)
        node_risk = failure_prob * load_loss
        total_risk += node_risk
    return total_risk
```

#### 数学公式

* **节点风险**：

  $$
    R_i \;=\; p_i \times \max\bigl(P_i - F_i,\, 0\bigr),
  $$

  * 若节点 $i$ 为 DG 节点，则用 $p_{\text{DG}}=0.005$；否则用 $p_{\text{node}}=0.005$。
* **全网失负荷风险**：

  $$
    R_{LL} \;=\; \sum_{i \in V_{\text{load}}} R_i.
  $$
* 注意：此处没有再乘以权重 $w_i$，因为这已在“危害度”里体现。这里主要关注“概率 × 缺口”，量化预期损失量。

#### 代码实现细节

1. **遍历所有节点**

   * 不再区分 DG 与非 DG 节点的“过滤”，只要 `power_demand > 0` 都参与；
   * 如果是 DG 节点，故障概率用 `self.dg_risk`；否则用 `self.node_risk`；
   * 注意：有些 DG 节点可能功率负荷设为了 0 或负数，一并跳过。

2. **最大转移功率计算**

   * 复用了和 `C_ll` 一样的逻辑，从三座变电站分别求最大流，再取最大值。

3. **风险值叠加**

   * `node_risk = failure_prob * load_loss` 直接累加。
   * 由于大部分节点可能定义的 `power_demand` 规模较小，若分布式能源覆盖能力强，`load_loss` 很小，此处对全网风险贡献有限。

---

## 六、过载风险计算

### 6.1 过载线路比例：`P_ol_all`

```python
def P_ol_all(self) -> float:
    total_lines = 0
    overloaded_lines = 0
    threshold = 1.1 * self.feeder_current_limit  # 过载阈值
    for edge in self._edges_info:
        begin, end = list(edge.keys())[0]
        current = self.I_ij(begin, end)
        if current > threshold:
            overloaded_lines += 1
        total_lines += 1
    return overloaded_lines / total_lines if total_lines > 0 else 0.0
```

#### 数学定义

* 令所有线路数为 $M$。
* 对于第 $k$ 条线路 $(i_k, j_k)$，其实际电流为 $I_{i_k j_k}$。
* **过载判定阈值**：

  $$
    I_{\text{th}} = 1.1 \times I_{\text{rated}}.
  $$
* **过载线路比例**

  $$
    P_{OL} = \frac{|\{k : I_{i_k j_k} > I_{\text{th}}\}|}{M}.
  $$
* 若没有任何线路，则返回 0。

#### 代码要点

1. **遍历所有边**

   ```python
   for edge in self._edges_info:
       begin, end = list(edge.keys())[0]
       current = self.I_ij(begin, end)
       if current > threshold:
           overloaded_lines += 1
       total_lines += 1
   ```

   * 通过 `self._edges_info` 中的键提取 `(begin, end)`。
   * 直接调用之前写好的 `I_ij`，避免重复代码。

2. **安全阈值**

   * `threshold = 1.1 * self.feeder_current_limit`。
   * 其中 `self.feeder_current_limit=220A`，因此超过 242A 就算“过载”。

3. **返回值**

   * 比例型指标，值域 $[0,1]$。

### 6.2 过载危害度：`C_ol`

```python
def C_ol(self) -> float:
    total_consequence = 0.0
    threshold = 1.1 * self.feeder_current_limit
    for edge in self._edges_info:
        begin, end = list(edge.keys())[0]
        current = self.I_ij(begin, end)
        if current > threshold:
            # 获取两端节点类型及权重
            begin_type = self._graph.get_node_attribute(str(begin), 'type') or '居民'
            end_type = self._graph.get_node_attribute(str(end), 'type') or '居民'
            begin_weight = self._damage_weights.get(begin_type, 1.0)
            end_weight = self._damage_weights.get(end_type, 1.0)
            avg_weight = (begin_weight + end_weight) / 2
            overload_severity = current - threshold
            consequence = avg_weight * overload_severity
            total_consequence += consequence
    return total_consequence
```

#### 数学表示

* 对于每条过载线路 $(i,j)$，定义过载程度

  $$
    S_{ij} = I_{ij} - I_{\text{th}}, \quad
    I_{\text{th}} = 1.1 I_{\text{rated}}.
  $$
* 两端节点类型分别对应权重 $w_i$ 与 $w_j$。
* **加权过载危害度**

  $$
    C_{OL} 
    = \sum_{(i,j):\,I_{ij} > I_{\text{th}}}
      \left( \frac{w_i + w_j}{2} \right) \cdot S_{ij}.
  $$
* 直观理解：若一条过载线路两端均为“政府与机构”类型（权重 3.0），且过载幅度 50 A，则该线路危害度贡献为 $3.0 \times 50 = 150$。若两端类型不同，则取平均权重。

#### 代码实现亮点

1. **读取节点类型**

   * 两端节点 `begin`、`end` 均通过 `self._graph.get_node_attribute(str(node_id), 'type')` 获取节点类型。
   * 若某个节点类型缺失，默认为 `'居民'`，对应权重 1.0。

2. **计算过载程度与加权**

   * `overload_severity = current - threshold` 直接得到过载 A 数；
   * `avg_weight = (begin_weight + end_weight) / 2` 求平均权重，体现了“线路对两端影响”的综合考量。

3. **累加**

   * `total_consequence += avg_weight * overload_severity`，累加所有过载线路的“危害度值”。

---

## 七、综合风险指标与关键线路识别

### 7.1 综合风险分析：`comprehensive_risk_analysis`

```python
def comprehensive_risk_analysis(self) -> Dict[str, float]:
    results = {
        'failure_probability': self.P_f(),                
        'load_loss_consequence': self.C_ll(),             
        'load_loss_risk': self.load_loss_risk(),          
        'overload_probability': self.P_ol_all(),          
        'overload_consequence': self.C_ol(),              
    }
    results['total_risk'] = (
         results['load_loss_risk'] + 
         results['overload_probability'] * results['overload_consequence']
    )
    return results
```

* **返回值**：一个字典，包含 6 项：

  1. `failure_probability`：全网线路“基础故障概率”累计（线性叠加）；
  2. `load_loss_consequence`：失负荷“危害度” $C_{LL}$；
  3. `load_loss_risk`：失负荷“预期风险值” $R_{LL}$；
  4. `overload_probability`：过载线路比例 $\rho$；
  5. `overload_consequence`：过载“危害度” $C_{OL}$；
  6. `total_risk`：综合风险指标，按

     $$
       \text{TotalRisk} 
         = R_{LL} \;+\; \rho \times C_{OL}.
     $$

* **理念**：将“失负荷风险”和“过载风险”分开计算，最后以一个简单线性组合的方式给出一个“综合风险”。

  * 其中 $\rho=C_{OL}/|E|$ 为一个比例量纲，而 $C_{OL}$ 本身有 A×权重量纲，二者乘积是“预期损失量级”。
  * 这种设计思想：若过载概率 $\rho$ 很小，但某些过载线路一旦发生灾难性后果（$C_{OL}$ 很大），仍会被量化到综合风险位置。

#### 代码实现简单易读，关键在于多次调用前面方法即可。

### 7.2 关键线路识别：`get_critical_lines`

```python
def get_critical_lines(self, top_n: int = 5) -> List[Tuple[Tuple[int, int], float]]:
    line_currents = []
    for edge in self._edges_info:
        begin, end = list(edge.keys())[0]
        current = self.I_ij(begin, end)
        line_currents.append(((begin, end), current))
    line_currents.sort(key=lambda x: x[1], reverse=True)
    return line_currents[:top_n]
```

* **功能**：返回电流最大的前 `top_n` 条线路，列表元素为 `((begin,end), current_value)`。
* **用途**：这些“高电流线路”往往是系统中最“关键”的线路，一旦故障或过载，可能引起连锁停电。
* **代码思路**：

  1. 遍历每条边，计算 `I_ij` 电流值；
  2. 将 `( (u,v), I_uv )` 放入列表；
  3. 按电流值降序排序并截取前 `top_n`。

---

## 八、模型优势、参数敏感性与可拓展方向

### 8.1 模型优点小结

1. **一体化架构**

   * 从基础潮流分配到最大流估算，再到多种风险指标（故障概率、失负荷与过载风险）计算，模块间数据共享，调用链路清晰。
   * 所有风险指标均基于同一套“图 + 数据”进行计算，易于维护与升级。

2. **参数透明，可定制**

   * 运行时所有关键参数（$\lambda, p_{\text{SW}}, p_{\text{DG}}, \cos\phi, \text{容量}, \text{权重}$ 等）均在 `__init__` 中明确定义，后续易于根据实际电网情况做调整。
   * 例如：若想模拟夏季高温导致线路故障率上升，可把 `edge_each_length_risk` 调整到 0.003\~0.004；若想考察不同用户类型的损失重要度，可修改 `_damage_weights`。

3. **代码结构清晰，易二次开发**

   * 面向对象封装，各模块方法功能单一；
   * 并且通过 `try/except` 做了必要的错误处理，不会因为单个数据缺失导致崩溃；
   * 若要换图实现，只需将 `UndirectedGraph` 换成新的图类，且只要保证接口一致即可。

4. **近似潮流+最大流的混合思路**

   * 既保留了“最短路径 + BFS” 的直观潮流分配，也融合了最大流对节点可达容量的精细估算，为失负荷风险量化提供了合理依据。
   * 在中小规模配电网中，这种简化潮流往往既能保证运算效率，也能满足工程上“准可靠”需求。

### 8.2 参数敏感性分析（前瞻性思考）

1. **故障率参数 $\lambda, p_{\text{SW}}, p_{\text{DG}}$**

   * 若 $\lambda$ 稍微调高，`P_f` 会线性增大；若想量化“维护优化带来的风险提升/下降”，可以在敏感性分析中逐步增减 $\lambda$，观察 `failure_probability` 变化。
   * `switch_risk` 影响较小，仅在分段开关或联络开关数量较多的场景下才明显提升风险。

2. **潮流假设误差**

   * 简化潮流忽略了电压降、无功功率、潮流迂回等因素，若节点分布不均匀、线路阻抗差异大，可能导致 `I_ij` 计算偏差。
   * 在实际应用中，可在 `calculate_power_flow_simple` 之后插入一次 DC 潮流或 AC 潮流计算，做二次修正，提高精度。

3. **权重系数选择**

   * `_damage_weights` 对 `C_ll` 与 `C_ol` 有直接刻画作用；若要模拟不同城市用电结构，可将“居民 vs 商业 vs 工业”的权重做大幅度调整，看看系统哪类用户“韧性最弱”。
   * 在支撑应急预案时，若对政府机构断电要求“0容忍”，可以把其权重拉到 5.0 以上，迅速识别出必须双回路供电的节点。

### 8.3 可拓展方向

1. **引入时序仿真**

   * 当前模型针对“某一时刻的静态风险评估”，若想研究“高峰期 17:00\~19:00 连续 24 小时”的风险演变，需要做时序循环：每小时更新节点 `power`、环境影响系数，再次计算全网指标。
   * 可以将 `RiskAnalyzer` 包装成一个“小时级”或“分钟级”迭代器，动态输出风险曲线。

2. **结合机器学习预测故障率**

   * 目前 `edge_each_length_risk`、`node_risk` 等都属于经验值。若有历史故障日志，可训练一个“故障率预测模型”，在 `P_f` 中引用该模型预测参数。
   * 例如：基于天气（温度/湿度/雷雨）预测线路故障率，让模型更贴近实际场景。

3. **更精细的潮流计算**

   * 增加 AC 潮流（Newton-Raphson）或 DC 潮流分析，考虑无功功率和节点电压限制；
   * 引入分段电感、电容补偿等拓扑，精细化 `I_ij`。

4. **并网开关状态联合评估**

   * 目前代码对联络线（`type=="馈线间联络线"`）的控制仅通过 `use_tie` 参数在最大流中禁用；可扩展成“根据实时开关状态图”动态启用/禁用各路连接。

5. **改进失负荷逻辑**

   * 如果某节点部分负荷可由 DG 自供，那么在计算缺口时，应先减去 DG 容量 `dg_capacity`，再计算最大流剩余缺口。

---

## 九、示例运行与结果展示（可选）

> **提示**：如果你想把下面的演示结果画成图表，或者想把指标结果输出成 CSV，再用课题组的可视化平台画热力图，都可以用 `python_user_visible` 工具来实现。我在这里先给出伪代码思路，你可以按需插入到 Jupyter Notebook 中：

```python
# 示例：加载数据，实例化 RiskAnalyzer，计算指标
from utils.data_loder import nodes_info, edges_info
analyzer = RiskAnalyzer(nodes_info=nodes_info, edges_info=edges_info)

# 1. 计算综合风险指标
results = analyzer.comprehensive_risk_analysis()
print("综合风险指标：", results)

# 2. 获取 Top5 关键线路
critical_lines = analyzer.get_critical_lines(top_n=5)
print("Top5 关键线路及电流：", critical_lines)

# 3. 画出每条线路的电流水平分布
edge_currents = [(edge, analyzer.I_ij(edge[0], edge[1])) for edge_dict in edges_info for edge in edge_dict]
# 如果想画柱状图或表格，可以用 python_user_visible 生成 DataFrame 然后用 matplotlib 绘制。
```

若你需要这部分“代码+图表”演示，请随时告诉我！😉

---

## 十、总结

* **总体评价**：`RiskAnalyzer.py` 通过合理的数学近似和图算法，将电网风险评估模块化为：

  1. 潮流（最短路径）→
  2. 电流计算 →
  3. 最大流估算 →
  4. 故障概率与风险指标量化 →
  5. 关键线路识别。
* **写作建议**：在实际撰写论文或报告时，可以把各个指标的数学公式列出后，再在代码部分逐行对照解释。例如，把 `I_ij` 对应公式、把 `edmons_krap` 对应最大流模型、把 `P_f` 对应线性叠加模型，都写成文字+公式+伪代码的形式，既显示数学深度，又体现工程实现。
* **前瞻思考**：如果要把这个风险分析系统推向生产环境，建议：

  1. 与实时 SCADA 系统打通接口，获得分钟级负荷数据与开关状态；
  2. 定期更新故障率参数（通过历史数据训练）；
  3. 在巡检时生成风险报告，为运维人员指引“优先维修线路”；
  4. 结合智能预警机制，当过载比例或失负荷风险突破阈值时自动发出告警。

这样，你的数学建模报告不仅思想清晰、内容详实，还兼具工程可行性与未来拓展思路。加油，期待你的精彩成果！🚀
