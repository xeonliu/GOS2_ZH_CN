#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from gim import gim2png, png2gim
import io


def batch_convert(input_dir, output_dir, mode='gim2png', recursive=True, verbose=False):
    """
    批量转换GIM文件
    
    Args:
        input_dir: 输入文件夹
        output_dir: 输出文件夹
        mode: 转换模式 ('gim2png' 或 'png2gim')
        recursive: 是否递归处理子文件夹
        verbose: 是否显示详细日志
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 验证输入文件夹
    if not input_path.exists() or not input_path.is_dir():
        print(f'Error: Input directory not found: {input_path}', file=sys.stderr)
        sys.exit(1)
    
    # 创建输出文件夹
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 确定文件扩展名
    if mode == 'gim2png':
        input_ext = '*.gim'
        output_ext = '.png'
        conversion_func = gim2png
    else:  # png2gim
        input_ext = '*.png'
        output_ext = '.gim'
        conversion_func = png2gim
    
    # 查找文件
    if recursive:
        files = list(input_path.rglob(input_ext))
    else:
        files = list(input_path.glob(input_ext))
    
    if not files:
        print(f'No {input_ext} files found in {input_path}')
        return 0
    
    print(f'Found {len(files)} files to convert')
    print()
    
    success_count = 0
    error_count = 0
    
    for idx, input_file in enumerate(files, 1):
        try:
            # 计算相对路径，保留目录结构
            rel_path = input_file.relative_to(input_path)
            output_file = output_path / rel_path.with_suffix(output_ext)
            
            # 创建输出文件的父目录
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if verbose:
                print(f'[{idx}/{len(files)}] {rel_path}', end=' ... ')
            else:
                print(f'[{idx}/{len(files)}] ', end='', flush=True)
            
            # 读取输入文件
            with open(input_file, 'rb') as f:
                input_data = f.read()
            
            # 转换
            if mode == 'gim2png':
                class Args:
                    verbose = False
                
                with gim2png(input_data, Args()) as im:
                    im.save(output_file)
            else:  # png2gim
                class Args:
                    gim_pixel_order = False
                    gim_byteorder = 'little'
                    gim_project_name = 'GIM Project'
                    gim_user_name = 'User'
                    gim_no_fileinfo = False
                    gim_saved_date = None
                    gim_originator = None
                
                output_data = png2gim(input_data, Args())
                with open(output_file, 'wb') as f:
                    f.write(output_data)
            
            if verbose:
                print(f'✓ -> {output_file.name}')
            else:
                print('✓', end=' ', flush=True)
            
            success_count += 1
        
        except Exception as e:
            if verbose:
                print(f'✗ Error: {e}')
            else:
                print('✗', end=' ', flush=True)
            error_count += 1
            if verbose:
                import traceback
                traceback.print_exc()
    
    print()
    print()
    print(f'Complete: {success_count} successful, {error_count} failed')
    
    return 0 if error_count == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description='Batch convert GIM images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s input_folder output_folder
  %(prog)s input_folder output_folder -m png2gim
  %(prog)s input_folder output_folder --no-recursive --verbose
        '''
    )
    
    parser.add_argument('input_dir',
                        help='Input directory containing GIM files')
    
    parser.add_argument('output_dir',
                        help='Output directory for converted files')
    
    parser.add_argument('-m', '--mode',
                        choices=['gim2png', 'png2gim'],
                        default='gim2png',
                        help='Conversion mode (default: gim2png)')
    
    parser.add_argument('--no-recursive',
                        action='store_false',
                        dest='recursive',
                        help='Do not process subdirectories')
    
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Verbose output with detailed information')
    
    args = parser.parse_args()
    
    return batch_convert(
        args.input_dir,
        args.output_dir,
        mode=args.mode,
        recursive=args.recursive,
        verbose=args.verbose
    )


if __name__ == '__main__':
    sys.exit(main())
