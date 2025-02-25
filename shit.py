import os

def count_crlf_lines(file_path):
    """
    计算文件中CRLF行数。
    :param file_path: 文件路径
    :return: CRLF行数
    """
    crlf_count = 0
    try:
        with open(file_path, "rb") as file:
            for line in file:
                if line.endswith(b"\r\n"):
                    crlf_count += 1
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return crlf_count


def compare_folders(folder1, folder2):
    """
    比较两个文件夹中文件的CRLF行数。
    :param folder1: 第一个文件夹路径
    :param folder2: 第二个文件夹路径
    """
    # 获取两个文件夹中的文件列表
    files1 = set(os.listdir(folder1))
    files2 = set(os.listdir(folder2))

    # 检查文件夹中的文件是否一致
    if files1 != files2:
        print("两个文件夹中的文件不一致！")
        print("仅在第一个文件夹中存在的文件：", files1 - files2)
        print("仅在第二个文件夹中存在的文件：", files2 - files1)
        return

    # 比较每个文件的CRLF行数
    for file_name in files1:
        file_path1 = os.path.join(folder1, file_name)
        file_path2 = os.path.join(folder2, file_name)

        crlf_count1 = count_crlf_lines(file_path1)
        crlf_count2 = count_crlf_lines(file_path2)

        if crlf_count1 != crlf_count2:
            print(f"文件 {file_name} 的CRLF行数不一致：")
            print(f"  文件夹 {folder1}: {crlf_count1} 行")
            print(f"  文件夹 {folder2}: {crlf_count2} 行")
        # else:
            # print(f"文件 {file_name} 的CRLF行数一致：{crlf_count1} 行")


# 主函数
if __name__ == "__main__":
    folder1 = input("请输入第一个文件夹路径：")
    folder2 = input("请输入第二个文件夹路径：")

    if not os.path.isdir(folder1) or not os.path.isdir(folder2):
        print("输入的路径无效，请确保路径是文件夹！")
    else:
        compare_folders(folder1, folder2)