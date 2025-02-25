import collections
import json
"""
统计字数信息
"""
def count_characters(strs):
    text = ''.join(strs)
    counter = collections.Counter(text)
    sorted_characters = sorted(counter.items(), key=lambda item: item[1], reverse=True)
    # Exclude ASCII characters
    return [char for char, count in sorted_characters if '\u4e00' <= char <= '\u9fff']

def translation_list(file):
    with open(file, 'r', encoding='utf-8') as f:
        all_mappings = json.load(f)
    translations = [entry['translation'] for entry in all_mappings]
    print(f"Loaded {len(translations)} translations")
    return translations

"""
下载翻译文件
"""

if __name__ == '__main__':
    # 读取文件
    file_path = "all_mappings.json"
    translations = translation_list(file_path)
    characters = count_characters(translations)
    print(characters)