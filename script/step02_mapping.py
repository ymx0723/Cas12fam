import re
import sys

# 读取映射文件并构建映射字典
mapping = {}
with open(sys.argv[1], 'r') as f:
    # 跳过前两行（标题和空行）
    lines = f.readlines()[2:]
    for line in lines:
        original, renum = line.split()  # original 是第一列，renum 是第二列
        mapping[renum] = original  # 使用 renum（新数字）作为键，original（旧数字）作为值

# 读取 sword.txt 文件进行处理
with open(sys.argv[2], 'r') as f:
    sword_lines = f.readlines()

# 替换数字的函数
def replace_numbers(match):
    # 获取匹配到的数字范围
    numbers = match.group(0).split('-')  # 如果是范围（例如 1-143），分成两部分
    # 替换范围内的每个数字
    numbers = [mapping.get(num, num) for num in numbers]  # 查找映射并替换
    return '-'.join(numbers)  # 返回替换后的范围

# 处理文件中的 * 所在的行
modified_lines = []
for line in sword_lines:
    # 只处理包含 * 的行
    if '*' in line:
        # 使用正则表达式找到所有数字范围，并进行替换
        line = re.sub(r'\b(\d+(-\d+)?)\b', replace_numbers, line)
    
    # 将修改后的行保存到新的列表
    modified_lines.append(line)

# 输出修改后的文件内容到一个新文件
with open(sys.argv[3], 'w') as f:
    f.writelines(modified_lines)

# 正确输出文件名
print(f"File has been modified and saved as '{sys.argv[3]}'")

