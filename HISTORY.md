# 简要历史

2010年，“EVA同好会”发布汉化信息

PSP掌机站相关报道（互联网档案馆存档）[神隐、EVA我的钢铁女友2完整汉化版近期发布](https://web.archive.org/web/20180603134541/http://psp.duowan.com/1007/142595251153.html)

7月，“天峰子”在新浪博客（互联网档案馆存档）发布测试信息和部分汉化截图

[PSP新世纪福音战士 钢铁的女友2【基情ＯＸ＝ＸＯ中](https://web.archive.org/web/20120715191454/http://blog.sina.com.cn/s/blog_4e57a4710100jtxx.html)

随后项目疑似弃坑。

---

2012年2月，电玩巴士论坛上 `licanranqy` 发布了题为“[应求上传 《新世纪福音战士 钢铁的女朋友2ND》汉化版（不完美，非官方）](https://web.archive.org/web/20120620133202/http://bbs.tgbus.com/thread-3116635-1-1.html)”的帖子，EVA同好会的汉化版本首次进入互联网。

------

与此同时，在西方世界：
+ 2016年前后，出现[英译](https://www.gamebrew.org/wiki/Shinseiki_Evangelion:_Koutetsu_no_Girlfriend_2nd_Portable_PSP_-_English_Translation)版本。
+ 2023年， `tehmugi` 将英译版本 `1.02` 发布于[GitHub](https://github.com/tehmugi/patches_release)

# “EVA同好会”完成的内容

> 2025年，经研究，发现2012年起在互联网流传的版本完成了下述工作

* 部分图片的替换
* 脚本对话部分的汉化
* 修改SJIS到UCS2（UTF16）的映射表，覆盖添加GB2312字符
* 修改PGF字体文件为微软雅黑

## 历史遗留BUG

* 部分翻译字符串内部存在CRLF换行符，导致脚本解析出错，程序崩溃
* 文本替换时出现非SJIS字符（属于CP932扩展），导致运行时无法正常显示，仅显示下划线占位符
# 修正

此次对旧版本的修改包括

* 字符串换行BUG修复
* 翻译文本调整
* 翻译菜单地名
* 字库修正
* 更新PIC0
* 更新开始页面菜单图片
