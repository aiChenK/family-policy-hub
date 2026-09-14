# -*- coding: utf-8 -*-
"""
数据存储层 - 物理附件与文件系统管理：
多级分类目录安全保存、防路径穿越校验、macOS/Linux Unicode 规范化匹配、孤儿附件扫描与物理释放
"""

import os
import re
import time
import base64
import datetime
import unicodedata
from urllib.parse import unquote

from . import config
from .storage_json import load_policies_data, load_vehicles_data, load_companies_data


def format_file_size(size_bytes: int) -> str:
    """人性化格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def save_attachment_bytes(category: str, filename: str, file_bytes: bytes, subfolder: str = "") -> dict:
    """安全保存二进制字节流附件至指定分类目录（支持子文件夹）并返回元数据"""
    category = category if category in ('vehicle', 'company', 'personal') else 'personal'
    base_dir = os.path.join(config.ATTACHMENT_DIR, category)

    # 规范化并分段清洗子文件夹名（支持如 "浙A13K52/2026" 多级安全目录，严格杜绝路径穿越）
    subfolder_str = unquote(str(subfolder or '')).replace('\\', '/').strip('/')
    safe_parts = []
    for part in subfolder_str.split('/'):
        part = part.strip()
        if not part or part in ('.', '..'):
            continue
        safe_part = re.sub(r'[^\w\u4e00-\u9fa5\.-]', '_', part).strip('._')
        safe_part = re.sub(r'\.{2,}', '_', safe_part)
        if safe_part:
            safe_parts.append(safe_part)

    safe_subfolder = '/'.join(safe_parts)
    if safe_parts:
        target_dir = os.path.abspath(os.path.join(base_dir, *safe_parts))
        # 防路径穿越安全校验：必须在 base_dir 之内
        if not (target_dir == base_dir or target_dir.startswith(base_dir + os.sep)):
            target_dir = base_dir
            safe_subfolder = ""
    else:
        target_dir = base_dir

    os.makedirs(target_dir, exist_ok=True)

    original_name = os.path.basename(filename)
    safe_name_root = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fa5\.-]', '_', original_name)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    stored_filename = f"{timestamp}_{safe_name_root}"

    file_path = os.path.join(target_dir, stored_filename)
    with open(file_path, 'wb') as f:
        f.write(file_bytes)

    # 统一使用正斜杠构建相对存储名与访问 URL
    if safe_subfolder:
        stored_name = f"{safe_subfolder}/{stored_filename}"
    else:
        stored_name = stored_filename

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "id": f"att_{int(time.time() * 1000)}",
        "name": original_name,
        "category": category,
        "storedName": stored_name,
        "url": f"/api/attachments/{category}/{stored_name}",
        "size": len(file_bytes),
        "uploadedAt": now_str
    }


def save_attachment_file(category: str, filename: str, content_base64: str, subfolder: str = "") -> dict:
    """安全保存上传的 base64 附件至指定分类目录（向下兼容历史调用）"""
    if ',' in content_base64:
        content_base64 = content_base64.split(',', 1)[1]
    file_bytes = base64.b64decode(content_base64)
    return save_attachment_bytes(category, filename, file_bytes, subfolder=subfolder)


def get_attachment_path(category: str, filename: str) -> str:
    """获取指定附件的安全物理绝对路径，支持子目录、防路径穿越并兼容中文编码与旧格式"""
    category = category if category in ('vehicle', 'company', 'personal') else 'personal'
    base_dir = os.path.abspath(os.path.join(config.ATTACHMENT_DIR, category))
    if not os.path.exists(base_dir):
        return ""

    decoded_name = unquote(str(filename or '')).replace('\\', '/').strip('/')
    if not decoded_name:
        return ""

    # 1. 直接通过规范化相对路径尝试命中
    full_path = os.path.abspath(os.path.join(base_dir, decoded_name))
    # 防路径穿越：必须在 base_dir 目录下
    if not (full_path == base_dir or full_path.startswith(base_dir + os.sep)):
        return ""

    if os.path.exists(full_path) and os.path.isfile(full_path):
        return full_path

    # 2. 兼容 macOS/Linux Unicode 规范化差异 (NFC / NFD)
    base_name = os.path.basename(decoded_name)
    parent_dir = os.path.dirname(full_path)
    norm_base = unicodedata.normalize('NFC', base_name)

    if os.path.exists(parent_dir) and os.path.isdir(parent_dir):
        try:
            for real_name in os.listdir(parent_dir):
                if unicodedata.normalize('NFC', real_name) == norm_base:
                    cand = os.path.join(parent_dir, real_name)
                    if os.path.isfile(cand):
                        return cand
        except Exception:
            pass

    # 3. 全局回退查找：兼容旧版未分目录引用或历史路径变动
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if unicodedata.normalize('NFC', f) == norm_base:
                cand = os.path.join(root, f)
                if os.path.isfile(cand):
                    return cand

    return ""


def delete_attachment_file(category: str, filename: str) -> bool:
    """安全删除附件物理文件，并自动清理空子目录"""
    file_path = get_attachment_path(category, filename)
    if file_path and os.path.exists(file_path):
        try:
            parent_dir = os.path.dirname(file_path)
            os.remove(file_path)
            # 递归向上清理已空的子目录（直至分类根目录）
            category = category if category in ('vehicle', 'company', 'personal') else 'personal'
            base_dir = os.path.abspath(os.path.join(config.ATTACHMENT_DIR, category))
            curr_dir = parent_dir
            while curr_dir and os.path.abspath(curr_dir) != base_dir and os.path.abspath(curr_dir).startswith(base_dir + os.sep):
                try:
                    if not os.listdir(curr_dir):
                        os.rmdir(curr_dir)
                        curr_dir = os.path.dirname(curr_dir)
                    else:
                        break
                except Exception:
                    break
            return True
        except Exception as e:
            print(f"[WARN] 删除附件失败: {e}")
    return False


def get_all_referenced_attachments() -> dict:
    """收集当前所有保单与车辆中正在引用的有效附件物理文件名集合（支持子目录相对路径与文件名）"""
    referenced = {
        "personal": set(),
        "vehicle": set(),
        "company": set()
    }

    def collect_from_att_list(att_list, default_cat):
        if not isinstance(att_list, list):
            return
        for att in att_list:
            if not isinstance(att, dict):
                continue
            cat = att.get("category", default_cat)
            cat = cat if cat in ("vehicle", "company", "personal") else "personal"
            stored_name = att.get("storedName", "")
            if not stored_name and att.get("url"):
                # 从 url 中截取 /api/attachments/{category}/ 之后的部分
                url_str = att.get("url", "")
                prefix = f"/api/attachments/{cat}/"
                if prefix in url_str:
                    stored_name = url_str.split(prefix, 1)[1].split('?')[0]
                else:
                    stored_name = os.path.basename(url_str)
            if stored_name:
                decoded_name = unquote(stored_name).replace('\\', '/').strip('/')
                base_name = os.path.basename(decoded_name)
                for name_variant in (stored_name, decoded_name, base_name):
                    referenced[cat].add(name_variant)
                    referenced[cat].add(unicodedata.normalize('NFC', name_variant))
                    referenced[cat].add(unicodedata.normalize('NFD', name_variant))

    # 1. 扫描人身保单
    policies_data = load_policies_data()
    for p in policies_data.get("policies", []):
        if isinstance(p, dict):
            collect_from_att_list(p.get("attachments", []), "personal")

    # 2. 扫描车辆与车险记录
    vehicles_data = load_vehicles_data()
    for v in vehicles_data.get("vehicles", []):
        if isinstance(v, dict):
            collect_from_att_list(v.get("attachments", []), "vehicle")
            for rec in v.get("insuranceRecords", []):
                if isinstance(rec, dict):
                    collect_from_att_list(rec.get("attachments", []), "vehicle")

    # 3. 扫描关联企业营业执照附件
    companies_data = load_companies_data()
    for comp in companies_data.get("companies", []):
        if isinstance(comp, dict):
            collect_from_att_list(comp.get("attachments", []), "company")

    # 4. 扫描聚合旧版兼容数据（防止误删仅存在于旧版格式中的引用）
    if os.path.exists(config.LEGACY_FILE):
        try:
            import json
            with open(config.LEGACY_FILE, 'r', encoding='utf-8') as f:
                legacy = json.load(f)
                for p in legacy.get("policies", []):
                    if isinstance(p, dict):
                        collect_from_att_list(p.get("attachments", []), "personal")
                for v in legacy.get("vehicles", []):
                    if isinstance(v, dict):
                        collect_from_att_list(v.get("attachments", []), "vehicle")
                        for rec in v.get("insuranceRecords", []):
                            if isinstance(rec, dict):
                                collect_from_att_list(rec.get("attachments", []), "vehicle")
                for c in legacy.get("companies", []):
                    if isinstance(c, dict):
                        collect_from_att_list(c.get("attachments", []), "company")
        except Exception:
            pass

    return referenced


def scan_orphan_attachments() -> dict:
    """全面递归扫描磁盘附件目录，比对引用关系并返回孤儿附件统计与清单"""
    referenced = get_all_referenced_attachments()
    categories = ['personal', 'vehicle', 'company']

    total_files = 0
    total_size = 0
    orphans = []
    orphan_size = 0

    for cat in categories:
        cat_dir = os.path.join(config.ATTACHMENT_DIR, cat)
        if not os.path.exists(cat_dir) or not os.path.isdir(cat_dir):
            continue

        for root, dirs, files in os.walk(cat_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for fname in files:
                if fname.startswith('.'):
                    continue
                full_path = os.path.join(root, fname)
                if not os.path.isfile(full_path):
                    continue

                try:
                    fsize = os.path.getsize(full_path)
                    mtime = os.path.getmtime(full_path)
                    mod_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    fsize = 0
                    mod_str = ""

                total_files += 1
                total_size += fsize

                # 计算相对于 cat_dir 的相对路径
                rel_path = os.path.relpath(full_path, cat_dir).replace('\\', '/')

                # 比对是否在引用集合中（比对相对路径与纯文件名，防 Unicode 差异）
                norm_rel = unicodedata.normalize('NFC', rel_path)
                norm_base = unicodedata.normalize('NFC', fname)
                cat_set = referenced.get(cat, set())

                is_referenced = (
                    rel_path in cat_set or
                    norm_rel in cat_set or
                    fname in cat_set or
                    norm_base in cat_set
                )

                if not is_referenced:
                    orphans.append({
                        "category": cat,
                        "storedName": rel_path,
                        "size": fsize,
                        "sizeFormatted": format_file_size(fsize),
                        "modifiedAt": mod_str
                    })
                    orphan_size += fsize

    # 按修改时间倒序排列
    orphans.sort(key=lambda x: x.get("modifiedAt", ""), reverse=True)

    return {
        "status": "ok",
        "totalFiles": total_files,
        "totalSize": total_size,
        "totalSizeFormatted": format_file_size(total_size),
        "referencedFiles": total_files - len(orphans),
        "orphanCount": len(orphans),
        "orphanSize": orphan_size,
        "orphanSizeFormatted": format_file_size(orphan_size),
        "orphans": orphans
    }


def clean_orphan_attachments() -> dict:
    """批量物理清理所有无引用的孤儿附件，安全释放磁盘空间"""
    scan_res = scan_orphan_attachments()
    orphans = scan_res.get("orphans", [])

    cleaned_count = 0
    freed_size = 0
    failed_files = []

    for item in orphans:
        cat = item.get("category", "personal")
        fname = item.get("storedName", "")
        fsize = item.get("size", 0)
        if delete_attachment_file(cat, fname):
            cleaned_count += 1
            freed_size += fsize
        else:
            failed_files.append(fname)

    return {
        "status": "ok",
        "cleanedCount": cleaned_count,
        "freedSize": freed_size,
        "freedSizeFormatted": format_file_size(freed_size),
        "failedCount": len(failed_files),
        "failedFiles": failed_files
    }
