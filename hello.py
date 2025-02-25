import struct
import zlib
import os
from pathlib import Path
import argparse
import hashlib

# THFS文件头结构 (16字节)
THFS_HEADER_FORMAT = '4sIII'  # 小端模式
THFS_HEADER_SIZE = 16
# 条目结构 (64字节)
THFS_ENTRY_FORMAT = 'Q40sIIII'
THFS_ENTRY_SIZE = 64


class THFSFile:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.entries = []
        self.header = None
        with open(self.file_path, 'rb') as f:
                # 1. 读取并验证文件头
                header = f.read(THFS_HEADER_SIZE)
                if len(header) < THFS_HEADER_SIZE:
                    raise ValueError("文件头不完整")
                magic, total_size, entry_count, reserved = struct.unpack(
                    THFS_HEADER_FORMAT, header
                )
                
                if magic != b'THFS':
                    raise ValueError("无效的THFS文件 (魔数不匹配)")
                
                self.header = {
                    'magic': magic,
                    'total_size': total_size,
                    'entry_count': entry_count,
                    'reserved': reserved
                }

                print(f"THFS文件大小: {total_size} 字节")
                print(f"条目数量: {entry_count}")
                print(f"保留字段: {reserved}")
                
                # 2. 读取所有条目
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
                    
                    self.entries.append({
                        'filename': filename,
                        'start_addr': start_addr,
                        'compressed_size': compressed_size,
                        'compression_flag': compression_flag,
                        'raw_size': raw_size,
                        'filename_hash': filename_hash
                    })

    def unpack(self, output_dir):
        """解析THFS文件并提取内容"""
        try:
            with open(self.file_path, 'rb') as f:
                # 3. 提取文件数据
                for entry in self.entries:
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

    def repack(self, input_dir, output_file):
        """重新打包THFS文件"""
        try:
            # 1. 读取原始文件头和条目信息
            with open(self.file_path, 'rb') as f:
                f.seek(THFS_HEADER_SIZE + len(self.entries) * THFS_ENTRY_SIZE)
                file_data = f.read()  # 读取原始文件数据部分

            # 2. 构建新的文件头和条目
            new_entries = []
            new_file_data = bytearray()
            current_offset = THFS_HEADER_SIZE + len(self.entries) * THFS_ENTRY_SIZE

            for entry in self.entries:
                input_path = Path(input_dir) / entry['filename']
                if not input_path.exists():
                    raise FileNotFoundError(f"文件未找到: {entry['filename']}")
                
                with open(input_path, 'rb') as in_file:
                    data = in_file.read()
                
                # 压缩数据
                compressed_data = zlib.compress(data) if entry['compression_flag'] == 0x01 else data
                compressed_size = len(compressed_data)
                raw_size = len(data)

                # 构建新条目
                new_entry = struct.pack(
                    THFS_ENTRY_FORMAT,
                    entry['filename_hash'],  # 使用原始文件名哈希
                    entry['filename'].encode('shift-jis').ljust(40, b'\x00'),  # 文件名
                    current_offset,  # 数据起始位置
                    compressed_size,  # 压缩后大小
                    entry['compression_flag'],  # 压缩标志
                    raw_size  # 原始大小
                )
                new_entries.append(new_entry)
                new_file_data.extend(compressed_data)
                current_offset += compressed_size

            # 3. 构建新的文件头
            new_header = struct.pack(
                THFS_HEADER_FORMAT,
                self.header['magic'],
                THFS_HEADER_SIZE + len(new_entries) * THFS_ENTRY_SIZE + len(new_file_data),
                len(self.entries),
                self.header['reserved']
            )

            # 4. 写入新的THFS文件
            with open(output_file, 'wb') as out_file:
                out_file.write(new_header)
                for entry in new_entries:
                    out_file.write(entry)
                out_file.write(new_file_data)

            print(f"重新打包完成: {output_file}")
        except Exception as e:
            print(f"处理失败: {str(e)}")
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='THFS文件处理工具')
    parser.add_argument('input', help='输入THFS文件路径或解包后的目录路径')
    parser.add_argument('-o', '--output', default='thfs_output', help='输出目录或打包后的文件路径')
    parser.add_argument('-f', '--folder', default='thfs_extracted', help='解包后的目录路径')
    parser.add_argument('-m', '--mode', choices=['unpack', 'repack'], default='unpack', help='操作模式 (unpack/repack)')

    args = parser.parse_args()

    try:
        thfs = THFSFile(args.input)
        if args.mode == 'unpack':
            thfs.unpack(args.output)
        elif args.mode == 'repack':
            thfs.repack(args.folder, args.output)
        print("操作完成！")
    except KeyboardInterrupt:
        print("用户中断操作")