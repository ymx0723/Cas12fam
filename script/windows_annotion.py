import pandas as pd
import re
import sys
from collections import defaultdict
# 解析结构域文件
def parse_domain_file(domain_file):
    domains = []
    boundary_pattern = re.compile(r'(\d+)-(\d+)\(([\w\-]+)\)')

    # 读取并解析文件
    with open(domain_file, 'r') as file:
        lines = file.readlines()

    # 解析每一行的结构域信息
    for line in lines:
        matches = boundary_pattern.findall(line)
        for match in matches:
            start, end, annotation = match
            domains.append((int(start), int(end), annotation))
    print(domains)
    # 查找WED区域的最大值
    max_wed1 = -float('inf')
    for start, end, annotation in domains:
        if 'WED' in annotation:  # 查找WED系列结构域的最大值
            max_wed1 = max(end, max_wed1)
            print(max_wed1)
    # 如果没有WED系列结构域，则查找RuvC系列的最小值
    if max_wed1 == -float('inf'):
        min_ruvc = float('inf')
        for start, end, annotation in domains:
            if 'RuvC' in annotation:  # 查找RuvC系列结构域的最小值
                min_ruvc = min(min_ruvc, start)
        return min_ruvc
    else:
        return max_wed1

def process_window_with_csv(csv_file):
    """
    根据最大WED或最小RuvC值按窗口区间处理结构域频次。
    只传入CSV文件路径和窗口大小，自动获取最大WED或最小RuvC值。
    返回每个窗口及其对应的结构域注释。
    """
    # 解析结构域文件，获取最大WED值或最小RuvC值
    df = pd.read_csv(csv_file)
    domains = df.iloc[:, 0].tolist()
    print(f"Total domains found: {len(domains)}")

    max_wed1_or_min_ruvc = parse_domain_file(domain_file)
    print(f"Max WED1 or Min RuvC: {max_wed1_or_min_ruvc}")
    try:
        max_wed1_or_min_ruvc = int(max_wed1_or_min_ruvc)
        print(f"Converted max_wed1_or_min_ruvc to int: {max_wed1_or_min_ruvc}")
    except ValueError:
        print(f"Error: Max WED1 or Min RuvC value is not an integer: {max_wed1_or_min_ruvc}")
        return None, None 
    
 
    # 读取CSV文件
    df = pd.read_csv(csv_file)
    # print(f"CSV Data Loaded: {df.shape[0]} rows, {df.shape[1]} columns.")
    window_size=int(20)

    # 初始化频率字典
    freq_dict = defaultdict(int)
    window_annotations = {}
    # 根据最大WED或最小RuvC值进行窗口处理
    print(f"Processing windows with range starting at {max_wed1_or_min_ruvc}...")
    print(type(max_wed1_or_min_ruvc),type(df.shape[1]),type(window_size))
    with open(output_file, 'w') as output:
        for window_start in range(max_wed1_or_min_ruvc, df.shape[1], 20):
            window_end = min(window_start + window_size, df.shape[1])
            print(f"Processing window: ({window_start}, {window_end})")
            
            for col_idx in range(window_start, window_end):
                column_data = df.iloc[:, col_idx]  # 获取当前列的数据
                highest_score = column_data.max()  # 当前列的最大分数
                highest_score_idx = column_data.idxmax()  # 获取最大分数所在的行索引
                # print(highest_score_idx)
                # 找到对应的结构域名称
                structure_domain = domains[highest_score_idx]
                # print(structure_domain)
                # 统计当前结构域的频次
                freq_dict[structure_domain] += 1
                window_annotations[(window_start, window_end)] = structure_domain

            window_annotation = window_annotations.get((window_start, window_end), "No annotation")
            output.write(f"Window ({window_start}, {window_end}) annotations: {window_annotation}\n")
            print(f"Window ({window_start}, {window_end}) annotations: {window_annotation}")

    print(f"Final Frequency Dict: {dict(freq_dict)}")
    return window_annotations, freq_dict


domain_file = sys.argv[1] # 这里换成你的实际文件路径
csv_file = sys.argv[2] 
output_file = sys.argv[3]
print(parse_domain_file(domain_file))
window_annotations, freq_dict = process_window_with_csv(csv_file)



