import pandas as pd
import numpy as np
from Bio import PDB
import sys
import re

# 定义函数来解析SWORD文件以获取蛋白长度
def get_protein_length_from_sword(sword_file_path):
    max_end = 0
    with open(sword_file_path, "r") as file:
        for line_num, line in enumerate(file, 1):
            # 检查是否为空行
            if not line.strip():
                print(f"Warning: Skipping empty line at line {line_num}")
                continue
            
            # 查找所有可能的区间
            matches = re.findall(r'(\d+)-(\d+)', line)
            if not matches:
                print(f"Warning: Skipping line {line_num} due to invalid format: {line.strip()}")
                continue
            
            try:
                for match in matches:
                    start, end = map(int, match)
                    if start > end:
                        print(f"Warning: Skipping range {start}-{end} at line {line_num} because start > end: {line.strip()}")
                        continue
                    max_end = max(max_end, end)
            except ValueError:
                print(f"Warning: Skipping line {line_num} due to invalid integer values: {line.strip()}")
    
    # 最终检查是否有有效的数据
    if max_end == 0:
        print("Error: No valid range found in SWORD file.")
        sys.exit(1)
    
    return max_end

# 定义函数来解析DALI文件并构建矩阵
def parse_dali_file(dali_file_path, protein_length):
    # 初始化空的矩阵
    matrix = pd.DataFrame(0, index=[], columns=range(1, protein_length + 1))
    
    # 定义结构域名称替换映射
    domain_mapping = {
        'WED1-1': 'WED1',
        'WED1-2': 'WED2',
        'OBD1': 'WED1',
        'OBD2': 'WED2',
        'Helical1': 'REC1',
        'Helical2': 'REC2',
        'Helical3': 'REC3',
        'Rec2': 'REC2',
        'BH1': 'BH',
        'Nuc': 'NUC',
        'Nuc-1': 'NUC1',
        'Nuc-2': 'NUC2',
        'RUVC3': 'RuvC3',
    }
    
    # 打开DALI注释文件并解析内容
    with open(dali_file_path, "r") as file:
        for line in file:
            # 解析每行内容
            parts = line.strip().split()
            if len(parts) == 4 and '-' in parts[3]:
                try:
                    domain_name = parts[2]
                    # 替换结构域名称
                    domain_name = domain_mapping.get(domain_name, domain_name)
                    start, end = map(int, parts[3].split('-'))
                    
                    # 如果矩阵中还没有该结构域，添加一行
                    if domain_name not in matrix.index:
                        matrix.loc[domain_name] = [0] * protein_length
                    
                    # 更新矩阵中相应区间的值
                    matrix.loc[domain_name, start:end+1] += 1
                except ValueError:
                    print(f"Warning: Skipping line due to invalid range format: {line}")
    return matrix

# 解析新的注释文件并更新矩阵
def parse_new_annotation_file(annotation_file_path, protein_length, domain_matrix):
    with open(annotation_file_path, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 8:
                protein_id = parts[0]  # 蛋白ID
                domain_full = parts[1]  # 结构域名
                domain = domain_full.split('_')[-1]                
                start = int(parts[6])  # 结构域开始位置
                end = int(parts[7])  # 结构域结束位置
                
                # 如果结构域名称在映射表中，进行替换
                domain_mapping = {
                    'WED1-1': 'WED1',
                    'WED1-2': 'WED2',
                    'OBD1': 'WED1',
                    'OBD2': 'WED2',
                    'Helical1': 'REC1',
                    'Helical2': 'REC2',
                    'Helical3': 'REC3',
                    'Rec2': 'REC2',
                    'BH1': 'BH',
                    'Nuc': 'NUC',
                    'Nuc-1': 'NUC1',
                    'Nuc-2': 'NUC2',
                    'RUVC3': 'RuvC3',
                }
                domain = domain_mapping.get(domain, domain)
                
                # 更新矩阵中的相关区域
                if domain not in domain_matrix.index:
                    domain_matrix.loc[domain] = [0] * protein_length
                
                domain_matrix.loc[domain, start:end + 1] += 1
    return domain_matrix


# 定义函数来解析SWORD文件并为每个区域分配结构域
def assign_domains_to_sword_regions(sword_file_path, domain_matrix, new_annotation_matrix=None):
    assigned_lines = []
    
    with open(sword_file_path, "r") as file:
        for line in file:
            if line.strip() and "BOUNDARIES" not in line and "ALTERNATIVES" not in line and "#D" not in line:
                matches = re.findall(r'(\d+)-(\d+)', line)
                new_line = line.strip()
                for match in matches:
                    try:
                        start, end = map(int, match)
                        
                        # 获取该区间在矩阵中的所有结构域得分
                        domain_scores = domain_matrix.loc[:, start:end].sum(axis=1)
                        
                        # 如果存在新的注释矩阵，考虑其中的结构域
                        if new_annotation_matrix is not None:
                            new_domain_scores = new_annotation_matrix.loc[:, start:end].sum(axis=1)
                            domain_scores += new_domain_scores
                
                        # 找到得分最高的结构域，如果多个结构域得分相同，选择第一个
                        if not domain_scores.empty:
                            assigned_domain = domain_scores.idxmax()
                        else:
                            assigned_domain = "UNKNOWN"
                        
                        
                        # 在原始区间后面加上对应的结构域
                        new_line = new_line.replace(f"{start}-{end}", f"{start}-{end}({assigned_domain})")
                    except ValueError:
                        print(f"Warning: Skipping range due to invalid format: {line}")
                assigned_lines.append(new_line)
            else:
                assigned_lines.append(line.strip())
    
    return "\n".join(assigned_lines)


# 主程序
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python step06_2_domain_matrix.py <dali_file_path> <sword_file_path> <new_annotation_file_path> <output_file_path>")
        sys.exit(1)
    
    dali_file_path = sys.argv[1]  # DALI注释文件路径
    sword_file_path = sys.argv[2]  # SWORD区域文件路径
    new_annotation_file_path = sys.argv[3]  # 新的注释文件路径
    
    # 获取蛋白长度从SWORD文件中
    protein_length = get_protein_length_from_sword(sword_file_path)
    
    # 解析DALI注释文件并构建矩阵
    domain_matrix = parse_dali_file(dali_file_path, protein_length)
    
    # 解析新的注释文件并更新矩阵
    domain_matrix = parse_new_annotation_file(new_annotation_file_path, protein_length, domain_matrix)
    
    # 为每个SWORD区域分配结构域
    formatted_result = assign_domains_to_sword_regions(sword_file_path, domain_matrix)
    
    # 输出分配的结构域信息到文件
    output_file_path = f"{sys.argv[4]}_annotated_sword_result.txt"
    with open(output_file_path, "w") as output_file:
        output_file.write(formatted_result)
    print(f"Annotated SWORD result saved to {output_file_path}")
    
    # 保存矩阵到CSV文件
    domain_matrix.to_csv(f"{sys.argv[4]}_domain_annotation_matrix.csv")

