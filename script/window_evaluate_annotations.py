import sys

def read_annotations(file_path):
    """读取注释文件，返回蛋白ID和结构域信息"""
    annotations = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:  # 跳过空行
                continue
            
            parts = line.split("\t")  # 以制表符分割
            if len(parts) < 4:  # 如果行的列数小于4，说明格式有问题
                print(f"Warning: 跳过格式不正确的行: {line}")
                continue
            
            protein_id = parts[0]
            domain = parts[1]
            domain_start = int(parts[2])
            domain_end = int(parts[3])
            
            if protein_id not in annotations:
                annotations[protein_id] = []
            annotations[protein_id].append((domain, domain_start, domain_end))
    
    return annotations

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


def evaluate_annotations(correct_domain_file, annotation_file):
    correct_domains = read_annotations(correct_domain_file)
    annotations = read_annotations(annotation_file)

    # print("Correct Domains:", correct_domains)  # 打印 correct_domains
    # print("Annotations:", annotations)  # 打印 annotations
    results = []
    for protein_id, domains in correct_domains.items():
        for domain, domain_start, domain_end in domains:  # 解包 domains 中的每个元组
            matching_boundaries = [b for b in annotations.get(protein_id, []) if b[0] == domain]
            if not matching_boundaries:
                print(f"Warning: 没有找到与蛋白ID '{protein_id}' 和结构域 '{domain}' 匹配的注释区间。")
            
            print("Protein ID\tCorrect Domain\tCorrect Domain Start\tCorrect Domain End\tAnnotation Domain\tAnnotation Domain Start\tAnnotation Domain End\tStatus\tOverlap Ratio\tExceed Ratio")

            for matching in matching_boundaries:
                domain_annotation, boundary_start, boundary_end = matching  # 解包匹配的结构域
                
                overlap_ratio, exceed_ratio = calculate_overlap((boundary_start, boundary_end),(domain_start, domain_end))
                
                # 判断重叠比例和超出比例
                if 0.7 <= overlap_ratio <= 1.3 and exceed_ratio <= 1.3:
                    status = "Success"
                else:
                    status = "Fail"
                result_line = f"{protein_id}\t{domain}\t{domain_start}\t{domain_end}\t{domain_annotation}\t{boundary_start}\t{boundary_end}\t{status}\t{overlap_ratio:.2f}\t{exceed_ratio:.2f}"                
                results.append(result_line)

    for result in results:
        print(result)

    return results


# 执行评估
correct_domain_file = "rcsb_cas12_domain.position.txt"
annotation_file = sys.argv[1]
evaluate_annotations(correct_domain_file, annotation_file)
