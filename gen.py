import codecs

# 定义 SJIS 和 GB2312 的范围
sjis_ranges = [
    (0x8140, 0x9FFC),  # SJIS 范围
    (0xE040, 0xEAA4)   # SJIS 扩展范围
]

gb2312_ranges = [
    (0xA1A1, 0xFEFE)  # GB2312 范围
]

def is_valid_sjis(byte1, byte2):
    return (0x81 <= byte1 <= 0x9F or 0xE0 <= byte1 <= 0xEF) and (0x40 <= byte2 <= 0xFC and byte2 != 0x7F)

def is_valid_gb2312(byte1, byte2):
    return (0xA1 <= byte1 <= 0xF7) and (0xA1 <= byte2 <= 0xFE)

# 打开输出文件
with codecs.open('output.txt', 'w', 'utf-8') as f:
    # 生成所有有效的 SJIS 字符
    for byte1 in range(0x81, 0xFF):
        for byte2 in range(0x40, 0xFF):
            if is_valid_sjis(byte1, byte2):
                try:
                    sjis_bytes = bytes([byte1, byte2])
                    sjis_char = sjis_bytes.decode('shift_jis')
                    utf16_hex = sjis_char.encode('utf-16-be').hex().upper()
                    f.write(utf16_hex + '\n')
                except UnicodeDecodeError:
                    continue

    # 生成所有有效的 GB2312 字符
    for byte1 in range(0xA1, 0xFF):
        for byte2 in range(0xA1, 0xFF):
            if is_valid_gb2312(byte1, byte2):
                try:
                    gb2312_bytes = bytes([byte1, byte2])
                    gb2312_char = gb2312_bytes.decode('gb2312')
                    utf16_hex = gb2312_char.encode('utf-16-be').hex().upper()
                    f.write(utf16_hex + '\n')
                except UnicodeDecodeError:
                    continue
    
    # 生成ASCII字符
    for byte in range(0x20, 0x7F):
        f.write(hex(byte)[2:].upper() + '\n')