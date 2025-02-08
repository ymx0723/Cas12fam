import pandas as pd
import re
import sys
# 文件路径
m8_file_path = sys.argv[2]
pdb_file_path = sys.argv[1]
output_file_path = sys.argv[3]

# 读取 pdb 文件中的氨基酸顺序，生成连续编号到不连续编号的映射
def parse_pdb_residues(pdb_file):
    residue_mapping = {}
    continuous_index = 1
    seen_res_seq = set()
    with open(pdb_file, 'r') as pdb:
        for line in pdb:
            if line.startswith('ATOM') or line.startswith('HETATM'):
                chain_id = line[21].strip()  # 链标识符 (21列)
                res_name = line[17:20].strip()  # 氨基酸名称 (17-20列)
                res_seq = int(line[22:26].strip())  # 残基序列号 (22-26列)
                # 确保每个残基序列号只映射一次
                if res_seq not in seen_res_seq:
                    residue_mapping[continuous_index] = res_seq
                    seen_res_seq.add(res_seq)
                    continuous_index += 1
    print("连续编号到不连续编号的映射关系：")
    for k, v in residue_mapping.items():
        print(f"连续编号 {k} -> 不连续编号 {v}")
    return residue_mapping

# 读取 .m8 文件
def read_m8_file(m8_file):
    return pd.read_csv(m8_file, sep='\t', header=None)

# 映射 .m8 文件第七列和第八列到 pdb 中的不连续编号
def remap_columns(m8_df, residue_mapping):
    mapped_values_7 = []
    mapped_values_8 = []
    for idx, row in m8_df.iterrows():
        try:
            res_index_7 = int(row[6])  # 第七列是 index 6
            res_index_8 = int(row[7])  # 第八列是 index 7

            # 使用残基字典映射到 pdb 中的不连续编号
            value_7 = residue_mapping.get(res_index_7, 'N/A')
            value_8 = residue_mapping.get(res_index_8, 'N/A')

            # 打印替换信息
            # print(f"第 {idx} 行，第七列的残基编号 {res_index_7} 被替换为：{value_7}")
            # print(f"第 {idx} 行，第八列的残基编号 {res_index_8} 被替换为：{value_8}")

            mapped_values_7.append(value_7)
            mapped_values_8.append(value_8)
        except ValueError:
            print(f"错误：第 {idx} 行的残基编号无法转换为整数。")
            mapped_values_7.append('N/A')
            mapped_values_8.append('N/A')

    m8_df[6] = mapped_values_7
    m8_df[7] = mapped_values_8
    return m8_df

# 主程序
if __name__ == "__main__":
    # 获取 pdb 文件中的连续到不连续氨基酸信息映射
    residue_mapping = parse_pdb_residues(pdb_file_path)
    
    # 读取 m8 文件
    m8_df = read_m8_file(m8_file_path)
    
    # 重映射第七列和第八列
    mapped_m8_df = remap_columns(m8_df, residue_mapping)
    
    # 保存输出结果
    mapped_m8_df.to_csv(output_file_path, sep='\t', index=False, header=False)
    print(f"处理完成，输出文件已保存至: {output_file_path}")
