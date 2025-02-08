import os
import re
import sys
from collections import defaultdict

# 解析结构域位置文件
def parse_domain_positions(domain_file):
    """
    解析结构域位置文件，返回一个字典：
    {
        'PDBID_Chain': [
            {'domain': 'DomainName', 'start': int, 'end': int},
            ...
        ],
        ...
    }
    """
    domain_dict = defaultdict(list)
    with open(domain_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 4:
                continue  # 跳过格式不正确的行
            pdb_chain, domain, start, end = parts[:4]
            try:
                start = int(start)
                end = int(end)
            except ValueError:
                continue  # 跳过起始或结束不是整数的行
            domain_dict[pdb_chain].append({
                'domain': domain,
                'start': start,
                'end': end
            })
    return domain_dict

# 解析 DALI 输出文件
import re

def parse_dali_output(dali_file):
    """
    解析 DALI 输出文件，返回一个列表的等价关系字典：
    [
        {
            'mol1_start': int,
            'mol1_end': int,
            'mol2_start': int,
            'mol2_end': int
        },
        ...
    ]
    """
    # 更新正则表达式，匹配括号内的等价关系（例如：UNK 1 - LEU 12 <=> MET 1 - PRO 12）
    pattern = re.compile(r'\(\s*(\S+)\s*(\d+)\s*-\s*(\S+)\s*(\d+)\s*<=>\s*(\S+)\s*(\d+)\s*-\s*(\S+)\s*(\d+)\s*\)')
    
    equivalences = []
    
    with open(dali_file, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                # 提取等价关系中的数字和氨基酸名
                mol1_start = int(match.group(2))
                mol1_end = int(match.group(4))
                mol2_start = int(match.group(6))
                mol2_end = int(match.group(8))
                print(f"mol1_start: {mol1_start}, mol1_end: {mol1_end}")
                print(f"mol2_start: {mol2_start}, mol2_end: {mol2_end}")
                equivalences.append({
                    'mol1_start': mol1_start,
                    'mol1_end': mol1_end,
                    'mol2_start': mol2_start,
                    'mol2_end': mol2_end
                })

            else:
                # 打印未匹配的行以进行调试
                print(f"未匹配行: {line.strip()}")
                pass
    
    return equivalences
# 映射结构域
def map_domains(equivalences, domains):
    """
    根据等价关系和结构域信息，映射 molA1 (mol1) 的结构域到 mol2 的位置。
    返回一个字典：
    {
        'DomainName': [
            (mol2_start, mol2_end),
            ...
        ],
        ...
    }
    """
    domain_mapping = defaultdict(list)
    
    # 遍历所有等价关系
    for eq in equivalences:
        m2_start = eq['mol2_start']
        m2_end = eq['mol2_end']
        m1_start = eq['mol1_start']
        m1_end = eq['mol1_end']
        
        # 遍历所有结构域
        for domain in domains:
            d_start = domain['start']
            d_end = domain['end']
            
            # 检查 mol1 的结构域和 mol2 的等价区是否有重叠
            if m1_end < d_start or m1_start > d_end:
                continue  # 无重叠
            
            # 计算重叠部分
            overlap_start = max(m1_start, d_start)
            overlap_end = min(m1_end, d_end)
            
            # 计算 mol1 中的相对位置比例
            m1_range = m1_end - m1_start + 1
            if m1_range <= 0:
                continue  # 避免除以零或负数
            
            ratio_start = (overlap_start - m1_start) / m1_range
            ratio_end = (overlap_end - m1_start) / m1_range
            
            # 计算对应的 mol2 位置
            m2_overlap_start = int(m2_start + ratio_start * (m2_end - m2_start + 1))
            m2_overlap_end = int(m2_start + ratio_end * (m2_end - m2_start + 1))
            
            # 确保 start <= end
            if m2_overlap_start > m2_overlap_end:
                m2_overlap_start, m2_overlap_end = m2_overlap_end, m2_overlap_start
            
            domain_mapping[domain['domain']].append((m2_overlap_start, m2_overlap_end))
    
    return domain_mapping
# 主函数
def main():
    if len(sys.argv) != 3:
        print("Usage: python map_molA_domains_fixed.py <dali_output_directory> <domain_position_file>")
        sys.exit(1)
    
    dali_output_dir = sys.argv[1]      # 包含所有 mol1A.txt 文件的目录
    domain_position_file = sys.argv[2] # 结构域位置文件
    
    # 检查目录和文件是否存在
    if not os.path.isdir(dali_output_dir):
        print(f"Error: DALI output directory '{dali_output_dir}' does not exist.")
        sys.exit(1)
    if not os.path.isfile(domain_position_file):
        print(f"Error: Domain position file '{domain_position_file}' does not exist.")
        sys.exit(1)
    
    # 解析结构域位置文件
    domains_dict = parse_domain_positions(domain_position_file)
    print(f"已解析结构域位置文件，共包含 {len(domains_dict)} 个 PDBID_Chain 组合。")
    
    # 准备输出文件
    output_mapping_file = os.path.join(dali_output_dir, "molA2_domain_mapping.txt")
    with open(output_mapping_file, 'w') as out_f:
        # 写入表头
        out_f.write("DALI_File\tPDBID_Chain\tDomain\tMolA_Residue_Range\n")
        
        # 遍历所有 DALI 输出文件
        for dali_file in os.listdir(dali_output_dir):
            if not dali_file.endswith('_mol1A.txt'):
                continue  # 只处理以 _mol1A.txt 结尾的文件
            dali_path = os.path.join(dali_output_dir, dali_file)
            
            # 假设 DALI 文件名格式为 <input_file>_mol1A.txt，例如 5u34_A_mol1A.txt
            match = re.match(r'^(.+)_mol1A\.txt$', dali_file)
            if not match:
                print(f"警告：文件名格式不匹配，跳过文件 {dali_file}")
                continue
            input_basename = match.group(1)
            
            # 假设输入文件名包含 PDBID 和 Chain，用下划线分隔，例如 5u34_A
            pdb_chain_match = re.match(r'^(\w{4})_(\w)$', input_basename)
            if not pdb_chain_match:
                print(f"警告：输入文件名格式不符合预期，跳过文件 {dali_file}")
                continue
            pdb_id, chain = pdb_chain_match.groups()
            pdb_chain = f"{pdb_id}_{chain}"
            
            if pdb_chain not in domains_dict:
                print(f"警告：未在结构域位置文件中找到 {pdb_chain}，跳过文件 {dali_file}")
                continue
            domains = domains_dict[pdb_chain]
            
            # 解析 DALI 输出文件
            equivalences = parse_dali_output(dali_path)
            if not equivalences:
                print(f"警告：未在文件 {dali_file} 中解析到等价关系。")
                continue
            
            # 映射结构域
            domain_mappings = map_domains(equivalences, domains)
            
            # 写入映射结果
            for domain, ranges in domain_mappings.items():
                for r in ranges:
                    out_f.write(f"{dali_file}\t{pdb_chain}\t{domain}\t{r[0]}-{r[1]}\n")
    
    print(f"结构域映射完成，结果保存在 '{output_mapping_file}'。")

if __name__ == "__main__":
    main()