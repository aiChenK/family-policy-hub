# -*- coding: utf-8 -*-
"""
家庭保险管理系统 - 后端服务包
"""

from .config import PORT, HOST, DATA_DIR, BACKUP_DIR

def run_server():
    """按需加载并运行服务调度器"""
    from .main import run_server as _run_server
    return _run_server()

__all__ = ["PORT", "HOST", "DATA_DIR", "BACKUP_DIR", "run_server"]
