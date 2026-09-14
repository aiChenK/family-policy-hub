# -*- coding: utf-8 -*-
"""
数据存储层 - JSON 结构化数据持久化：
原子写入、多版本轮转自动备份、保单/缴费/爱车/企业数据存取与向下兼容
"""

import os
import json
import shutil
import glob
import datetime
from . import config


def _is_business_identical(old_obj, new_obj) -> bool:
    """对比两份数据是否在业务内容上完全一致（忽略 updatedAt 时间戳差异）"""
    if isinstance(old_obj, dict) and isinstance(new_obj, dict):
        keys = set(old_obj.keys()) | set(new_obj.keys())
        for k in keys:
            if k == "updatedAt":
                continue
            if k not in old_obj or k not in new_obj:
                return False
            if not _is_business_identical(old_obj[k], new_obj[k]):
                return False
        return True
    return old_obj == new_obj


def atomic_save_json(filepath: str, data: dict, max_backups: int = 10) -> None:
    """先写临时文件再原子重命名 (os.replace)，带自动轮转备份，彻底防止意外断电或并发崩溃损坏"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # 1. 检查文件是否已存在：若业务内容无任何变动，直接跳过落盘与冗余备份
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            if _is_business_identical(current_data, data):
                return
        except Exception:
            pass  # 若旧文件损坏或无法解析，继续走下方安全覆写逻辑

    # 2. 写入临时文件并落盘
    tmp_file = f"{filepath}.tmp"
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())

    # 3. 备份旧文件（仅在发生实质变动时生成有效快照）
    if os.path.exists(filepath):
        base_name = os.path.basename(filepath)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(config.BACKUP_DIR, f"{base_name}.{timestamp}.bak")
        try:
            shutil.copy2(filepath, backup_file)
            pattern = os.path.join(config.BACKUP_DIR, f"{base_name}.*.bak")
            existing = sorted(glob.glob(pattern), key=os.path.getmtime)
            while len(existing) > max_backups:
                os.remove(existing.pop(0))
        except Exception as e:
            print(f"[WARN] 备份失败: {e}")

    # 4. 原子重命名覆盖
    os.replace(tmp_file, filepath)


def load_policies_data() -> dict:
    """加载保单与被保人列表"""
    if os.path.exists(config.POLICIES_FILE):
        try:
            with open(config.POLICIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] 读取 policies.json 失败: {e}")
    # 尝试从 legacy 文件还原
    if os.path.exists(config.LEGACY_FILE):
        try:
            with open(config.LEGACY_FILE, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                return {
                    "updatedAt": raw.get("updatedAt", ""),
                    "members": raw.get("members", []),
                    "memberSummary": raw.get("memberSummary", {}),
                    "familyMembers": raw.get("familyMembers", []),
                    "policies": raw.get("policies", [])
                }
        except Exception:
            pass
    return {"updatedAt": "", "members": [], "memberSummary": {}, "familyMembers": [], "policies": []}


def load_history_data() -> dict:
    """加载历史已缴保费明细"""
    if os.path.exists(config.HISTORY_FILE):
        try:
            with open(config.HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] 读取 history_payments.json 失败: {e}")
    if os.path.exists(config.LEGACY_FILE):
        try:
            with open(config.LEGACY_FILE, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                return {
                    "updatedAt": raw.get("updatedAt", ""),
                    "count": len(raw.get("historicalPayments", [])),
                    "payments": raw.get("historicalPayments", [])
                }
        except Exception:
            pass
    return {"updatedAt": "", "count": 0, "payments": []}


DEFAULT_INSURANCE_PHONES = {
    "defaultPhone": "",
    "phones": [
        {"id": "phone_1", "name": "中国平安", "keyword": "平安", "phone": "95511", "notes": "全国统一客服与理赔报案（产险/寿险/健康险）"},
        {"id": "phone_2", "name": "中国人保", "keyword": "人保", "phone": "95518", "notes": "PICC 中国人保全国客服热线"},
        {"id": "phone_3", "name": "中国人寿", "keyword": "人寿", "phone": "95519", "notes": "中国人寿全国统一客户服务专线"},
        {"id": "phone_4", "name": "中国太保", "keyword": "太保", "phone": "95500", "notes": "太平洋人寿/财险全国统一热线"},
        {"id": "phone_5", "name": "华夏保险", "keyword": "华夏", "phone": "95300", "notes": "华夏人寿全国客户服务热线"},
        {"id": "phone_6", "name": "众安保险", "keyword": "众安", "phone": "1010-9955", "notes": "众安互联网财险全国客服专线"},
        {"id": "phone_7", "name": "大都会人寿", "keyword": "大都会", "phone": "400-818-8168", "notes": "中美联泰大都会人寿全国热线"},
        {"id": "phone_8", "name": "绍兴市民保/人社", "keyword": "绍兴政府", "phone": "12333", "notes": "绍兴市民保 / 全国人社政务服务便民热线"},
        {"id": "phone_9", "name": "中华联合保险", "keyword": "中华", "phone": "95585", "notes": "中华财险/人寿全国客户服务电话"},
        {"id": "phone_10", "name": "中国大地保险", "keyword": "大地", "phone": "95590", "notes": "大地财险客户服务及报案专线"},
        {"id": "phone_11", "name": "阳光保险", "keyword": "阳光", "phone": "95510", "notes": "阳光财险/人寿客户服务电话"},
        {"id": "phone_12", "name": "中国太平", "keyword": "太平", "phone": "95589", "notes": "太平人寿/财险全国客户服务热线"}
    ]
}


def load_insurance_phones_data() -> dict:
    """加载保险机构服务与报案电话配置，不存在时自动初始化落盘"""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if os.path.exists(config.INSURANCE_PHONES_FILE):
        try:
            with open(config.INSURANCE_PHONES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and "phones" in data:
                    return data
        except Exception as e:
            print(f"[ERROR] 读取 insurance_phones.json 失败: {e}")

    # 首次启动或文件不存在时，写入默认预设配置
    initial_data = {
        "updatedAt": now_str,
        "defaultPhone": DEFAULT_INSURANCE_PHONES["defaultPhone"],
        "phones": list(DEFAULT_INSURANCE_PHONES["phones"])
    }
    try:
        atomic_save_json(config.INSURANCE_PHONES_FILE, initial_data)
    except Exception as e:
        print(f"[WARN] 初始化写入 insurance_phones.json 异常: {e}")
    return initial_data


def save_insurance_phones_data(data: dict) -> None:
    """保存保险机构电话配置"""
    if not isinstance(data, dict):
        data = {"defaultPhone": "", "phones": []}
    data["updatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    atomic_save_json(config.INSURANCE_PHONES_FILE, data)


def load_vehicles_data() -> dict:
    """加载车辆与车险记录"""
    if os.path.exists(config.VEHICLES_FILE):
        try:
            with open(config.VEHICLES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] 读取 vehicles.json 失败: {e}")
    return {"updatedAt": "", "vehicles": []}


def load_companies_data() -> dict:
    """加载关联企业与营业执照备查记录"""
    if os.path.exists(config.COMPANIES_FILE):
        try:
            with open(config.COMPANIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] 读取 companies.json 失败: {e}")
    return {"updatedAt": "", "companies": []}


def save_companies_data(data: dict) -> None:
    """保存关联企业与营业执照备查记录"""
    if not isinstance(data, dict):
        data = {"companies": []}
    data["updatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    atomic_save_json(config.COMPANIES_FILE, data)


def load_payment_records_data() -> dict:
    """加载保费缴费确认与归档记录"""
    if os.path.exists(config.PAYMENT_RECORDS_FILE):
        try:
            with open(config.PAYMENT_RECORDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] 读取 payment_records.json 失败: {e}")
    return {"updatedAt": "", "confirmations": {}, "archiveRecords": []}


def save_payment_records_data(data: dict) -> None:
    """保存保费缴费确认记录"""
    data["updatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    atomic_save_json(config.PAYMENT_RECORDS_FILE, data)


def update_payment_confirmation(record_key: str, info: dict) -> dict:
    """更新单笔保费手动确认状态"""
    data = load_payment_records_data()
    confirmations = data.setdefault("confirmations", {})
    if record_key not in confirmations:
        confirmations[record_key] = {}
    conf_data = info.get("confirmation", info) if isinstance(info.get("confirmation"), dict) else info
    for k, v in conf_data.items():
        if k not in ("recordKey", "confirmation"):
            confirmations[record_key][k] = v
    confirmations[record_key]["updatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_payment_records_data(data)
    return confirmations[record_key]


def get_aggregated_data() -> dict:
    """向下兼容合并旧版单一 JSON 结构"""
    p_data = load_policies_data()
    h_data = load_history_data()
    v_data = load_vehicles_data()
    comp_data = load_companies_data()
    pay_data = load_payment_records_data()
    phone_data = load_insurance_phones_data()
    return {
        "updatedAt": p_data.get("updatedAt", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "members": p_data.get("members", []),
        "memberSummary": p_data.get("memberSummary", {}),
        "familyMembers": p_data.get("familyMembers", []),
        "policies": p_data.get("policies", []),
        "historicalPayments": h_data.get("payments", []),
        "paymentRecords": pay_data,
        "vehicles": v_data.get("vehicles", []),
        "companies": comp_data.get("companies", []),
        "insurancePhones": phone_data
    }


def save_aggregated_data(data: dict) -> None:
    """拆分保存：将前端提交的聚合全量数据分别安全写入对应分表文件"""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. 拆分保存 policies.json
    policies_payload = {
        "updatedAt": now_str,
        "members": data.get("members", []),
        "memberSummary": data.get("memberSummary", {}),
        "familyMembers": data.get("familyMembers", []),
        "policies": data.get("policies", [])
    }
    atomic_save_json(config.POLICIES_FILE, policies_payload)

    # 2. 若包含 paymentRecords，保存 payment_records.json
    if "paymentRecords" in data and isinstance(data["paymentRecords"], dict):
        save_payment_records_data(data["paymentRecords"])

    # 3. 若包含 historicalPayments，独立保存 history_payments.json
    if "historicalPayments" in data and isinstance(data["historicalPayments"], list):
        history_payload = {
            "updatedAt": now_str,
            "count": len(data["historicalPayments"]),
            "payments": data["historicalPayments"]
        }
        atomic_save_json(config.HISTORY_FILE, history_payload)

    # 4. 若包含 vehicles，独立保存 vehicles.json
    if "vehicles" in data and isinstance(data["vehicles"], list):
        vehicles_payload = {
            "updatedAt": now_str,
            "vehicles": data["vehicles"]
        }
        atomic_save_json(config.VEHICLES_FILE, vehicles_payload)

    # 5. 若包含 companies，独立保存 companies.json
    if "companies" in data and isinstance(data["companies"], list):
        companies_payload = {
            "updatedAt": now_str,
            "companies": data["companies"]
        }
        atomic_save_json(config.COMPANIES_FILE, companies_payload)

    # 6. 若包含 insurancePhones，独立保存 insurance_phones.json
    if "insurancePhones" in data and isinstance(data["insurancePhones"], dict):
        save_insurance_phones_data(data["insurancePhones"])

    # 同步写入一份 legacy 文件用于冷备
    try:
        atomic_save_json(config.LEGACY_FILE, data, max_backups=5)
    except Exception:
        pass
