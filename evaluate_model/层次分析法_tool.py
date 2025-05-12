import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import warnings
from typing import List, Tuple, Dict

# 忽略所有警告
warnings.filterwarnings("ignore")

# 设置支持中文的字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 支持中文的字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 自定义配色
custom_palette = ['#f9f7f7', '#dbe2ef', '#3f72af', '#112d4e']

class AHPAnalyzer:
    """
    通用层次分析法(AHP)分析工具
    支持多准则和多备选方案的层次分析
    """
    def __init__(self):
        """
        初始化AHP分析器
        """
        self.RI_DICT = {
            1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 
            6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
        }

    def ahp_weight(self, matrix: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        计算AHP权重和一致性比率
        
        参数:
        - matrix: 判断矩阵
        
        返回:
        - 权重向量
        - 一致性比率
        """
        n = matrix.shape[0]
        # 计算几何平均数
        geo_mean = np.prod(matrix, axis=1) ** (1/n)
        # 归一化权重
        weights = geo_mean / np.sum(geo_mean)

        # 一致性检验
        lambda_max = np.sum(np.dot(matrix, weights) / weights) / n
        CI = (lambda_max - n) / (n - 1)
        RI = self.RI_DICT.get(n, 1.49)
        CR = CI / RI if RI != 0 else 0

        return weights, CR

    def create_judgment_matrix(self, vals: List[List[float]]) -> np.ndarray:
        """
        创建完整的判断矩阵
        
        参数:
        - vals: 上三角矩阵数据
        
        返回:
        - 完整的判断矩阵
        """
        size = len(vals) + 1
        matrix = np.ones((size, size))
        for i in range(size - 1):
            for j in range(i + 1, size):
                matrix[i, j] = vals[i][j - i - 1]
                matrix[j, i] = 1 / matrix[i, j]
        return matrix

    def plot_heatmap(self, 
                     data: np.ndarray, 
                     title: str = '代价热力图', 
                     x_labels: List[str] = None, 
                     y_labels: List[str] = None, 
                     cmap: str = "YlGnBu") -> None:
        """
        绘制热力图
        
        参数:
        - data: 热力图数据 (numpy数组)
        - title: 图表标题
        - x_labels: X轴标签
        - y_labels: Y轴标签
        - cmap: 颜色映射
        """
        plt.figure(figsize=(12, 8))
        ax = sns.heatmap(data, 
                         annot=True, 
                         fmt=".1f", 
                         cmap=cmap, 
                         linewidths=0.5)
        ax.set_title(title, fontsize=18)
        if x_labels:
            ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=10)
        if y_labels:
            ax.set_yticklabels(y_labels, rotation=0, fontsize=10)
        ax.set_xlabel("因素", fontsize=14)
        ax.set_ylabel("备选方案", fontsize=14)
        plt.tight_layout()
        plt.show()


def main():
    """
    测试AHP分析工具的主函数
    """
    # 创建AHP分析器实例
    ahp = AHPAnalyzer()
    
    # --- 第一步：准则判断矩阵 ---
    criteria_names = ['教育', '费用', '生活', '语言', '签证']
    criteria_matrix = ahp.create_judgment_matrix([
        [3, 4, 7, 6],
        [2, 5, 4],
        [3, 2],
        [0.5]
    ])
    
    # 计算准则权重
    criteria_weights, cr_crit = ahp.ahp_weight(criteria_matrix)
    print("准则权重:")
    for name, weight in zip(criteria_names, criteria_weights):
        print(f"{name}: {weight:.4f}")
    print(f"准则权重一致性比率: {cr_crit:.4f}")
    
    # --- 第二步：每个准则下的备选方案判断矩阵 ---
    alternatives = ['美国', '英国', '加拿大', '德国']
    criteria_alt_matrices = {
        '教育': ahp.create_judgment_matrix([
            [2, 3, 4],
            [1.5, 2],
            [1.5]
        ]),
        '费用': ahp.create_judgment_matrix([
            [0.5, 0.33, 0.25],
            [0.5, 0.33],
            [0.5]
        ]),
        '生活': ahp.create_judgment_matrix([
            [1.5, 1.2, 1.8],
            [1.1, 1.5],
            [1.3]
        ]),
        '语言': ahp.create_judgment_matrix([
            [1.1, 1.2, 2],
            [1.1, 1.8],
            [1.6]
        ]),
        '签证': ahp.create_judgment_matrix([
            [1.2, 1.5, 2],
            [1.2, 1.7],
            [1.4]
        ])
    }
    
    # 计算各准则下的备选方案权重
    alt_weights = []
    for criterion in criteria_names:
        w, cr = ahp.ahp_weight(criteria_alt_matrices[criterion])
        alt_weights.append(w)
        print(f"\n{criterion}准则下各备选方案权重:")
        for alt, weight in zip(alternatives, w):
            print(f"{alt}: {weight:.4f}")
        print(f"{criterion}准则下备选方案权重一致性比率: {cr:.4f}")
    
    # 转换为矩阵：形状 (准则数量, 备选方案数量)
    alt_weights_matrix = np.array(alt_weights)
    
    # 第三步：计算综合评分
    final_scores = np.dot(criteria_weights, alt_weights_matrix)
    final_df = pd.DataFrame({
        '国家': alternatives,
        '综合评分': final_scores
    }).sort_values(by='综合评分', ascending=False)
    
    print("\n🏆 综合得分结果：")
    print(final_df)

    # 热力图可视化
    df_heat = pd.DataFrame(alt_weights_matrix, index=criteria_names, columns=alternatives)
    ahp.plot_heatmap(df_heat, title="各准则下留学国家权重分布 (AHP)")


if __name__ == "__main__":
    main()