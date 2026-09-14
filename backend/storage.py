# -*- coding: utf-8 -*-
"""
数据存储层统一门面模块 (Facade)：
将 JSON 结构化数据存储 (storage_json) 与物理附件安全管理 (storage_attachments) 统一暴露，
确保所有历史调用方、路由模块与脚本 100% 平滑兼容无破坏。
"""

from .storage_json import (
    atomic_save_json,
    load_policies_data,
    load_history_data,
    DEFAULT_INSURANCE_PHONES,
    load_insurance_phones_data,
    save_insurance_phones_data,
    load_vehicles_data,
    load_companies_data,
    save_companies_data,
    load_payment_records_data,
    save_payment_records_data,
    update_payment_confirmation,
    get_aggregated_data,
    save_aggregated_data
)

from .storage_attachments import (
    format_file_size,
    save_attachment_file,
    save_attachment_bytes,
    get_attachment_path,
    delete_attachment_file,
    get_all_referenced_attachments,
    scan_orphan_attachments,
    clean_orphan_attachments
)

__all__ = [
    # JSON 结构化持久化
    "atomic_save_json",
    "load_policies_data",
    "load_history_data",
    "DEFAULT_INSURANCE_PHONES",
    "load_insurance_phones_data",
    "save_insurance_phones_data",
    "load_vehicles_data",
    "load_companies_data",
    "save_companies_data",
    "load_payment_records_data",
    "save_payment_records_data",
    "update_payment_confirmation",
    "get_aggregated_data",
    "save_aggregated_data",
    # 物理附件与孤儿清理
    "format_file_size",
    "save_attachment_file",
    "save_attachment_bytes",
    "get_attachment_path",
    "delete_attachment_file",
    "get_all_referenced_attachments",
    "scan_orphan_attachments",
    "clean_orphan_attachments"
]
