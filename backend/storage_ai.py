# -*- coding: utf-8 -*-
"""
数据存储层 - AI 识单引擎配置与密钥持久化管理：
支持 BaseURL、API Key、模型名称安全存取、脱敏回传与原子写入
"""

import os
import json
import datetime
from . import config
from .storage_json import atomic_save_json

DEFAULT_AI_SETTINGS = {
    "enabled": False,
    "baseUrl": "",
    "apiKey": "",
    "model": "",
    "timeout": 60,
    "updatedAt": ""
}


def mask_api_key(key: str) -> str:
    """对 API Key 进行脱敏保护处理"""
    if not key:
        return ""
    key = str(key).strip()
    if len(key) <= 8:
        return "****"
    return f"{key[:3]}****{key[-4:]}"


def load_ai_settings() -> dict:
    """加载底层真实的完整 AI 配置（含真实 API Key）"""
    settings = dict(DEFAULT_AI_SETTINGS)
    
    # 优先从数据文件读取
    if os.path.exists(config.AI_SETTINGS_FILE):
        try:
            with open(config.AI_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    settings.update(data)
                    return settings
        except Exception as e:
            print(f"[WARN] 读取 ai_settings.json 异常: {e}")

    # 若数据文件尚未创建，尝试回退读取环境变量预设
    env_key = os.environ.get('AI_API_KEY', '').strip()
    env_base = os.environ.get('AI_BASE_URL', '').strip()
    env_model = os.environ.get('AI_MODEL', '').strip()
    if env_key:
        settings["apiKey"] = env_key
        settings["enabled"] = True
    if env_base:
        settings["baseUrl"] = env_base
    if env_model:
        settings["model"] = env_model

    return settings


def get_safe_ai_settings() -> dict:
    """获取脱敏的 AI 配置供前端展示与状态查询"""
    real = load_ai_settings()
    has_key = bool(real.get("apiKey", "").strip())
    masked_key = mask_api_key(real.get("apiKey", ""))
    
    is_configured = bool(
        real.get("enabled", False) and
        has_key and
        real.get("baseUrl", "").strip() and
        real.get("model", "").strip()
    )

    return {
        "enabled": bool(real.get("enabled", False)),
        "baseUrl": real.get("baseUrl", ""),
        "apiKey": masked_key,
        "apiKeyMasked": masked_key,
        "hasApiKey": has_key,
        "isConfigured": is_configured,
        "model": real.get("model", ""),
        "timeout": int(real.get("timeout", 60)),
        "updatedAt": real.get("updatedAt", "")
    }


def save_ai_settings(payload: dict) -> dict:
    """安全持久化保存 AI 配置，智能判断并保留未修改的 API Key"""
    current = load_ai_settings()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_key = str(payload.get("apiKey", "")).strip()
    # 判断是否为脱敏字符串（若用户未修改 key，前端传回来的通常包含 ****）
    if "****" in new_key:
        # 保留原有的 key
        final_key = current.get("apiKey", "").strip()
    else:
        final_key = new_key

    updated = {
        "enabled": bool(payload.get("enabled", False)),
        "baseUrl": str(payload.get("baseUrl", "")).strip(),
        "apiKey": final_key,
        "model": str(payload.get("model", "")).strip(),
        "timeout": int(payload.get("timeout", 60)),
        "updatedAt": now_str
    }

    # 原子写入文件
    atomic_save_json(config.AI_SETTINGS_FILE, updated)
    return get_safe_ai_settings()
