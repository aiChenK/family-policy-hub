# -*- coding: utf-8 -*-
"""
FastAPI 现代化异步 Web 应用构建器
"""

import os
import datetime
from . import config, auth, storage, utils

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
