import os
import re
import json

# 设置文件夹路径
folder_path1 = "./jpn"
folder_path2 = "./chs"

# 从 output_mapping.json 文件中读取字符转换字典
with open('output_mapping.json', 'r', encoding='utf-8') as f:
    char_conversion_dict = json.load(f)

# 存储所有文件的映射
all_mappings = []

# 遍历第一个文件夹中的所有文件
for filename in os.listdir(folder_path1):
    file_path1 = os.path.join(folder_path1, filename)
    file_path2 = os.path.join(folder_path2, filename)
    
    # 确保第二个文件夹中也有相同的文件
    if os.path.exists(file_path2):
        # 以二进制模式读取文件
        with open(file_path1, "rb") as file1, open(file_path2, "rb") as file2:
            content1 = file1.read()
            content2 = file2.read()
            
            # 使用正则表达式匹配双引号包裹的内容
            matches1 = re.findall(rb'"(.+?)"', content1, re.DOTALL)
            matches2 = re.findall(rb'"(.+?)"', content2, re.DOTALL)
            
            # 转换匹配到的字符串
            converted_matches2 = []
            for match in matches2:
                text = match.decode("shift_jis", errors="replace")
                converted_text = ''.join(char_conversion_dict.get(char, char) for char in text)
                converted_matches2.append(converted_text)
            
            # 建立映射
            mapping = dict(zip(matches1, converted_matches2))
            
            # 去除mapping中只含有ascii字符的项
            mapping = {key.decode("shift_jis", errors="replace"): value for key, value in mapping.items() if not all(ord(char) < 128 for char in key.decode("shift_jis", errors="ignore"))}
            
            # 打印映射
            print(f"文件 {filename} 的映射：")
            for key, value in mapping.items():
                print(f"{key} -> {value}")
            
            # 添加到总映射列表
            # 如果key已经存在，不添加
            for key, value in mapping.items():
                if not any(existing_mapping["key"] == key for existing_mapping in all_mappings):
                    all_mappings.append({"key": key, "original": key, "translation": value, "context": filename})

# 将所有映射保存到一个文件中
with open("output/all_mappings.json", 'w', encoding='utf-8') as json_file:
    json.dump(all_mappings, json_file, ensure_ascii=False, indent=4)