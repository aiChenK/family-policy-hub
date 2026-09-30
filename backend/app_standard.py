# -*- coding: utf-8 -*-
"""
Python 标准库平滑降级引擎
零第三方依赖的高可用多线程 HTTP 处理器
"""

import os
import json
import datetime
from urllib.parse import urlparse
from http.server import SimpleHTTPRequestHandler
import re
from urllib.parse import unquote
from . import config, auth, storage, utils, ai_service


def parse_multipart_payload(content_type: str, raw_bytes: bytes) -> tuple:
    """健壮解析 multipart/form-data 字节流，原生支持 UTF-8 中文文件名与单/多文件，彻底杜绝 Header 类型错误"""
    m = re.search(r'boundary=([^;]+)', content_type, re.IGNORECASE)
    if not m:
        return {}, []
    boundary = m.group(1).strip('"\'').encode('latin-1')
    delimiter = b'--' + boundary

    parts = raw_bytes.split(delimiter)
    fields = {}
    files = []

    for part in parts:
        part = part.strip(b'\r\n')
        if not part or part == b'--':
            continue
        if b'\r\n\r\n' in part:
            header_bytes, payload = part.split(b'\r\n\r\n', 1)
        elif b'\n\n' in part:
            header_bytes, payload = part.split(b'\n\n', 1)
        else:
            continue

        header_text = header_bytes.decode('utf-8', errors='replace')
        cd_match = re.search(r'Content-Disposition:\s*form-data;\s*([^;\r\n]+(?:;[^\r\n]+)*)', header_text, re.IGNORECASE)
        if not cd_match:
            continue

        params_str = cd_match.group(1)
        name_m = re.search(r'name=["\']?([^"\';\r\n]+)["\']?', params_str)
        fname_m = re.search(r'filename\*?=(?:UTF-8\'\')?["\']?([^"\';\r\n]+)["\']?', params_str, re.IGNORECASE)

        name = name_m.group(1) if name_m else ''
        if fname_m:
            filename = unquote(fname_m.group(1))
            files.append((filename, payload))
        elif name:
            fields[name] = payload.decode('utf-8', errors='replace').strip()

    return fields, files


class StandardHandler(SimpleHTTPRequestHandler):
    """基于标准库的请求处理器，全面实现与 FastAPI 兼容的路由与鉴权"""

    def __init__(self, *args, **kwargs):
        doc_dir = config.DIST_DIR if os.path.exists(config.DIST_DIR) else (
            config.FRONTEND_DIR if os.path.exists(config.FRONTEND_DIR) else config.BACKEND_DIR
        )
        super().__init__(*args, directory=doc_dir, **kwargs)

    def send_json(self, status_code: int, data: dict) -> None:
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()
        self.wfile.write(body)

    def check_authorized(self, query: str = '') -> bool:
        if not config.ACCESS_PASSWORD:
            return True
        auth_header = self.headers.get('Authorization', '')
        token = auth.extract_bearer_token(auth_header)
        if not token and query:
            from urllib.parse import parse_qs
            qs = parse_qs(query)
            token = qs.get('token', [''])[0]
        return auth.verify_token(token)


    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.end_headers()

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.strip()
        query = parsed.query.strip()
        if path.startswith('/api/attachments/'):
            if not self.check_authorized(query):
                self.send_response(401)
                self.end_headers()
                return
            import mimetypes
            from urllib.parse import unquote, quote
            parts = path.split('/')
            if len(parts) >= 5:
                cat = parts[3]
                fname = unquote('/'.join(parts[4:]))
                fpath = storage.get_attachment_path(cat, fname)
                if fpath and os.path.exists(fpath):
                    mime_type, _ = mimetypes.guess_type(fpath)
                    mime_type = mime_type or 'application/octet-stream'
                    fsize = os.path.getsize(fpath)
                    self.send_response(200)
                    self.send_header('Content-Type', mime_type)
                    self.send_header('Content-Length', str(fsize))
                    encoded_name = quote(os.path.basename(fpath))
                    self.send_header('Content-Disposition', f"inline; filename*=UTF-8''{encoded_name}")
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    return
            self.send_response(404)
            self.end_headers()
            return
        return super().do_HEAD()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.strip()
        query = parsed.query.strip()

        if path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml')
            self.send_header('Content-Length', str(len(utils.FAVICON_SVG)))
            self.end_headers()
            self.wfile.write(utils.FAVICON_SVG)
            return

        if path.startswith('/.well-known/'):
            self.send_json(404, {"error": "not found"})
            return

        # 严格禁止外部直接静态读取数据目录、隐藏配置与敏感后端源码
        if path.startswith(('/.', '/backend', '/data')) or path in ('/.env', '/config.py', '/storage.py', '/main.py'):
            self.send_json(403, {"error": "禁止直接访问敏感文件与数据存储目录"})
            return

        if path == '/api/auth/status':
            auth_header = self.headers.get('Authorization', '')
            token = auth.extract_bearer_token(auth_header)
            is_authed = auth.verify_token(token)
            self.send_json(200, {
                "auth_required": bool(config.ACCESS_PASSWORD),
                "authenticated": is_authed
            })
            return

        # 保护 API 路由
        if path.startswith('/api/'):
            if not self.check_authorized(query):
                self.send_json(401, {"error": "未授权访问或登录已过期"})
                return


            if path == '/api/policies':
                self.send_json(200, storage.load_policies_data())
                return
            elif path == '/api/history':
                self.send_json(200, storage.load_history_data())
                return
            elif path == '/api/vehicles':
                self.send_json(200, storage.load_vehicles_data())
                return
            elif path == '/api/companies':
                self.send_json(200, storage.load_companies_data())
                return
            elif path == '/api/payment-records':
                self.send_json(200, storage.load_payment_records_data())
                return
            elif path == '/api/insurance-phones':
                self.send_json(200, storage.load_insurance_phones_data())
                return
            elif path == '/api/settings/ai':
                self.send_json(200, storage.get_safe_ai_settings())
                return
            elif path == '/api/data':
                self.send_json(200, storage.get_aggregated_data())
                return
            elif path == '/api/attachments/orphans':
                self.send_json(200, storage.scan_orphan_attachments())
                return
            elif path.startswith('/api/attachments/'):
                # 提取 /api/attachments/{category}/{filename}
                import mimetypes
                from urllib.parse import unquote, quote
                parts = path.split('/')
                if len(parts) >= 5:
                    cat = parts[3]
                    fname = unquote('/'.join(parts[4:]))
                    fpath = storage.get_attachment_path(cat, fname)
                    if fpath and os.path.exists(fpath):
                        mime_type, _ = mimetypes.guess_type(fpath)
                        mime_type = mime_type or 'application/octet-stream'
                        with open(fpath, 'rb') as f:
                            content = f.read()
                        self.send_response(200)
                        self.send_header('Content-Type', mime_type)
                        self.send_header('Content-Length', str(len(content)))
                        encoded_name = quote(os.path.basename(fpath))
                        self.send_header('Content-Disposition', f"inline; filename*=UTF-8''{encoded_name}")
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(content)
                        return
                self.send_json(404, {"error": "附件不存在"})
                return
            else:
                self.send_json(404, {"error": "API route not found"})
                return

        # 静态网页托管 (SPA 模式回退)
        if path == '/' or path == '':
            self.path = '/index.html'
        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.strip()

        # 读取原始请求体字节
        length = int(self.headers.get('Content-Length', 0))
        raw_bytes = self.rfile.read(length) if length > 0 else b""
        payload = {}
        content_type = self.headers.get('Content-Type', '')
        if 'application/json' in content_type or not content_type:
            try:
                body = raw_bytes.decode('utf-8') if raw_bytes else "{}"
                payload = json.loads(body) if body else {}
            except Exception:
                payload = {}

        if path == '/api/auth/login':
            pwd = str(payload.get('password', ''))
            if not config.ACCESS_PASSWORD or pwd == config.ACCESS_PASSWORD:
                self.send_json(200, {"status": "ok", "token": auth.generate_token()})
            else:
                self.send_json(401, {"error": "访问密码错误，请重新输入"})
            return

        # 保护写 API
        if path.startswith('/api/'):
            if not self.check_authorized():
                self.send_json(401, {"error": "未授权访问或凭证无效"})
                return

            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if path == '/api/policies':
                payload["updatedAt"] = now_str
                storage.atomic_save_json(config.POLICIES_FILE, payload)
                self.send_json(200, {"status": "ok", "message": "保单已原子保存"})
                return
            elif path == '/api/vehicles':
                payload["updatedAt"] = now_str
                storage.atomic_save_json(config.VEHICLES_FILE, payload)
                self.send_json(200, {"status": "ok", "message": "车辆信息已保存"})
                return
            elif path == '/api/companies':
                payload["updatedAt"] = now_str
                storage.atomic_save_json(config.COMPANIES_FILE, payload)
                self.send_json(200, {"status": "ok", "message": "企业资质数据已保存"})
                return
            elif path == '/api/payment-records':
                storage.save_payment_records_data(payload)
                self.send_json(200, {"status": "ok", "message": "缴费确认记录已保存"})
                return
            elif path == '/api/payment-records/confirm':
                record_key = str(payload.get('recordKey', ''))
                if not record_key:
                    self.send_json(400, {"error": "缺少 recordKey"})
                    return
                updated = storage.update_payment_confirmation(record_key, payload)
                self.send_json(200, {"status": "ok", "record": updated})
                return
            elif path == '/api/insurance-phones':
                storage.save_insurance_phones_data(payload)
                self.send_json(200, {"status": "ok", "message": "保险电话配置已保存"})
                return
            elif path == '/api/data':
                storage.save_aggregated_data(payload)
                self.send_json(200, {"status": "ok", "message": "数据已成功保存至本地"})
                return
            elif path == '/api/attachments/upload':
                content_type = self.headers.get('Content-Type', '')
                if 'multipart/form-data' in content_type:
                    try:
                        form_fields, files = parse_multipart_payload(content_type, raw_bytes)
                        cat = str(form_fields.get("category", "personal"))
                        subfolder = str(form_fields.get("subfolder", ""))
                        if not files:
                            self.send_json(400, {"error": "缺少上传文件"})
                            return
                        filename, file_bytes = files[0]
                        if not filename or not file_bytes:
                            self.send_json(400, {"error": "缺少上传文件或文件名"})
                            return
                        att = storage.save_attachment_bytes(cat, filename, file_bytes, subfolder=subfolder)
                        self.send_json(200, {"status": "ok", "attachment": att})
                        return
                    except Exception as e:
                        self.send_json(500, {"error": f"保存附件失败: {e}"})
                        return
                else:
                    cat = str(payload.get("category", "personal"))
                    fname = str(payload.get("filename", ""))
                    c_b64 = str(payload.get("contentBase64", ""))
                    subfolder = str(payload.get("subfolder", ""))
                    if not fname or not c_b64:
                        self.send_json(400, {"error": "缺少文件名或文件内容"})
                        return
                    try:
                        att = storage.save_attachment_file(cat, fname, c_b64, subfolder=subfolder)
                        self.send_json(200, {"status": "ok", "attachment": att})
                    except Exception as e:
                        self.send_json(500, {"error": f"保存附件失败: {e}"})
                    return
            elif path == '/api/attachments/delete':
                cat = str(payload.get("category", "personal"))
                fname = str(payload.get("filename", ""))
                if not fname:
                    self.send_json(400, {"error": "缺少文件名"})
                    return
                ok = storage.delete_attachment_file(cat, fname)
                self.send_json(200, {"status": "ok" if ok else "not_found"})
                return
            elif path == '/api/attachments/orphans/clean':
                self.send_json(200, storage.clean_orphan_attachments())
                return
            elif path == '/api/settings/ai':
                res = storage.save_ai_settings(payload)
                self.send_json(200, res)
                return
            elif path == '/api/settings/ai/test':
                current = storage.load_ai_settings()
                req_key = str(payload.get("apiKey", "")).strip()
                if not req_key or "****" in req_key:
                    payload["apiKey"] = current.get("apiKey", "")
                res = ai_service.test_ai_connection(payload)
                self.send_json(200, res)
                return
            elif path == '/api/vehicles/parse-policy':
                ai_cfg = storage.load_ai_settings()
                if not ai_cfg.get("enabled", False) or not ai_cfg.get("apiKey", "").strip():
                    self.send_json(400, {
                        "error": "not_configured",
                        "message": "AI 识单引擎尚未配置或已关闭，请先在【管理与工具 -> AI 识单引擎配置】中设置 API Key 与模型"
                    })
                    return

                content_type = self.headers.get('Content-Type', '')
                file_items = []
                plate_hint = ""

                if 'multipart/form-data' in content_type:
                    try:
                        form_fields, files = parse_multipart_payload(content_type, raw_bytes)
                        plate_hint = form_fields.get('plateNo', '').strip()
                        file_items = files
                    except Exception as e:
                        self.send_json(500, {"error": f"解析上传文件失败: {e}"})
                        return
                else:
                    plate_hint = str(payload.get("plateNo", "")).strip()
                    raw_files = payload.get("files", [])
                    if not raw_files and payload.get("contentBase64"):
                        raw_files = [{
                            "filename": payload.get("filename", "policy.pdf"),
                            "contentBase64": payload.get("contentBase64")
                        }]
                    import base64
                    for rf in raw_files:
                        b64 = str(rf.get("contentBase64", ""))
                        if ',' in b64:
                            b64 = b64.split(',', 1)[1]
                        if b64:
                            file_items.append((rf.get("filename", "policy.pdf"), base64.b64decode(b64)))

                if not file_items:
                    self.send_json(400, {"error": "未接收到需要解析的保单文件"})
                    return

                try:
                    policy_data = ai_service.parse_policy_files(file_items, ai_cfg)
                except Exception as e:
                    self.send_json(500, {"error": f"AI 保单解析异常: {e}"})
                    return

                final_plate = plate_hint or policy_data.get("plateNo") or "vehicles"
                final_year = policy_data.get("year") or datetime.datetime.now().year
                subfolder = f"{final_plate}/{final_year}"
                saved_attachments = []
                for fname, fbytes in file_items:
                    try:
                        att = storage.save_attachment_bytes('vehicle', fname, fbytes, subfolder=subfolder)
                        saved_attachments.append(att)
                    except Exception as e:
                        print(f"[WARN] 自动归档解析附件失败 {fname}: {e}")

                self.send_json(200, {
                    "status": "ok",
                    "policyData": policy_data,
                    "attachments": saved_attachments
                })
                return
            else:
                self.send_json(404, {"error": "API not found"})
                return


        self.send_json(404, {"error": "Not found"})

    def log_message(self, format, *args):
        try:
            msg = format % args
            if '/api/' in msg:
                print(f"[{self.log_date_time_string()}] {msg}")
        except Exception:
            pass
