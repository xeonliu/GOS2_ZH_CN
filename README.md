# 新世纪福音战士 钢铁女友2nd 汉化仓库

基于2010年“EVA同好会”的翻译文本，参见 `HISTORY.md`

# 修正
* “有”和“代”误用非`SJIS`字符“㈲”“㈹”。
* 菜单地名未翻译
* 翻译错误的地名
# License
* 翻译文本依据 `CC-BY-NC` 协议开源
* 程序按 `MIT` 协议开源
# 贡献

## 翻译/校对/润色

项目位于[Paratranz平台](https://paratranz.cn/projects/13612)

## 开发

### USRDIR目录内容

* `UTILS`：存档图片
* `SCRIPTS`：脚本文件（文本）
* `FONTS`：`SJIS`到`UCS2`的码表以及PGF字库

### THFS文件格式

> 参考： 2015年1月32日
>  
> [Evangelion: Girlfriend of Steel 2nd the THFS file structure.](https://web.archive.org/web/20180910161542/https://bbs.blacklabel-translations.com/showthread.php?tid=61)

```C
struct THFS_Header {
    uint32_t magic;       // 0x00: "THFS"签名（0x54484653）
    uint32_t totalSize;   // 0x04: 文件总大小
    uint32_t entryCount;  // 0x08: 文件条目数（对应代码中的param_1 + 8）
    uint32_t reserved;    // 0x0C: 保留字段
};
```

```C
struct THFS_Entry {
    uint64_t filenameHash; // 0x00-0x07: 文件名哈希
    char     filename[]; // 0x08-0x2F: 文件名（零填充）
    uint32_t startAddr;    // 0x30: 文件起始地址
    uint32_t compressedSize; //0x34: 压缩后大小
    uint32_t compressionFlag;//0x38: 压缩标志（0x01=启用zlib）
    uint32_t rawSize;      // 0x3C: 原始大小
}; // 文章指出条目占0x40字节
```

···
python ./hello.py 'e:/PSP_GAME/USRDIR/SCRIPT.THFS' -f chs_translated/ -o 'd:/EmulatorROM/gos/PSP_GAME/USRDIR/SCRIPT.THFS' -m repack

···