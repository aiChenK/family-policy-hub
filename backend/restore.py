# -*- coding: utf-8 -*-
"""
家庭保险资产管理系统 - 数据备份快照查看与安全恢复工具
用法:
  python3 backend/restore.py list [module]      # 列出可用备份快照 (module 可选: policies, vehicles, etc.)
  python3 backend/restore.py restore <filename>  # 恢复指定快照 (恢复前会自动对当前状态创建安全快照)
"""

import os
import sys
import glob
import json
import shutil
import datetime

# 确保能正常加载 config
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend import config


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def list_backups(module_filter: str = "") -> list:
    """列出所有或指定模块的备份快照"""
    pattern = os.path.join(config.BACKUP_DIR, "*.bak")
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    
    backups = []
    for f in files:
        bname = os.path.basename(f)
        target_name = bname.split('.json.')[0] + '.json' if '.json.' in bname else ''
        if module_filter and module_filter.lower() not in bname.lower():
            continue
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M:%S')
        backups.append({
            "filename": bname,
            "filepath": f,
            "target": target_name,
            "size": format_size(os.path.getsize(f)),
            "mtime": mtime
        })
    return backups


def show_list(module_filter: str = "") -> None:
    backups = list_backups(module_filter)
    if not backups:
        print("\n📭 暂无符合条件的备份快照文件。")
        return

    print("\n" + "=" * 80)
    print(f"{'序号':<4} {'目标数据文件':<24} {'快照生成时间':<20} {'大小':<10} {'快照文件名'}")
    print("-" * 80)
    for idx, b in enumerate(backups, 1):
        print(f"[{idx:<2}] {b['target']:<24} {b['mtime']:<20} {b['size']:<10} {b['filename']}")
    print("=" * 80)
    print(f"提示: 使用 python3 backend/restore.py restore <快照文件名> 即可安全恢复。\n")


def restore_backup(backup_identifier: str) -> None:
    """按文件名恢复指定备份"""
    backups = list_backups()
    matched = None

    # 支持序号匹配或完整文件名匹配
    if backup_identifier.isdigit():
        idx = int(backup_identifier)
        if 1 <= idx <= len(backups):
            matched = backups[idx - 1]
    else:
        for b in backups:
            if b["filename"] == backup_identifier or b["filename"].startswith(backup_identifier):
                matched = b
                break

    if not matched:
        print(f"\n❌ 未找到匹配的快照文件: {backup_identifier}")
        print("可运行 python3 backend/restore.py list 查看所有可用快照。")
        return

    src_file = matched["filepath"]
    target_name = matched["target"]
    target_path = os.path.join(config.DATA_DIR, target_name)

    # 1. 校验备份文件是否为合法 JSON
    try:
        with open(src_file, 'r', encoding='utf-8') as f:
            json.load(f)
    except Exception as e:
        print(f"\n❌ 快照文件损坏，无法读取解析为有效 JSON: {e}")
        return

    # 2. 覆盖前对当前目标文件做一次安全保底备份 (pre_restore)
    if os.path.exists(target_path):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safety_backup = os.path.join(config.BACKUP_DIR, f"{target_name}.pre_restore_{ts}.bak")
        shutil.copy2(target_path, safety_backup)
        print(f"🛡️  已对当前最新状态创建安全回退快照: {os.path.basename(safety_backup)}")

    # 3. 原子覆盖恢复
    tmp_path = f"{target_path}.tmp"
    shutil.copy2(src_file, tmp_path)
    os.replace(tmp_path, target_path)

    print(f"\n✅ 成功恢复数据快照！")
    print(f"   源快照: {matched['filename']}")
    print(f"   已还原至: {target_path}")
    print(f"   生效时间: {matched['mtime']}\n")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help', 'help'):
        print(__doc__)
        return

    action = args[0].lower()
    if action == 'list':
        module = args[1] if len(args) > 1 else ""
        show_list(module)
    elif action == 'restore':
        if len(args) < 2:
            print("❌ 请指定要恢复的备份快照文件名或序号！例如: python3 backend/restore.py restore 1")
            return
        restore_backup(args[1])
    else:
        print(f"❌ 未知命令: {action}。支持的命令: list, restore")


if __name__ == '__main__':
    main()
