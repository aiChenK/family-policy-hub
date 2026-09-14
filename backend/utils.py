# -*- coding: utf-8 -*-
"""
工具函数与控制台终端展示辅助
"""

import socket
from . import config

FAVICON_SVG = b'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path d="M50 5 L85 20 L85 55 C85 75 50 95 50 95 C50 95 15 75 15 55 L15 20 Z" fill="#0284c7"/>
  <path d="M40 50 L48 58 L65 38" stroke="#ffffff" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''


def get_lan_ip() -> str:
    """获取本机局域网 IP 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def print_banner(server_engine: str, local_url: str, lan_url: str) -> None:
    """打印漂亮的控制台启动横幅"""
    print("=" * 64)
    print("  🏠 家庭保险资产管理系统 - 服务已启动")
    print("=" * 64)
    print(f"  > 运行引擎:      {server_engine}")
    print(f"  > 密码鉴权:      {'🔒 已启用访问密码' if config.ACCESS_PASSWORD else '🔓 未设置密码 (免密访问)'}")
    print(f"  > 本机访问地址:  {local_url}")
    print(f"  > 局域网访问:    {lan_url}")
    print(f"  > 数据持久目录:  {config.DATA_DIR}")
    print(f"  > 容灾备份目录:  {config.BACKUP_DIR}")
    print("=" * 64)
    print("  提示: 按 Ctrl+C 可停止服务\n")
