#!/bin/bash

# 检查输入参数
if [ $# -ne 2 ]; then
    echo "Usage: $0 <target_pdbfile> <output_directory>"
    exit 1
fi

TARGET_PDBFILE=$1      # --pdbfile2 参数
OUTPUT_DIR=$2          # 用于存放生成的 mol1A.txt 文件
id=$(basename $1|sed "s/_[A-Z].pdb//g")
# 检查目标 PDB 文件是否存在
if [ ${#id} -gt 4 ]; then
    id=$(head /dev/urandom | tr -dc A-Za-z | head -c 4)
    echo "ID was too long, using random 4-letter ID: $id"
fi
if [ ! -f "$TARGET_PDBFILE" ]; then
    echo "Error: Target PDB file '$TARGET_PDBFILE' does not exist."
    exit 1
fi
./DaliLite.v5/bin/import.pl --pdbfile $TARGET_PDBFILE   --pdbid $id --dat global_database_v2/ --clean 
# 创建输出目录（如果不存在）
mkdir -p "$OUTPUT_DIR"

# 遍历 global_database_v2/ 目录中的所有包含 '_' 的文件
for i in $(ls global_database_v2/ | grep "_"); do
    INPUT_PDBFILE="global_database_v2/$i"
    
    # 检查输入 PDB 文件是否存在
    if [ ! -f "$INPUT_PDBFILE" ]; then
        echo "Warning: Input PDB file '$INPUT_PDBFILE' does not exist. Skipping."
        continue
    fi
    
    echo "Running DALI for $i against $(basename $TARGET_PDBFILE)..."
    
    # 运行 DALI
    ./DaliLite.v5/bin/dali.pl --pdbfile1 "$INPUT_PDBFILE" --pdbfile2 "$TARGET_PDBFILE" --dat1 global_database_v2/ --dat2 ./ --outfmt equivalences --clean
    
    # 检查 DALI 是否生成了 mol1A.txt 文件
    if [ -f "mol1A.txt" ]; then
        # 获取输入文件的基础名称（不含扩展名）
        BASENAME=$(basename "$i" | sed 's/\..*$//')
        
        # 重命名并移动 mol1A.txt 文件
        mv mol1A.txt "$OUTPUT_DIR/${BASENAME}_mol1A.txt"
        echo "Moved and renamed mol1A.txt to $OUTPUT_DIR/${BASENAME}_mol1A.txt"
    else
        echo "Warning: DALI did not generate mol1A.txt for $i."
    fi
done

echo "All DALI runs completed. Check the '$OUTPUT_DIR' directory for results."
