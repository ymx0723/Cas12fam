import re
import pandas as pd
import sys
from collections import defaultdict
from collections import Counter

# 解析结构域文件，提取结构域起始位置与注释信息
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
    # print(domains)
    return domains

# 处理窗口，判断WED2的起始作为窗口循环的起始位置
def process_window_with_csv(csv_file, domain_file, output_file):
    """
    根据WED2的起始位置按窗口区间处理结构域频次。
    传入CSV文件路径、域文件路径和输出文件路径，自动获取WED2的起始位置。
    返回每个窗口及其对应的结构域注释。
    """
    # 解析CSV文件
    df = pd.read_csv(csv_file)
    print(f"CSV Data Loaded: {df.shape[0]} rows, {df.shape[1]} columns.")

    # 解析结构域文件，获取WED2的起始位置
    domain_data = parse_domain_file(domain_file)
    print(f"Total domains parsed from domain file: {len(domain_data)}")

    # 查找WED2的起始位置
    wed2_start = None
    for start, end, annotation in domain_data:
        if 'WED2' in annotation:
            wed2_start = start
            print(f"Found WED2 at position {start}")
            break

    if wed2_start is None:
        print("Error: Could not find WED2 start position.")
        return None, None

    print(f"WED2 starting at position: {wed2_start}")
    domains = df.iloc[:, 0].tolist()
    # 初始化频率字典
    freq_dict = defaultdict(int)
    window_annotations = {}
    window_size = 5  # 设置窗口大小为5

    # 根据WED2的起始位置进行窗口处理
    with open(output_file, 'w') as output:
        for window_start in range(1, wed2_start, 5):
            window_end = min(window_start + window_size, df.shape[1])
            print(f"Processing window: ({window_start}, {window_end})")
            domain_counter = Counter()

            for col_idx in range(window_start, window_end):
                column_data = df.iloc[:, col_idx]  # 获取当前列的数据
                # print(column_data)
                # column_data = pd.to_numeric(column_data, errors='coerce')
                if column_data.isna().all():  # 如果整列都是NaN，跳过该列
                    print(f"Skipping column {col_idx} due to non-numeric values.")
                    continue
                highest_score = column_data.max()  # 当前列的最大分数
                highest_score_idx = column_data.idxmax()  # 获取最大分数所在的行索引
                # print(highest_score)
                # print(highest_score_idx)

                # 获取对应的结构域名称
                structure_domain = domains[highest_score_idx]
                # print(structure_domain)
                # 统计当前结构域的频次
                domain_counter[structure_domain] += 1
                # print(freq_dict)

                # 存储窗口区间的结构域注释
            if domain_counter:
                most_common_domain, freq = domain_counter.most_common(1)[0]
            else:
                most_common_domain, freq = "No annotation", 0

            # 处理每个窗口的注释
            window_annotations[(window_start, window_end)] = (most_common_domain, freq)
            output.write(f"{window_start}-{window_end}:{most_common_domain} {freq}\n")
            print(f"{window_start}-{window_end}:{most_common_domain} {freq}")

    print(f"Final Frequency Dict: {dict(freq_dict)}")
    return window_annotations, freq_dict

domain_file = sys.argv[1] # 这里换成你的实际文件路径
csv_file = sys.argv[2] 
output_file = sys.argv[3]
print(parse_domain_file(domain_file))
window_annotations, freq_dict = process_window_with_csv(csv_file,domain_file,output_file)