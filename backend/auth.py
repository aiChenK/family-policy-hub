# -*- coding: utf-8 -*-
"""
安全认证与 Token 鉴权模块
基于 HMAC-SHA256 签名与 Base64 编码实现轻量无状态鉴权
"""

import time
import hmac
import hashlib
import base64
from . import config

def get_server_key() -> str:
    """根据密码与混淆盐派生服务端签名密钥"""
    return hashlib.sha256((config.ACCESS_PASSWORD + config.SECRET_SALT).encode('utf-8')).hexdigest()

def generate_token() -> str:
    """生成包含时间戳与 HMAC 签名的认证 Token"""
    ts = int(time.time())
    raw = str(ts)
    sig = hmac.new(get_server_key().encode('utf-8'), raw.encode('utf-8'), hashlib.sha256).hexdigest()
    token_str = f"{raw}.{sig}"
    return base64.urlsafe_b64encode(token_str.encode('utf-8')).decode('utf-8')

def verify_token(token_str: str) -> bool:
    """
    校验 Token 有效性：
    - 若未配置访问密码，直接放行 (True)
    - 校验时间戳有效性（30天有效期，允许 300秒 时钟偏移）
    - 校验 HMAC 签名防篡改
    """
    if not config.ACCESS_PASSWORD:
        return True
    if not token_str:
        return False
    try:
        decoded = base64.urlsafe_b64decode(token_str.encode('utf-8')).decode('utf-8')
        if '.' not in decoded:
            return False
        ts_str, sig = decoded.split('.', 1)
        ts = int(ts_str)
        now = time.time()
        # 30 天有效期 (2592000秒)，且允许微小时钟偏差 (300秒)
        if now - ts > 2592000 or ts > now + 300:
            return False
        expected_sig = hmac.new(get_server_key().encode('utf-8'), ts_str.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected_sig)
    except Exception:
        return False

def extract_bearer_token(auth_header: str) -> str:
    """从 Authorization 标头中提取 Bearer Token"""
    if not auth_header:
        return ""
    parts = auth_header.strip().split()
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return parts[1]
    return ""
