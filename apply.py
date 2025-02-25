import os
import re
import json

# 设置文件夹路径
input_folder_path = "./jpn"
output_folder_path = "./chs_translated"

# 从 output_mapping.json 文件中读取字符转换字典
with open('output_mapping.json', 'r', encoding='utf-8') as f:
    char_conversion_dict = json.load(f)
    
# 反转字符转换字典
char_conversion_dict = {value: key for key, value in char_conversion_dict.items()}

# 确保输出文件夹存在
os.makedirs(output_folder_path, exist_ok=True)

# 读取 all_mappings.json 文件
with open('all_mappings.json', 'r', encoding='utf-8') as f:
    all_mappings = json.load(f)

# 创建一个字典用于快速查找翻译
translation_dict = {mapping['original']: mapping['translation'] for mapping in all_mappings}

# 遍历文件夹中的所有文件
for filename in os.listdir(input_folder_path):
    input_file_path = os.path.join(input_folder_path, filename)
    output_file_path = os.path.join(output_folder_path, filename)
    
    # 以二进制模式读取文件
    with open(input_file_path, "rb") as file:
        content = file.read()
        
        # 使用正则表达式匹配双引号包裹的内容
        matches = re.findall(rb'"(.+?)"', content, re.DOTALL)
        
        # 替换匹配到的内容
        for match in matches:
            # 将匹配到的二进制内容解码为字符串（忽略解码错误）
            text = match.decode("shift_jis", errors="ignore")
            
            # 跳过纯 ASCII 字符串
            if all(ord(char) < 128 for char in text):
                continue
            
            # 查找翻译并转换字符串中的字符
            if text in translation_dict:
                translation = translation_dict[text]
                # TODO：若无匹配，报错
                try:
                    converted_text = ''.join(char_conversion_dict[char] for char in translation)
                except KeyError as e:
                    print(f"未找到字符: {e.args[0]}")
                    converted_text = ''.join(char_conversion_dict.get(char, char) for char in translation)
                    # raise ValueError(f"字符转换字典中缺少字符: {e.args[0]}") from e
                
                # 将转换后的字符串编码为二进制
                converted_bytes = converted_text.encode("cp932", errors="error")
                # 使用正则表达式替换原始内容，确保只替换双引号包裹的内容
                # content = re.sub(rb'(?<=\")' + re.escape(match) + rb'(?=\")', converted_bytes, content)
                print(f"翻译: {translation}")
                print(f"转换: {converted_text}")
                escaped_match = b''.join(
                    f'\\x{b:02x}'.encode('latin-1')  # 先格式化为字符串，再编码为字节
                    for b in match
                )
                pattern = rb'(?<=")' + escaped_match + rb'(?=")'
                content = re.sub(pattern, converted_bytes, content)
            else:
                print(f"未找到翻译: {repr(text)}")
                text = text.replace(" ", "")
                if text in translation_dict:
                    # print(f"尝试移除空格后的翻译: {repr(text)}")
                    translation = translation_dict[text]
                    print(f"翻译: {translation}")
                    try:
                        converted_text = ''.join(char_conversion_dict[char] for char in translation)
                    except KeyError as e:
                        print(f"未找到字符: {e.args[0]}")
                        converted_text = ''.join(char_conversion_dict.get(char, char) for char in translation)
                    # 将转换后的字符串编码为二进制
                    converted_bytes = converted_text.encode("cp932", errors="warn")
                    
                    # 使用正则表达式替换原始内容，确保只替换双引号包裹的内容
                    content = re.sub(rb'(?<=\")' + re.escape(match) + rb'(?=\")', converted_bytes, content)
    
    # 以二进制模式写回文件到输出文件夹
    with open(output_file_path, "wb") as file:
        file.write(content)