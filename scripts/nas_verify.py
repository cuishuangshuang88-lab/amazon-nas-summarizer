#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核验 NAS 分类复制结果"""
import os
import csv

ROOT = "/Volumes/Amazon事业部"
BASE = os.path.join(ROOT, "崔双双测试勿删")
DIRS = ["亚马逊原图汇总", "亚马逊已经出单线稿图及说明书", "未知"]
EXPECT = {"原图": 3233, "说明书": 2083, "线稿图": 1432, "未知": 752}

def count_files(d):
    n = 0; size = 0
    for dp, _, fns in os.walk(d):
        for f in fns:
            if f.lower() in ('.ds_store', 'thumbs.db', 'desktop.ini'):
                continue
            n += 1
            try: size += os.path.getsize(os.path.join(dp, f))
            except OSError: pass
    return n, size

print("=== 目标文件夹核验 ===")
total_n = total_s = 0
for d in DIRS:
    n, s = count_files(os.path.join(BASE, d))
    total_n += n; total_s += s
    print(f"  {d}: {n} 个文件, {s/1024/1024/1024:.2f} GB")
print(f"  合计: {total_n} 个文件, {total_s/1024/1024/1024:.2f} GB")
print(f"  预期: 7500 个文件 -> {'通过' if total_n >= 7500 else '不符(差 %d)' % (7500-total_n)}")

print("\n=== 源文件保留核验 ===")
for d in ["亚马逊原图存放", "亚马逊线稿图说明书存放", "产品说明书", "亚马逊过年效果图", "图库", "生产资料"]:
    p = os.path.join(ROOT, d)
    if os.path.isdir(p):
        n, s = count_files(p)
        print(f"  {d}: {n} 个文件, {s/1024/1024/1024:.2f} GB")

print("\n=== 清单CSV核对 ===")
manifest = "/Users/mima0000/.dsh/bot/workspace/classification_manifest.csv"
if os.path.exists(manifest):
    with open(manifest, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    print(f"  表头: {header}")
    print(f"  数据行: {len(rows)}")
else:
    print("  清单文件不存在")
