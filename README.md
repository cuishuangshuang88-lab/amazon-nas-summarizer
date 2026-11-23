# Amazon NAS Image Summarizer

DSH Skill for automatic image classification and organization from Amazon business NAS.

## Overview

This skill automates the process of scanning, classifying, and organizing image files from the Amazon business NAS shared folder. It categorizes files into:
- **原图** (Original images): Product renders, gallery materials
- **说明书** (Manuals): PDF documents and instruction images  
- **线稿图** (Line art): Technical drawings, design sketches
- **未知** (Unknown): UUID-named or unrecognizable files

## Repository Structure

```
amazon-nas-summarizer/
├── SKILL.md              # DSH skill definition
├── README.md            # This file
├── scripts/
│   ├── nas_sort.py      # Main classifier and copier
│   ├── nas_verify.py    # Verification tool
│   └── size_audit.py    # Byte-level integrity audit
├── docs/
│   └── usage.md         # Usage documentation
└── examples/            # Sample configurations
```

## Quick Start

```bash
# Clone repository
git clone https://github.com/cuishuangshuang88-lab/amazon-nas-summarizer.git
cd amazon-nas-summarizer

# Run dry-run to preview classification
python3 scripts/nas_sort.py

# Execute actual copy operation
python3 scripts/nas_sort.py --execute

# Verify results
python3 scripts/nas_verify.py
python3 scripts/size_audit.py
```

## Configuration

Edit `scripts/nas_sort.py` to configure paths:

```python
ROOT = "/Volumes/Amazon事业部"           # NAS root directory
TESTDIR = os.path.join(ROOT, "崔双双测试勿删")  # Target subdirectory
```

## Output Structure

```
崔双双测试勿删/
├── 亚马逊原图汇总/          # Original images storage
├── 亚马逊已经出单线稿图及说明书/  # Manuals + line art
└── 未知/                   # Unclassified files
```

## Production Results (2026-11-23)

| Category | Count | Size |
|----------|-------|------|
| 原图 | 3,233 | ~13 GB |
| 说明书 | 2,083 | - |
| 线稿图 | 1,432 | - |
| 未知 | 752 | ~294 MB |
| **Total** | **7,500** | **~21 GB** |

## Features

- **Intelligent Classification**: Regex-based detection for file types
- **Deduplication Handling**: Auto-renames conflicts with `__dup{N}` suffix
- **Manifest Generation**: CSV export with source→destination mapping
- **Byte-level Validation**: SHA256 hashing for integrity verification
- **SMB Error Recovery**: Handles large file transfer timeouts gracefully

## Requirements

- Python 3.8+
- macOS with SMB mount
- No third-party dependencies

## License

MIT License - Free to use and modify.

## Author

Created by Chief (DSH Bot) with assistance from codex助手
For cuishuangshuang88-lab
