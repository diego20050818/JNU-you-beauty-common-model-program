from 深圳杯C题.utils.RiskAnalyzer import RiskAnalyzer
from utils.tool import *
from utils.data_loder import edges_info, nodes_info
from tabulate import tabulate
from loguru import logger
import argparse
import ast
import sys
import time


@logger.catch
def problem1(print_entire_graph=False, instances=None, print_logs=True):
    """问题1：验证一条线路的失负荷与过负荷风险，并进行基础分析"""
    analyzer = RiskAnalyzer(nodes_info=nodes_info,edges_info=edges_info)
    

problem1()