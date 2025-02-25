import codecs
import json

def read_utf16_file(file_path):
    """
    从文件中读取内容，以小端UTF-16格式两个字节两个字节地读取，并返回翻译后的字符列表。
    :param file_path: 文件路径
    :return: 翻译后的字符列表
    """
    try:
        # 打开文件，以二进制模式读取
        with open(file_path, 'rb') as file:
            # 初始化字符列表
            characters = []
            # 每次读取两个字节
            while True:
                # 读取两个字节
                bytes_chunk = file.read(2)
                # 如果读取到的字节不足两个字节，说明已经读取到文件末尾，退出循环
                if len(bytes_chunk) < 2:
                    break
                # 将两个字节转换为小端UTF-16编码的字符
                try:
                    char = bytes_chunk.decode('utf-16le')
                    characters.append(char)
                except UnicodeDecodeError:
                    # 如果无法解码，跳过这两个字节
                    print(f"Skipping invalid UTF-16 bytes: {bytes_chunk.hex()}")
        return characters
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def write_utf16_file(file_path, characters):
    """
    将字符列表写入文件，以小端UTF-16格式两个字节两个字节地写入。
    :param file_path: 文件路径
    :param characters: 要写入的字符列表
    """
    try:
        # 打开文件，以二进制模式写入
        with open(file_path, 'wb') as file:
            # 逐个字符写入
            for char in characters:
                # 将字符编码为小端UTF-16格式的字节
                bytes_chunk = char.encode('utf-16le')
                # 写入文件
                file.write(bytes_chunk)
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"Failed to save data to file: {e}")

def is_valid_sjis(byte1, byte2):
    """
    检查两个字节是否是有效的 SJIS 字符。
    """
    return (0x81 <= byte1 <= 0x9F or 0xE0 <= byte1 <= 0xEF) and (0x40 <= byte2 <= 0xFC and byte2 != 0x7F)

def traverse_sjis():
    """
    遍历 SJIS 字符集中的字符，并将其转换为 Unicode 字符。
    """
    sjis_characters = []

    # 遍历 SJIS 字符集中的所有可能的字节组合
    for byte1 in range(0x85, 0xFF):
        for byte2 in range(0x40, 0xFF):
            if is_valid_sjis(byte1, byte2):
                try:
                    sjis_bytes = bytes([byte1, byte2])
                    sjis_char = sjis_bytes.decode('shift_jis')
                    sjis_characters.append(sjis_char)
                except UnicodeDecodeError:
                    continue

    return sjis_characters

def modify_table(characters, new_characters):
    """
    修改字符列表中的字符，覆盖填充new_characters。
    """
    # 取SJIS字符集，依次使用new_characters填充
    sjis_characters = traverse_sjis()
    print(sjis_characters)
    mapping_dict = {}
    for i in range(min(len(sjis_characters), len(new_characters))):
        mapping_dict[sjis_characters[i]] = new_characters[i]
    for i in range(len(characters)):
        if characters[i] in mapping_dict:
            characters[i] = mapping_dict[characters[i]]
    return characters
        
def create_dict_from_arrays(array1, array2):
    """
    根据两个字符数组创建一个字典，按位置一对一映射。
    :param array1: 第一个字符数组
    :param array2: 第二个字符数组
    :return: 映射后的字典
    """
    # 确保两个数组长度一致
    min_length = min(len(array1), len(array2))
    print(min_length)
    mapping_dict = {}
    for i in range(min_length):
        mapping_dict[array1[i]] = array2[i]
    return mapping_dict

def save_to_json(data, output_path):
    """
    将数据保存为JSON文件。
    :param data: 要保存的数据
    :param output_path: 输出文件路径
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {output_path}")
    except Exception as e:
        print(f"Failed to save data to JSON file: {e}")
        

if __name__ == '__main__':
    # 读取文件
    from paratranz import translation_list, count_characters
    import argparse
    
    # Parse args
    parser = argparse.ArgumentParser(description="Process some files.")
    parser.add_argument('--orig_table', type=str, default="jpn_font/jis2ucs.bin", help='Original table file path')
    parser.add_argument('--file_path', type=str, default="all_mappings.json", help='File path for translations')
    parser.add_argument('--output_file', type=str, default="chs_font/jis2ucs.bin", help='Output file path')
    args = parser.parse_args()

    orig_table = args.orig_table
    file_path = args.file_path
    output_file = args.output_file
    
    translations = translation_list(file_path)
    chs_characters = count_characters(translations)
    
    # Read Table
    characters = read_utf16_file(orig_table)
    # Modify Table
    merged_characters = modify_table(characters, chs_characters)
    write_utf16_file(output_file, merged_characters)
    
    characters = read_utf16_file(orig_table)
    res = create_dict_from_arrays(characters, merged_characters)
    save_to_json(res, "output_mapping.json")