import os
import json

# 设置文件路径
translation_file_path = "./all_mappings.json"

# 读取翻译文件
with open(translation_file_path, 'r', encoding='utf-8') as f:
    all_mappings = json.load(f)

# 找到所有含有假名的字符串
kana_strings = []

# 定义平假名和片假名的 Unicode 范围
hiragana_range = (0x3040, 0x309F)
katakana_range = (0x30A0, 0x30FF)

def contains_kana(s):
    return any(hiragana_range[0] <= ord(char) <= hiragana_range[1] or
               katakana_range[0] <= ord(char) <= katakana_range[1] for char in s)

for mapping in all_mappings:
    original = mapping.get('original', '')
    translation = mapping.get('translation', '')
    if contains_kana(translation):
        kana_strings.append(translation)
        # kana_strings.append(original)

# 打印含有假名的字符串
print("以下字符串含有假名：")
for string in kana_strings:
    print(string)