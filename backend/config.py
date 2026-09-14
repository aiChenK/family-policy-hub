# -*- coding: utf-8 -*-
"""
配置管理与环境初始化
"""

import os

# ==================== 1. 基础路径配置 ====================
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))

FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
DIST_DIR = os.path.join(FRONTEND_DIR, 'dist')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
ATTACHMENT_DIR = os.path.join(DATA_DIR, 'attachments')

POLICIES_FILE = os.path.join(DATA_DIR, 'policies.json')
HISTORY_FILE = os.path.join(DATA_DIR, 'history_payments.json')
PAYMENT_RECORDS_FILE = os.path.join(DATA_DIR, 'payment_records.json')
VEHICLES_FILE = os.path.join(DATA_DIR, 'vehicles.json')
COMPANIES_FILE = os.path.join(DATA_DIR, 'companies.json')
INSURANCE_PHONES_FILE = os.path.join(DATA_DIR, 'insurance_phones.json')
LEGACY_FILE = os.path.join(DATA_DIR, 'insurance_data.json')


# ==================== 2. 环境配置加载 (.env) ====================
def load_dotenv(path: str) -> None:
    """简易解析 .env 文件，不依赖第三方库"""
    if not os.path.exists(path):
        return
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip()
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception as e:
        print(f"[WARN] 读取 .env 异常: {e}")

# 优先读取项目根目录的 .env
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))


# ==================== 3. 核心服务常量 ====================
ACCESS_PASSWORD = os.environ.get('ACCESS_PASSWORD', '').strip()
PORT = int(os.environ.get('PORT', '8088'))
HOST = os.environ.get('HOST', '0.0.0.0')
SECRET_SALT = os.environ.get('SECRET_SALT', 'family_insurance_vault_salt_2026')


# ==================== 4. 初始化目录结构 ====================
def ensure_directories():
    """确保运行时所需数据与备份目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(os.path.join(ATTACHMENT_DIR, 'personal'), exist_ok=True)
    os.makedirs(os.path.join(ATTACHMENT_DIR, 'vehicle'), exist_ok=True)

ensure_directories()
