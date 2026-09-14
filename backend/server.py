# -*- coding: utf-8 -*-
"""
后端服务启动入口别名 (指向 backend.main)
支持直接执行: python3 backend/server.py
"""

import os
import sys

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.main import run_server

if __name__ == '__main__':
    run_server()
