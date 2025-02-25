#!/bin/bash

# 定义输入目录和输出目录
input_dir="/c/Users/SJTU/gos2/image"
output_dir="/c/Users/SJTU/gos2/orig_out"

# 检查输入目录是否存在
if [ ! -d "$input_dir" ]; then
    echo "输入目录不存在: $input_dir"
    exit 1
fi

# 确保输出目录存在
mkdir -p "$output_dir"

# 遍历输入目录中的所有 .gim 文件
for gim_file in "$input_dir"/*.gim; do
    # 检查文件是否存在
    if [ ! -f "$gim_file" ]; then
        echo "没有找到任何 .gim 文件在目录: $input_dir"
        exit 1
    fi

    # 获取文件名（不含路径和扩展名）
    filename=$(basename -- "$gim_file")
    filename="${filename%.*}"

    # 构造输出文件路径
    output_file="$output_dir/${filename}.png"

    # 调用 GimConv.exe 进行转换
    echo "正在转换: $gim_file -> $output_file"
    ./GimConv.exe "$gim_file" -o "$output_file"
done

echo "转换完成！"