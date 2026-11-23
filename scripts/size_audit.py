#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐字节比对源文件和目标文件"""
import csv
import os
from collections import defaultdict

WORKSPACE = "/Users/mima0000/.dsh/bot/workspace"
MANIFEST = f"{WORKSPACE}/classification_manifest.csv"

def gsz(p):
    try: return os.path.getsize(p)
    except OSError: return None

gsize = {}
def get_size(p):
    if p not in gsize:
        gsize[p] = gsz(p)
    return gsize[p]

tally = defaultdict(lambda: defaultdict(int))
problems = []

with open(MANIFEST, encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        if len(row) < 3: continue
        src, cat, tgt = row[0], row[1], row[2]
        
        t = get_size(tgt)
        s = get_size(src)
        
        if t is None: st = "ABSENT"
        elif s is None: st = "SRC_GONE"
        elif t == 0: st = "ZERO"
        elif t < s: st = "TRUNCATED"
        elif t > s: st = "BIGGER"
        else: st = "OK"
        
        tally[cat][st] += 1
        if st != "OK":
            problems.append((cat, st, src, tgt, t, s))

order = ["亚马逊原图汇总", "亚马逊已经出单线稿图及说明书", "未知"]
allst = ["OK", "ABSENT", "ZERO", "TRUNCATED", "BIGGER", "SRC_GONE"]

print("\n===== SIZE AUDIT TALLY (per category) =====")
hdr = "cat\t" + "\t".join(allst) + "\ttotal"
print(hdr)
for c in order:
    row = tally[c]
    tot = sum(row.values())
    print(f"{c}\t" + "\t".join(str(row.get(k,0)) for k in allst) + f"\t{tot}")
for c in tally:
    if c not in order:
        tot = sum(tally[c].values())
        print(f"{c}\t" + "\t".join(str(tally[c].get(k,0)) for k in allst) + f"\t{tot}")

bad_total = sum(len([1 for p in problems if p[1] != 'OK']) for _ in [0])
print(f"\nTOTAL rows: {sum(sum(row.values()) for row in tally.values())}")
print(f"OK (byte-complete & present): {sum(tally[c]['OK'] for c in tally)}")
print(f"BAD (ABSENT+ZERO+TRUNCATED+BIGGER+SRC_GONE): {len(problems)}")
print(f"problem list saved to: {WORKSPACE}/.problems.txt ({len(problems)} lines)")

with open(f"{WORKSPACE}/.problems.txt","w") as f:
    f.write("category\tstatus\tsrc\ttarget\ttarget_size\tsrc_size\n")
    for c,st,src,tgt,t,s in problems:
        f.write(f"{c}\t{st}\t{src}\t\t{t}\t{s}\n")

print("DONE")
