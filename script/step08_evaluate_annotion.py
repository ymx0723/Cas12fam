import pandas as pd
import re
import sys

def read_domain_positions(file_name):
    domain_positions = []
    with open(file_name, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 4:
                protein_id, domain, start, end = parts[:4]
                domain_positions.append((protein_id, domain, int(start), int(end)))
    return domain_positions

def calculate_overlap(boundary, domain):
    """
    计算边界区间和结构域区间的重叠比例和超出比例。

    参数:
        boundary: tuple (start1, end1) 注释区间
        domain: tuple (start2, end2) 真实结构域区间

    返回:
        tuple: (overlap_ratio, exceed_ratio)
    """
    start1, end1 = boundary
    start2, end2 = domain
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)
    
    if overlap_start <= overlap_end:
        overlap_length = overlap_end - overlap_start + 1
    else:
        overlap_length = 0

    domain_length = end2 - start2 + 1
    annotation_length = end1 - start1 + 1

    if domain_length == 0:
        print(f"Warning: 结构域长度为零: {domain}")
        return (0, 0)

    overlap_ratio = overlap_length / domain_length
    exceed_ratio = annotation_length / domain_length

    return (overlap_ratio, exceed_ratio)

def evaluate_annotations(cleaned_boundaries, domain_positions):
    results = []
    for protein_id, domain, domain_start, domain_end in domain_positions:
        # 找到与当前 protein_id 相同的注释
        matching_boundaries = [b for b in cleaned_boundaries if b[0] == protein_id]
        if not matching_boundaries:
            print(f"Warning: 没有找到与蛋白ID '{protein_id}' 匹配的注释区间。")
        for _, boundary_start, boundary_end, annotation in matching_boundaries:
            overlap_ratio, exceed_ratio = calculate_overlap((boundary_start, boundary_end), (domain_start, domain_end))
            if 0.7 <= overlap_ratio <= 1.3 and exceed_ratio <= 1.3:
                status = "Success"
            else:
                status = "Fail"
            results.append((protein_id, domain, domain_start, domain_end, annotation, status, overlap_ratio, exceed_ratio))
    return results

def write_evaluation_results(file_name, results):
    """
    将评估结果写入CSV文件。

    参数:
        file_name (str): 输出文件名
        results (list): 评估结果列表
    """
    df = pd.DataFrame(results, columns=[
        "Protein ID", "Domain", "Domain Start", "Domain End",
        "Annotation", "Status", "Overlap Ratio", "Exceed Ratio"
    ])
    df.to_csv(file_name, index=False)

if __name__ == "__main__":
    # 输入文件名
    domain_positions_file = "rcsb_cas12_domain.position.txt"
    cleaned_boundaries_file = sys.argv[1]

    # 读取真实结构域的位置
    domain_positions = read_domain_positions(domain_positions_file)

    # 读取清理后的注释区间
    cleaned_boundaries = []
    protein_id = sys.argv[2]  # 直接使用文件名作为蛋白ID
    with open(cleaned_boundaries_file, 'r') as file:
        for line in file:
            match = re.match(r'(\d+)-(\d+)\((\w+)\)', line.strip())
            if match:
                boundary_start, boundary_end, annotation = match.groups()
                cleaned_boundaries.append((protein_id, int(boundary_start), int(boundary_end), annotation))

    # 评估注释的准确性
    annotation_results = evaluate_annotations(cleaned_boundaries, domain_positions)

    # 将评估结果写入文件
    evaluation_results_file = f"{protein_id}_annotation_evaluation_results.csv"
    write_evaluation_results(evaluation_results_file, annotation_results)

    print(f"注释评估结果已保存到 {evaluation_results_file}") 