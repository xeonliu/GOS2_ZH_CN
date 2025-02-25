import struct
import zlib
import os
from pathlib import Path

# THFS文件头结构 (16字节)
THFS_HEADER_FORMAT = '4sIII'  # 小端模式
THFS_HEADER_SIZE = 16

# 条目结构 (64字节)
THFS_ENTRY_FORMAT = 'Q40sIIII'
THFS_ENTRY_SIZE = 64

def parse_thfs_file(thfs_path, output_dir):
    """解析THFS文件并提取内容"""
    try:
        with open(thfs_path, 'rb') as f:
            # 1. 读取并验证文件头
            header = f.read(THFS_HEADER_SIZE)
            if len(header) < THFS_HEADER_SIZE:
                raise ValueError("文件头不完整")

            magic, total_size, entry_count, reserved = struct.unpack(
                THFS_HEADER_FORMAT, header
            )
            
            if magic != b'THFS':
                raise ValueError("无效的THFS文件 (魔数不匹配)")
            
            print(f"THFS文件大小: {total_size} 字节")
            print(f"条目数量: {entry_count}")
            print(f"保留字段: {reserved}")

            # 2. 读取所有条目
            entries = []
            for _ in range(entry_count):
                entry_data = f.read(THFS_ENTRY_SIZE)
                if len(entry_data) < THFS_ENTRY_SIZE:
                    raise ValueError("条目数据不完整")

                # 解包条目数据
                (filename_hash, filename_bytes, 
                 start_addr, compressed_size, 
                 compression_flag, raw_size) = struct.unpack(
                    THFS_ENTRY_FORMAT, entry_data
                )[:6]  # 忽略末尾填充

                # 处理文件名 (移除零填充)
                filename = filename_bytes.split(b'\x00')[0].decode('shift-jis', errors='replace')
                
                entries.append({
                    'filename': filename,
                    'start_addr': start_addr,
                    'compressed_size': compressed_size,
                    'compression_flag': compression_flag,
                    'raw_size': raw_size
                })

            # 3. 提取文件数据
            for entry in entries:
                output_path = Path(output_dir) / entry['filename']
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # 定位到数据起始位置
                f.seek(entry['start_addr'])
                compressed_data = f.read(entry['compressed_size'])

                # 处理压缩
                if entry['compression_flag'] == 0x01:  # zlib压缩
                    try:
                        data = zlib.decompress(compressed_data)
                    except zlib.error as e:
                        print(f"解压失败: {entry['filename']} ({e})，尝试原始数据")
                        data = compressed_data
                else:  # 未压缩
                    data = compressed_data

                # 验证数据大小
                if entry['raw_size'] != 0 and len(data) != entry['raw_size']:
                    print(f"警告: {entry['filename']} 大小不匹配 "
                          f"(期望:{entry['raw_size']} 实际:{len(data)})")

                # 写入文件
                with open(output_path, 'wb') as out_file:
                    out_file.write(data)
                print(f"已提取: {entry['filename']}")

    except Exception as e:
        print(f"处理失败: {str(e)}")
        raise

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='THFS文件提取工具')
    parser.add_argument('input', help='输入THFS文件路径')
    parser.add_argument('-o', '--output', default='thfs_extracted', 
                       help='输出目录 (默认: thfs_extracted)')
    
    args = parser.parse_args()
    
    try:
        parse_thfs_file(args.input, args.output)
        print("提取完成！")
    except KeyboardInterrupt:
        print("用户中断操作")