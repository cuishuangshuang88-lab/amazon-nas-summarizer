---
name: amazon-nas-summarizer
description: |
  亚马逊素材整理与分类脚本，自动扫描NAS共享文件夹并按类别（原图/说明书/线稿图/未知）
  整理到指定目录。支持断点续传、去重处理和生成详细报告。
tags: [nas, file-management, sorting, automation, smb]
version: 1.0.0
author: Chief & codex助手
license: MIT
---

# Amazon NAS Summarizer Skill

自动化整理亚马逊事业部NAS中的图片素材文件，按类型分类存储。

## 功能特性

- **自动扫描**: 递归扫描指定目录下的所有图片文件
- **智能分类**: 
  - `原图`: 效果图、高清图库素材等
  - `说明书`: PDF文档及标注为说明书的图片
  - `线稿图`: 技术图纸、设计草图
  - `未知`: UUID命名或其他无法识别的文件
- **去重处理**: 自动生成唯一文件名避免冲突
- **完整性校验**: 支持SHA256哈希验证文件完整性
- **断点续传**: 支持从上次中断处继续复制

## 使用方法

```bash
# 运行扫描和分类（默认dry-run模式）
python3 nas_sort.py

# 执行实际复制操作
python3 nas_sort.py --execute

# 校验复制结果
python3 nas_verify.py
python3 size_audit.py
```

## 配置说明

编辑 `nas_sort.py` 中的以下变量：

```python
ROOT = "/Volumes/Amazon事业部"           # NAS根目录
TESTDIR = os.path.join(ROOT, "崔双双测试勿删")  # 目标子目录
```

## 输出结构

```
崔双双测试勿删/
├── 亚马逊原图汇总/          # 原图存放位置
├── 亚马逊已经出单线稿图及说明书/  # 说明书+线稿图
└── 未知/                   # 无法分类的文件
```

## 注意事项

1. 首次运行建议先dry-run查看分类结果
2. 确保有足够的磁盘空间（预计需要源文件1.5倍空间）
3. SMB大文件传输可能需要较长时间
4. 使用danger-full-access权限避免沙箱限制

## 依赖要求

- Python 3.8+
- 无第三方依赖

## 版本历史

- v1.0.0 (2026-11-23): 初始版本，完成基础分类和复制功能
