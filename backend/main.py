# -*- coding: utf-8 -*-
"""
家庭保险资产管理系统 - 统一启动入口与服务调度
支持 FastAPI + Uvicorn 异步模式与 Python 标准库多线程平滑降级双模运行
"""

import os
import sys
import webbrowser
from http.server import ThreadingHTTPServer

# 确保项目根目录在 sys.path 中，支持 python3 backend/main.py 直接调用
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend import config, utils
from backend.app_standard import StandardHandler

# 探测运行环境是否具备现代化异步框架
HAS_FASTAPI = False
try:
    import fastapi
    import uvicorn
    from backend.app_fastapi import create_fastapi_app
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


def run_server():
    """主服务启动函数"""
    lan_ip = utils.get_lan_ip()
    port = config.PORT
    host = config.HOST
    local_url = f"http://localhost:{port}"
    lan_url = f"http://{lan_ip}:{port}"

    if HAS_FASTAPI:
        engine_name = "FastAPI + Uvicorn (高性能异步生产级)"
        utils.print_banner(engine_name, local_url, lan_url)
        app = create_fastapi_app()
        try:
            uvicorn.run(app, host=host, port=port, log_level="info")
        except KeyboardInterrupt:
            print("\n服务已安全退出。")
    else:
        engine_name = "Python 标准库 ThreadingHTTPServer (零依赖多线程)"
        utils.print_banner(engine_name, local_url, lan_url)
        server_address = (host, port)
        try:
            httpd = ThreadingHTTPServer(server_address, StandardHandler)
        except OSError:
            alt_port = port + 1
            print(f"端口 {port} 被占用，切换至端口 {alt_port}...")
            httpd = ThreadingHTTPServer((host, alt_port), StandardHandler)
            local_url = f"http://localhost:{alt_port}"
            lan_url = f"http://{lan_ip}:{alt_port}"

        try:
            if not os.environ.get('NO_BROWSER'):
                webbrowser.open(local_url)
        except Exception:
            pass

        try:
            import signal
            signal.signal(signal.SIGHUP, signal.SIG_IGN)
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务已安全退出。")
            httpd.server_close()
        except Exception as e:
            print(f"\n服务异常退出: {e}")
            httpd.server_close()


if __name__ == '__main__':
    run_server()
