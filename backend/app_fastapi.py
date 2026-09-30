# -*- coding: utf-8 -*-
"""
FastAPI 现代化异步 Web 应用构建器
"""

import os
import datetime
from . import config, auth, storage, utils, ai_service

def create_fastapi_app():
    """构建高性能 FastAPI 应用实例"""
    from fastapi import FastAPI, Request, Response, HTTPException, status, Depends
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GZipMiddleware

    app = FastAPI(title="家庭保险管理系统 API", version="2.0.0")

    app.add_middleware(GZipMiddleware, minimum_size=1000)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def check_auth(request: Request):
        if not config.ACCESS_PASSWORD:
            return True
        auth_header = request.headers.get("Authorization", "")
        token = auth.extract_bearer_token(auth_header)
        if not auth.verify_token(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未授权或访问凭据已过期")
        return True

    @app.get("/api/auth/status")
    async def auth_status(request: Request):
        auth_header = request.headers.get("Authorization", "")
        token = auth.extract_bearer_token(auth_header)
        is_authed = auth.verify_token(token)
        return {
            "auth_required": bool(config.ACCESS_PASSWORD),
            "authenticated": is_authed
        }

    @app.post("/api/auth/login")
    async def auth_login(payload: dict):
        pwd = str(payload.get("password", ""))
        if not config.ACCESS_PASSWORD or pwd == config.ACCESS_PASSWORD:
            return {"status": "ok", "token": auth.generate_token()}
        return JSONResponse(status_code=401, content={"error": "访问密码错误，请重新输入"})

    @app.get("/api/policies")
    async def get_policies(_: bool = Depends(check_auth)):
        return storage.load_policies_data()

    @app.post("/api/policies")
    async def save_policies(payload: dict, _: bool = Depends(check_auth)):
        payload["updatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        storage.atomic_save_json(config.POLICIES_FILE, payload)
        return {"status": "ok", "message": "保单数据已原子保存"}

    @app.get("/api/history")
    async def get_history(_: bool = Depends(check_auth)):
        return storage.load_history_data()

    @app.get("/api/vehicles")
    async def get_vehicles(_: bool = Depends(check_auth)):
        return storage.load_vehicles_data()

    @app.post("/api/vehicles")
    async def save_vehicles(payload: dict, _: bool = Depends(check_auth)):
        payload["updatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        storage.atomic_save_json(config.VEHICLES_FILE, payload)
        return {"status": "ok", "message": "车辆与车险数据已保存"}

    @app.get("/api/payment-records")
    async def get_payment_records(_: bool = Depends(check_auth)):
        return storage.load_payment_records_data()

    @app.post("/api/payment-records")
    async def post_payment_records(payload: dict, _: bool = Depends(check_auth)):
        storage.save_payment_records_data(payload)
        return {"status": "ok", "message": "缴费确认记录已保存"}

    @app.post("/api/payment-records/confirm")
    async def post_confirm_payment(payload: dict, _: bool = Depends(check_auth)):
        record_key = str(payload.get("recordKey", ""))
        if not record_key:
            raise HTTPException(status_code=400, detail="缺少 recordKey")
        updated = storage.update_payment_confirmation(record_key, payload)
        return {"status": "ok", "record": updated}

    @app.get("/api/insurance-phones")
    async def get_insurance_phones(_: bool = Depends(check_auth)):
        return storage.load_insurance_phones_data()

    @app.post("/api/insurance-phones")
    async def post_insurance_phones(payload: dict, _: bool = Depends(check_auth)):
        storage.save_insurance_phones_data(payload)
        return {"status": "ok", "message": "保险电话配置已更新保存"}

    @app.get("/api/companies")
    async def get_companies(_: bool = Depends(check_auth)):
        return storage.load_companies_data()

    @app.post("/api/companies")
    async def save_companies(payload: dict, _: bool = Depends(check_auth)):
        payload["updatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        storage.atomic_save_json(config.COMPANIES_FILE, payload)
        return {"status": "ok", "message": "企业资质数据已保存"}

    # 向下兼容旧版 /api/data 聚合接口
    @app.get("/api/data")
    async def get_legacy_data(_: bool = Depends(check_auth)):
        return storage.get_aggregated_data()

    @app.post("/api/data")
    async def post_legacy_data(payload: dict, _: bool = Depends(check_auth)):
        storage.save_aggregated_data(payload)
        return {"status": "ok", "message": "全量数据已成功拆分持久化至本地"}

    # ==================== 附件存取 API ====================
    @app.post("/api/attachments/upload")
    async def upload_attachment(request: Request, _: bool = Depends(check_auth)):
        content_type = request.headers.get("content-type", "")
        if "multipart/form-data" in content_type:
            form = await request.form()
            file_obj = form.get("file")
            category = str(form.get("category", "personal"))
            subfolder = str(form.get("subfolder", ""))
            if not file_obj or not hasattr(file_obj, "read"):
                raise HTTPException(status_code=400, detail="缺少上传文件内容")
            try:
                file_bytes = await file_obj.read()
                filename = getattr(file_obj, "filename", "unnamed_file")
                att = storage.save_attachment_bytes(category, filename, file_bytes, subfolder=subfolder)
                return {"status": "ok", "attachment": att}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"保存附件异常: {e}")
        else:
            try:
                payload = await request.json()
            except Exception:
                payload = {}
            category = str(payload.get("category", "personal"))
            filename = str(payload.get("filename", ""))
            content_base64 = str(payload.get("contentBase64", ""))
            subfolder = str(payload.get("subfolder", ""))
            if not filename or not content_base64:
                raise HTTPException(status_code=400, detail="缺少文件名或文件内容")
            try:
                att = storage.save_attachment_file(category, filename, content_base64, subfolder=subfolder)
                return {"status": "ok", "attachment": att}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"保存附件异常: {e}")

    @app.get("/api/attachments/{category}/{filename:path}")
    async def get_attachment(category: str, filename: str, request: Request, token: str = ""):
        if config.ACCESS_PASSWORD:
            auth_header = request.headers.get("Authorization", "")
            tok = auth.extract_bearer_token(auth_header) or token
            if not auth.verify_token(tok):
                raise HTTPException(status_code=401, detail="未授权访问或登录凭证无效")
        import mimetypes
        from urllib.parse import unquote
        file_path = storage.get_attachment_path(category, unquote(filename))
        if not file_path:
            raise HTTPException(status_code=404, detail="附件不存在或已被移除")
        mime_type, _ = mimetypes.guess_type(file_path)
        return FileResponse(
            file_path,
            media_type=mime_type or "application/octet-stream",
            content_disposition_type="inline"
        )


    @app.get("/api/attachments/orphans")
    async def get_orphan_attachments(_: bool = Depends(check_auth)):
        return storage.scan_orphan_attachments()

    @app.post("/api/attachments/orphans/clean")
    async def clean_orphan_attachments(_: bool = Depends(check_auth)):
        return storage.clean_orphan_attachments()

    @app.post("/api/attachments/delete")
    async def delete_attachment(payload: dict, _: bool = Depends(check_auth)):
        category = str(payload.get("category", "personal"))
        filename = str(payload.get("filename", ""))
        if not filename:
            raise HTTPException(status_code=400, detail="缺少文件名")
        success = storage.delete_attachment_file(category, filename)
        return {"status": "ok" if success else "not_found"}

    # ==================== AI 识单引擎配置与解析 API ====================
    @app.get("/api/settings/ai")
    async def get_ai_settings(_: bool = Depends(check_auth)):
        return storage.get_safe_ai_settings()

    @app.post("/api/settings/ai")
    async def update_ai_settings(payload: dict, _: bool = Depends(check_auth)):
        return storage.save_ai_settings(payload)

    @app.post("/api/settings/ai/test")
    async def test_ai_settings_endpoint(payload: dict, _: bool = Depends(check_auth)):
        # 若 payload 中 apiKey 带有掩码或为空，使用现有已存密钥
        current = storage.load_ai_settings()
        req_key = str(payload.get("apiKey", "")).strip()
        if not req_key or "****" in req_key:
            payload["apiKey"] = current.get("apiKey", "")
        res = ai_service.test_ai_connection(payload)
        return res

    @app.post("/api/vehicles/parse-policy")
    async def parse_vehicle_policy(request: Request, _: bool = Depends(check_auth)):
        # 1. 检查 AI 识单引擎是否已配置并启用
        ai_cfg = storage.load_ai_settings()
        if not ai_cfg.get("enabled", False) or not ai_cfg.get("apiKey", "").strip():
            raise HTTPException(
                status_code=400,
                detail="AI 识单引擎尚未配置或已关闭，请先在【管理与工具 -> AI 识单引擎配置】中设置 API Key 与模型"
            )

        content_type = request.headers.get("content-type", "")
        file_items = []  # [(filename, bytes)]
        plate_hint = ""

        if "multipart/form-data" in content_type:
            form = await request.form()
            plate_hint = str(form.get("plateNo", "")).strip()
            # 读取所有上传的文件 (可能为一个 file 或多个 files)
            for key, val in form.multi_items():
                if hasattr(val, "read") and hasattr(val, "filename"):
                    b = await val.read()
                    if b and len(b) > 0:
                        file_items.append((val.filename, b))
        else:
            try:
                payload = await request.json()
            except Exception:
                payload = {}
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
            raise HTTPException(status_code=400, detail="未接收到需要解析的保单文件")

        # 2. 调用 AI 解析
        try:
            policy_data = ai_service.parse_policy_files(file_items, ai_cfg)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI 保单解析异常: {e}")

        # 3. 自动将上传文件保存至车辆附件目录
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

        return {
            "status": "ok",
            "policyData": policy_data,
            "attachments": saved_attachments
        }


    @app.get("/favicon.ico")
    async def favicon():
        return Response(content=utils.FAVICON_SVG, media_type="image/svg+xml")

    # 静态资源与前端工程全托管 (优先挂载打包产物 dist)
    target_dir = config.DIST_DIR if os.path.exists(config.DIST_DIR) else config.FRONTEND_DIR
    if os.path.exists(target_dir):
        from fastapi.staticfiles import StaticFiles
        app.mount("/", StaticFiles(directory=target_dir, html=True), name="frontend")
    else:
        @app.get("/")
        async def index():
            index_file = os.path.join(config.PROJECT_ROOT, 'index.html')
            if os.path.exists(index_file):
                return FileResponse(index_file, media_type="text/html; charset=utf-8")
            return HTMLResponse("<h3>index.html not found</h3>", status_code=404)

    return app
