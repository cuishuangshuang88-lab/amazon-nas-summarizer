#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""亚马逊事业部素材分类汇总工具"""
import os
import re
import sys
import shutil
import csv
from pathlib import Path
from collections import Counter

# === 配置区域 ===
ROOT = "/Volumes/Amazon事业部"
TESTDIR = os.path.join(ROOT, "崔双双测试勿删")
DST_RAW = os.path.join(TESTDIR, "亚马逊原图汇总")
DST_LINE = os.path.join(TESTDIR, "亚马逊已经出单线稿图及说明书")
DST_UNKNOWN = os.path.join(TESTDIR, "未知")

MANIFEST_PATH = "/Users/mima0000/.dsh/bot/workspace/classification_manifest.csv"

# 排除的顶层目录
EXCLUDE_TOP = {
    "RECYCLER", "Temp", "迅雷云盘", "崔双双测试勿删",
    "会议纪要", "亚马逊推广关键词", "岗位案例库",
}

# 系统隐藏文件
SYSFILES = {".ds_store", "thumbs.db", "desktop.ini"}

# 媒体扩展名
MEDIA_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".pdf", ".cdr"}

# 正则表达式
UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
HEX_RE = re.compile(r'^[0-9a-f]{16,}$', re.I)
NUM_RE = re.compile(r'^\d+$')
FUZZY_KW = ("主图", "未标题", "untitled", "img_", "dsc_", "微信图片")


def classify(filename):
    """根据文件名智能分类"""
    stem = Path(filename).stem
    lower = filename.lower()
    
    # 优先判断说明书
    if "说明书" in filename or lower.endswith(".pdf"):
        return "说明书"
    
    # 判断线稿图
    if "线稿" in filename or "图纸" in filename:
        return "线稿图"
    
    # 判断未知类（UUID/哈希/纯数字/模糊关键词）
    if (UUID_RE.match(stem) or HEX_RE.match(stem) or NUM_RE.match(stem)
            or any(k in lower for k in FUZZY_KW)):
        return "未知"
    
    # 默认为原图
    return "原图"


def get_target_path(src_full, category):
    """生成目标路径，保持层级结构"""
    rel = os.path.relpath(src_full, ROOT)
    parts = Path(rel).parts
    
    # 提取作者名（第二级目录或第一级）
    source_dir = parts[0] if len(parts) > 0 else "未分类"
    author = parts[1] if len(parts) > 1 else source_dir
    
    # 确定目标根目录
    dst_root = {
        "原图": DST_RAW,
        "说明书": DST_LINE,
        "线稿图": DST_LINE,
        "未知": DST_UNKNOWN
    }[category]
    
    # 构建目标路径
    sub_path = list(parts[2:]) if len(parts) > 2 else []
    target = os.path.join(dst_root, author, source_dir, *sub_path, Path(src_full).name)
    
    return target


def scan():
    """扫描并分类所有文件"""
    items = []
    
    for dp, dns, fns in os.walk(ROOT):
        # 跳过排除的目录
        rel = os.path.relpath(dp, ROOT)
        top = rel.split(os.sep)[0] if rel != '.' else ''
        if top in EXCLUDE_TOP:
            dns[:] = []
            continue
        
        for f in fns:
            if f.lower() in SYSFILES:
                continue
            if not any(f.lower().endswith(ext) for ext in MEDIA_EXT):
                continue
            
            full = os.path.join(dp, f)
            cat = classify(f)
            tgt = get_target_path(full, cat)
            items.append((full, cat, tgt))
    
    return items


def count_files(directory):
    """统计目录中的文件数量"""
    count = 0
    for dp, _, fns in os.walk(directory):
        count += len([f for f in fns if f.lower() not in SYSFILES])
    return count


def main():
    execute = "--execute" in sys.argv
    dry_run = not execute
    
    print("=== 开始扫描 ===")
    items = scan()
    
    # 统计分类
    by_cat = Counter(c for _, c, _ in items)
    print("\n=== 分类统计 ===")
    for k, v in by_cat.most_common():
        print(f"  {k}: {v}")
    print(f"  合计: {len(items)}")
    
    # 检测冲突
    tgt_counter = Counter(t for _, _, t in items)
    conflicts = {k: v for k, v in tgt_counter.items() if v > 1}
    print(f"\n=== 目标路径冲突: {len(conflicts)} 处 ===")
    for k, v in list(conflicts.items())[:10]:
        print(f"  x{v} {k}")
    
    # 保存清单
    with open(MANIFEST_PATH, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['源路径', '类别', '目标路径'])
        writer.writerows(items)
    print(f"\n=== 清单已保存到: {MANIFEST_PATH} ===")
    
    if dry_run:
        print("\n[DRY-RUN] 未执行复制操作")
        return
    
    # 执行复制
    print("\n=== 开始复制 ===")
    done = err = 0
    for i, (src, cat, tgt) in enumerate(items, 1):
        try:
            os.makedirs(os.path.dirname(tgt), exist_ok=True)
            
            # 检查目标是否已存在且完整
            if os.path.exists(tgt):
                src_size = os.path.getsize(src)
                tgt_size = os.path.getsize(tgt)
                if src_size == tgt_size:
                    done += 1
                    continue
                # 大小不同，添加后缀
                base, ext = os.path.splitext(tgt)
                tgt = f"{base}__dup{i}{ext}"
            
            shutil.copy2(src, tgt)
            done += 1
        except Exception as e:
            err += 1
            if err <= 20:
                print(f"  ERR [{cat}] {os.path.relpath(src, ROOT)}: {e}", flush=True)
        
        if i % 500 == 0:
            print(f"  进度 {i}/{len(items)}  成功{done} 失败{err}", flush=True)
    
    print(f"\n=== 完成: 成功 {done}, 失败 {err}, 总计 {len(items)} ===")


if __name__ == "__main__":
    main()
