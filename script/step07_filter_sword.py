import re
import sys

def read_file(file_name):
    with open(file_name, 'r') as file:
        return file.readlines()

def has_conflict(current_boundary, sub_boundaries):
    current_start, current_end, current_annotation = current_boundary
    print(f"Checking current boundary {current_start}-{current_end}({current_annotation}) with sub-boundaries...")
    
    for sub_start, sub_end, sub_annotation in sub_boundaries:
        print(f"    Comparing with sub-boundary {sub_start}-{sub_end}({sub_annotation})")
        
        # 输出调试信息
        print(f"    current_start == sub_start: {current_start == sub_start}, current_end == sub_end: {current_end == sub_end}")
        print(f"    current_annotation == sub_annotation: {current_annotation == sub_annotation}")
        
        # 检查是否有相同位置，但注释不同的情况
        if current_start == sub_start and current_end == sub_end and current_annotation != sub_annotation:
            print(f"    Conflict found: Sub-boundary {sub_start}-{sub_end}({sub_annotation}) conflicts with current annotation {current_annotation}")
            print(f"    Warning: The boundary {sub_start}-{sub_end} has the same position but different annotation ({current_annotation}, {sub_annotation}).")
            return False  # 不删除，只标记冲突
        
        # 如果子区间完全包含在当前区间内，则标记为冲突
        if sub_start >= current_start and sub_end <= current_end:
            print(f"    Conflict found: Sub-boundary {sub_start}-{sub_end}({sub_annotation}) is nested within parent boundary {current_start}-{current_end}({current_annotation})")
            return True
    
    return False

def check_and_fill_gap(boundaries, all_boundaries):
    """
    检查区间是否连续，并填补间隙
    """
    filled_boundaries = []
    previous_end = None  # 记录上一个区间的结束位置
    # print(all_boundaries)
    # 按起始位置排序
    boundaries.sort(key=lambda x: x[0])

    # 已经使用过的区间，避免重复
    used_boundaries = set((b[0], b[1]) for b in boundaries)

    for i, (start, end, annotation) in enumerate(boundaries):
        if previous_end is None:
            filled_boundaries.append((start, end, annotation))
            previous_end = end
            continue

        # 检查当前区间是否和前一个区间有间隙
        if start > previous_end + 5:  # Gap threshold of 5
            gap_start = previous_end
            gap_end = start
            print(f"Gap found between {gap_start} and {gap_end}. Trying to fill the gap...")

            # 找到所有与间隙有重叠的区间
            possible_fillers = []
            for gap_boundary in all_boundaries:
                b_start, b_end, b_annotation = gap_boundary
            
                # 检查是否与间隙有重叠
                overlap_start = max(gap_start, b_start)
                overlap_end = min(gap_end, b_end)
                print(gap_boundary)
                if  (b_start, b_end) not in used_boundaries:
                    # 计算重叠长度
                    overlap_length = overlap_end - overlap_start
                    if overlap_length > 0:  # 确保有重叠
                        # 计算与间隙的距离
                        start_distance = abs(b_start - gap_start)
                        end_distance = abs(b_end - gap_end)
                        total_distance = start_distance + end_distance  # 总距离

                        # 打印每个候选区间的距离信息
                        print(f"    Candidate boundary: {b_start}-{b_end}({b_annotation})")
                        print(f"    Overlap length: {overlap_length}, Start distance: {start_distance}, End distance: {end_distance}, Total distance: {total_distance}")

                        # 用重叠长度和距离来判断最佳填补区间
                        possible_fillers.append((overlap_length, total_distance, gap_boundary))

            if possible_fillers:
                # 按照重叠长度降序，距离升序排列，选择最佳区间
                possible_fillers.sort(key=lambda x: (x[0], x[1]))
                _, _, best_filler = possible_fillers[0]
                b_start, b_end, b_annotation = best_filler
                filled_boundaries.append((b_start, b_end, b_annotation))
                used_boundaries.add((b_start, b_end))
                previous_end = b_end  # 更新结束位置
                print(f"    Filling gap with boundary {b_start}-{b_end}({b_annotation})")
            else:
                print("    No suitable boundary found to fill the gap.")

        # 添加当前区间
        filled_boundaries.append((start, end, annotation))
        used_boundaries.add((start, end))
        previous_end = end

    return filled_boundaries

    
def process_boundaries(lines):
    all_boundaries = []

    # 正则表达式匹配区间及其注释
    boundary_pattern = re.compile(r'(\d+)-(\d+)\(([\w\-]+)\)')

    # 遍历每一行，提取所有区间及其注释
    for line_num, line in enumerate(lines, 1):
        if not line.strip() or '*' not in line:
            continue
        
        # 使用正则表达式查找所有可能的区间注释
        matches = boundary_pattern.findall(line)
        if matches:
            for match in matches:
                start, end, annotation = match
                if (int(start), int(end), annotation) not in all_boundaries:
                    all_boundaries.append((int(start), int(end), annotation))
                else:
                    print(f"Warning: Duplicate boundary {start}-{end}({annotation}) found at line {line_num}")
        else:
            print(f"Warning: No valid boundaries found at line {line_num}: {line.strip()}")

    # all_boundaries.sort(key=lambda x: x[0])
    all_boundaries.sort(key=lambda x: x[0])
    # print(all_boundaries)
    print(f"Total boundaries after extraction and sorting by start: {len(all_boundaries)}")
    print(all_boundaries)

    # 用于替换注释逻辑：检查区间前面是否有Ruvc注释的区间，若有则替换当前区间的WED为NUC
    for i in range(1, len(all_boundaries)):
        start, end, annotation = all_boundaries[i]
        print
        # 检查当前区间之前的所有区间，是否有包含Ruvc的区间，且当前区间为WED
        for j in range(i):
            if 'RuvC'in all_boundaries[j][2] and 'WED' in annotation:
                print(f"Replacing WED with NUC for boundary {start}-{end}")
                all_boundaries[i] = (start, end, annotation.replace('WED', 'NUC'))
                break
    all_boundaries.sort(key=lambda x: -(x[1] - x[0]))  # 按区间长度降序排列
    print(f"Total boundaries after sorting by length: {len(all_boundaries)}")
    # 打印提取的所有区间信息
    print(f"Total boundaries after extraction and sorting by start: {len(all_boundaries)}")
    
    cleaned_boundaries = []
    visited = set()
    
    for i, (start, end, annotation) in enumerate(all_boundaries):
        current_boundary = (start, end, annotation)
        print(f"Processing boundary {start}-{end}({annotation})")

        # 找出当前区间包含的所有子区间
        sub_boundaries = [
            b for j, b in enumerate(all_boundaries)
            if j != i and b[0] >= start and b[1] <= end
        ]
        
        print(f"    Found {len(sub_boundaries)} sub-boundaries for {start}-{end}({annotation})")

        # 判断子区间是否存在冲突
        if has_conflict((start, end, annotation), sub_boundaries):
            print(f"    Boundary {start}-{end}({annotation}) has conflicts and is deleted.")
        else:
            if current_boundary not in visited:
                cleaned_boundaries.append(current_boundary)
                visited.add(current_boundary)
                print(f"    Boundary {start}-{end}({annotation}) retained.")
    
    print("Checking and filling gaps in the cleaned boundaries...")
    final_boundaries = check_and_fill_gap(cleaned_boundaries, all_boundaries)

    # 打印调整后的区间信息
    print("Checking and filling gaps in the cleaned boundaries...")
    final_boundaries = check_and_fill_gap(cleaned_boundaries, all_boundaries)

    # 打印调整后的区间信息
    print(f"Total boundaries after filling gaps: {len(final_boundaries)}")

    # 去除冗余的部分，确保没有完全重复的区间
    final_boundaries_cleaned = []
    seen = set()
    for boundary in final_boundaries:
        if (boundary[0], boundary[1]) not in seen:
            final_boundaries_cleaned.append(boundary)
            seen.add((boundary[0], boundary[1]))
        else:
            print(f"Duplicate boundary {boundary[0]}-{boundary[1]}({boundary[2]}) removed from final list.")

    # 对输出的区间按起始位置排序
    final_boundaries_cleaned.sort(key=lambda x: x[0])
    print(f"Total boundaries after cleaning: {len(final_boundaries_cleaned)}")

    return final_boundaries_cleaned

def write_cleaned_boundaries(file_name, boundaries):
    with open(file_name, 'w') as file:
        for start, end, annotation in boundaries:
            file.write(f"{start}-{end}({annotation})\n")

# 读取文件内容
file_name = sys.argv[1]
lines = read_file(file_name)

# 处理区间注释
processed_boundaries = process_boundaries(lines)

# 写入清理后的区间到新文件
output_file_name = sys.argv[2]
write_cleaned_boundaries(output_file_name, processed_boundaries)

print(f"清理后的注释区间已保存到 {output_file_name}")