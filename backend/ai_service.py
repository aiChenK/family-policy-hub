# -*- coding: utf-8 -*-
"""
AI 识单引擎核心服务：
负责与 OpenAI 兼容大模型 API 交互、PDF 文本与多模态视觉提取、车险单据智能理解与字段归一化
"""

import os
import re
import io
import json
import time
import base64
import datetime
import urllib.request
import urllib.error

# 尝试导入 PyMuPDF (fitz) 以实现高性能 PDF 文本提取与扫描件渲染
try:
    import fitz
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

# 尝试导入纯 Python 跨平台 PDF 库 pypdf (零编译依赖，适配 Alpine/ARM64 等各种轻量容器)
try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

# 尝试导入 requests 库
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def _send_http_post(url: str, headers: dict, data: dict, timeout: int = 60) -> tuple:
    """底层通用 HTTP POST 请求封装（优先 requests，降级 urllib）"""
    json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
    if HAS_REQUESTS:
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=timeout)
            return resp.status_code, resp.text
        except requests.exceptions.Timeout:
            raise RuntimeError(f"请求 AI 服务超时（超过 {timeout} 秒）")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"网络请求失败: {e}")
    else:
        req = urllib.request.Request(url, data=json_bytes, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status_code = response.getcode()
                body = response.read().decode('utf-8')
                return status_code, body
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            return e.code, err_body
        except urllib.error.URLError as e:
            raise RuntimeError(f"网络连接异常: {e.reason}")
        except Exception as e:
            raise RuntimeError(f"请求失败: {e}")


def test_ai_connection(settings: dict) -> dict:
    """测试指定 AI 配置的连通性与模型可用性"""
    base_url = str(settings.get("baseUrl", "")).strip().rstrip('/')
    api_key = str(settings.get("apiKey", "")).strip()
    model = str(settings.get("model", "")).strip()
    timeout = int(settings.get("timeout", 20))

    if not base_url:
        return {"success": False, "message": "API Base URL 不能为空"}
    if not api_key:
        return {"success": False, "message": "API Key 不能为空"}
    if not model:
        return {"success": False, "message": "模型名称 (Model) 不能为空"}

    endpoint = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "请回复数字 1"}
        ],
        "max_tokens": 10
    }

    start_time = time.time()
    try:
        status_code, body_text = _send_http_post(endpoint, headers, payload, timeout=timeout)
        duration_ms = int((time.time() - start_time) * 1000)

        if status_code == 200:
            return {
                "success": True,
                "latencyMs": duration_ms,
                "message": f"连接成功！模型 [{model}] 响应正常 (耗时 {duration_ms}ms)"
            }
        else:
            try:
                err_data = json.loads(body_text)
                err_msg = err_data.get("error", {}).get("message", body_text)
            except Exception:
                err_msg = body_text[:300]
            
            hint = ""
            if status_code == 401:
                hint = " (API Key 无效或未授权)"
            elif status_code == 404:
                hint = " (请求地址有误或模型不存在)"
            elif status_code == 429:
                hint = " (超出服务商调用配额或被限流)"

            return {
                "success": False,
                "statusCode": status_code,
                "message": f"连接失败 HTTP {status_code}{hint}: {err_msg}"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"测试连接异常: {str(e)}"
        }


def extract_file_content(filename: str, file_bytes: bytes) -> dict:
    """提取文件内容：文本型 PDF 提取文本，图片或扫描件转为 Base64"""
    ext = os.path.splitext(filename.lower())[1]

    # 1. 处理 PDF 文件
    if ext == '.pdf':
        text_content = ""
        # 优先通过 fitz 读取
        if HAS_FITZ:
            try:
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                # 车险保单的核心数据 99% 在第 1 页，最多跨至第 2 页，第 3 页以后均为法律释义与通用条款
                extracted_pages = []
                max_pages = min(len(doc), 2)
                for p_idx in range(max_pages):
                    raw_text = doc[p_idx].get_text()
                    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
                    cleaned_page = "\n".join(lines)
                    
                    # 智能条款熔断：如果第2页全篇为法律条款且不再包含保费/单号/投保人信息，提前终止
                    if p_idx > 0 and ("保险条款" in cleaned_page or "总则" in cleaned_page) and not ("保费" in cleaned_page or "保险单号" in cleaned_page or "号牌号码" in cleaned_page):
                        break

                    if cleaned_page:
                        extracted_pages.append(f"--- 第 {p_idx+1} 页 ---\n" + cleaned_page)

                    # 若第 1 页已完整包含保单号、起止期间及保费合计，无需继续拉取后续条款页
                    if "保险单号" in cleaned_page and ("保险费合计" in cleaned_page or "保费合计" in cleaned_page or "当年应缴" in cleaned_page):
                        break

                text_content = "\n\n".join(extracted_pages)

                # 若提取到的文本足够多（>80字符），判定为矢量文本电子保单
                if len(text_content.strip()) > 80:
                    return {
                        "type": "text",
                        "content": text_content[:4000],
                        "filename": filename
                    }
                
                # 若提取文本极少，说明是扫描件 PDF，仅渲染第 1 页为高清图片传给多模态
                if len(doc) > 0:
                    pix = doc[0].get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")
                    b64_str = base64.b64encode(img_bytes).decode('utf-8')
                    return {
                        "type": "image",
                        "content": b64_str,
                        "mime": "image/png",
                        "filename": filename
                    }
            except Exception as e:
                print(f"[WARN] fitz 解析 PDF 异常: {e}")

        # 1.2 采用纯 Python pypdf 提取文本与内嵌图像 (零 C 编译依赖，完全兼容 Alpine/ARM64)
        if HAS_PYPDF or True:
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                texts = []
                max_pages = min(len(reader.pages), 2)
                for p_idx in range(max_pages):
                    p = reader.pages[p_idx]
                    t = p.extract_text() or ""
                    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
                    cleaned = "\n".join(lines)
                    if p_idx > 0 and ("保险条款" in cleaned or "总则" in cleaned) and not ("保费" in cleaned or "保险单号" in cleaned):
                        break
                    if cleaned:
                        texts.append(f"--- 第 {p_idx+1} 页 ---\n" + cleaned)
                    if "保险单号" in cleaned and ("保险费合计" in cleaned or "保费合计" in cleaned or "当年应缴" in cleaned):
                        break

                text_content = "\n\n".join(texts)
                if len(text_content.strip()) > 80:
                    return {
                        "type": "text",
                        "content": text_content[:4000],
                        "filename": filename
                    }

                # 若纯文本极少，检查是否为扫描件 PDF，直接提取第 1 页内嵌主图送入视觉大模型
                if len(reader.pages) > 0 and len(reader.pages[0].images) > 0:
                    sorted_imgs = sorted(reader.pages[0].images, key=lambda x: len(x.data), reverse=True)
                    top_img = sorted_imgs[0]
                    b64_str = base64.b64encode(top_img.data).decode('utf-8')
                    ext_lower = os.path.splitext(top_img.name.lower())[1]
                    mime = "image/jpeg" if ext_lower in ('.jpg', '.jpeg') else "image/png"
                    return {
                        "type": "image",
                        "content": b64_str,
                        "mime": mime,
                        "filename": filename
                    }
            except Exception as e:
                print(f"[WARN] pypdf 解析 PDF 异常: {e}")

        # 若提取不到文字且无法解析内嵌图片
        if text_content.strip():
            return {"type": "text", "content": text_content[:4000], "filename": filename}
        raise RuntimeError("无法提取 PDF 内容，若为纯扫描图片 PDF，建议直接上传保单清晰照片或截图")

    # 2. 处理图片文件 (jpg, png, webp 等)
    elif ext in ('.jpg', '.jpeg', '.png', '.webp', '.bmp'):
        mime_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        mime = mime_map.get(ext, 'image/jpeg')
        b64_str = base64.b64encode(file_bytes).decode('utf-8')
        return {
            "type": "image",
            "content": b64_str,
            "mime": mime,
            "filename": filename
        }

    else:
        raise ValueError(f"不支持的文件格式: {ext}，请上传 PDF 或常见图片格式")


POLICY_EXTRACT_PROMPT = """你是一个中国机动车保险核保与电子保单数据结构化录入专家。
请仔细阅读并识别我提供的车险保单单据内容（可能是商业险保单、交强险保单、驾乘人员意外险保单或发票），准确提取出结构化信息。

请按以下 JSON 字段输出（严禁输出任何多余的解释、开场白或 Markdown 标记，直接输出合法 JSON 字符串）：
{
  "company": "承保保险公司简称或全称，如：平安产险 / 人保财险 / 太保产险 / 安盛天平 / 国寿财险 等",
  "plateNo": "号牌号码，如：浙A13K52",
  "vin": "车辆识别代码/车架号 (17位字符)",
  "owner": "车主姓名或单位名称",
  "year": 2026,
  "startDate": "保险生效起期，格式如：YYYY-MM-DD",
  "endDate": "保险到期止期，格式如：YYYY-MM-DD",
  "commercialPolicyNo": "商业险保单号 (若有，纯字符串)",
  "compulsoryPolicyNo": "交强险保单号 (若有，纯字符串)",
  "accidentPolicyNo": "驾乘人员险/意外险保单号 (若有，纯字符串)",
  "commercialPremium": 0.0,
  "compulsoryPremium": 0.0,
  "tax": 0.0,
  "accidentPremium": 0.0,
  "totalPremium": 0.0,
  "hasDamage": true,
  "hasMedicalExcluded": true,
  "thirdPartyAmount": "第三者责任险保额，如：300万 / 200万 / 500万 (没有填空)",
  "driverAmount": "驾乘险或车上人员责任险保额，如：10万/座 / 各50万/座 / 跟车不限人 (没有填空)",
  "extra": "特约条款与增值服务，如：道路救援2次，代驾1次，送检1次",
  "detectedPolicies": ["commercial", "compulsory"]
}

提取特别规则：
1. company：承保公司尽量提取为常见规范简称（如“平安产险”、“人保财险”、“安盛天平”、“太平洋产险”）。
2. year：请根据保险生效日期的年份确定（如 2026-07-17 起保，则归档年度填 2026）。
3. 商业险保费 (commercialPremium)、交强险保费 (compulsoryPremium)、车船税 (tax)、驾乘险 (accidentPremium)：
   - 提取纯浮点数值（不要带“元”或“¥”）；
   - 若保单中未包含该项，填 0；
   - 车船税 (tax) 通常印在交强险保单的“代收车船税”栏；若为新能源汽车且注明免税，填 0；
   - 总保费 (totalPremium) 应为各保费分项加车船税的合计（若保单注明了合计以保单为准）。
4. 保障责任方案：
   - hasDamage：是否有机动车损失保险（车损险），有则为 true，无则为 false；
   - hasMedicalExcluded：是否有附加医保外医疗费用责任险，有则为 true，无则为 false；
   - thirdPartyAmount：提取第三者责任保险的责任限额/保额，格式化如“300万”、“200万”；
   - driverAmount：提取车上人员责任险或驾乘险各座保额，格式化如“10万/座”。
5. extra：提取保单特别约定的增值服务项目（如道路救援次数、代驾次数、安全检测次数等）。
6. 如果某些字段在单据中未提及或无法识别，字符串填空字符串 ""，金额填 0，布尔值填 false，严禁编造任何单号或金额！
"""


def _clean_json_response(raw_text: str) -> dict:
    """从模型输出中稳健提取 JSON 字典"""
    text = raw_text.strip()
    # 移除常见的 ```json ... ``` 包裹
    if "```" in text:
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            text = match.group(1).strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        # 尝试寻找首个 { 和最后一个 }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(text[start:end+1])
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
    raise RuntimeError(f"模型未返回有效 JSON 数据: {raw_text[:200]}")


def parse_policy_files(file_items: list, settings: dict) -> dict:
    """调用大模型对上传的保单文件列表进行识别解析并结构化返回"""
    base_url = str(settings.get("baseUrl", "")).strip().rstrip('/')
    api_key = str(settings.get("apiKey", "")).strip()
    model = str(settings.get("model", "")).strip()
    timeout = int(settings.get("timeout", 60))

    if not api_key:
        raise ValueError("AI 识单引擎未配置 API Key，请先在【管理与工具 -> AI 识单引擎配置】中完成设置")

    endpoint = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 提取所有上传文件的内容
    extracted_items = []
    has_image = False
    for filename, file_bytes in file_items:
        item = extract_file_content(filename, file_bytes)
        extracted_items.append(item)
        if item["type"] == "image":
            has_image = True

    # 组装 messages 内容
    user_content = []
    text_pieces = []
    for item in extracted_items:
        if item["type"] == "text":
            text_pieces.append(f"【文件: {item['filename']}】\n{item['content']}")
        elif item["type"] == "image":
            # 多模态 image_url 节点
            user_content.append({
                "type": "text",
                "text": f"【文件图片: {item['filename']}】"
            })
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{item['mime']};base64,{item['content']}"
                }
            })

    if text_pieces:
        user_content.insert(0, {
            "type": "text",
            "text": "以下是提取出的保单文件文本内容：\n\n" + "\n\n".join(text_pieces)
        })

    # 如果没有任何图片，简化为纯字符串 content 保证兼容性
    if not has_image:
        flat_text = "以下是保单文件内容：\n\n" + "\n\n".join(text_pieces)
        messages = [
            {"role": "system", "content": POLICY_EXTRACT_PROMPT},
            {"role": "user", "content": flat_text}
        ]
    else:
        messages = [
            {"role": "system", "content": POLICY_EXTRACT_PROMPT},
            {"role": "user", "content": user_content}
        ]

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1
    }

    # 发起请求
    status_code, body_text = _send_http_post(endpoint, headers, payload, timeout=timeout)
    if status_code != 200:
        err_msg = body_text
        try:
            err_json = json.loads(body_text)
            err_msg = err_json.get("error", {}).get("message", body_text)
        except Exception:
            pass
        raise RuntimeError(f"AI 服务调用失败 (HTTP {status_code}): {err_msg}")

    # 解析 LLM 返回
    resp_json = json.loads(body_text)
    choices = resp_json.get("choices", [])
    if not choices:
        raise RuntimeError("AI 服务未返回任何分析内容")
    raw_reply = choices[0].get("message", {}).get("content", "")

    parsed_result = _clean_json_response(raw_reply)

    # 规范化与数值兜底纠正
    return _normalize_policy_result(parsed_result)


def _normalize_policy_result(raw: dict) -> dict:
    """对 AI 提取出的原始 JSON 字段进行数据清洗与归一化"""
    def to_float(val) -> float:
        if val is None:
            return 0.0
        if isinstance(val, (int, float)):
            return round(float(val), 2)
        val_str = str(val).replace('¥', '').replace('￥', '').replace(',', '').strip()
        m = re.search(r'[-+]?\d*\.?\d+', val_str)
        return round(float(m.group(0)), 2) if m else 0.0

    def to_date_str(val) -> str:
        if not val:
            return ""
        val_str = str(val).strip()
        m = re.search(r'(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})', val_str)
        if m:
            return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        return val_str

    commercial_prem = to_float(raw.get("commercialPremium", 0))
    compulsory_prem = to_float(raw.get("compulsoryPremium", 0))
    tax = to_float(raw.get("tax", 0))
    accident_prem = to_float(raw.get("accidentPremium", 0))
    total_prem = to_float(raw.get("totalPremium", 0))

    # 若未提供总保费或总保费为0，尝试按分项汇总
    calc_total = round(commercial_prem + compulsory_prem + tax + accident_prem, 2)
    if total_prem <= 0 and calc_total > 0:
        total_prem = calc_total

    start_date = to_date_str(raw.get("startDate", ""))
    end_date = to_date_str(raw.get("endDate", ""))

    year_val = raw.get("year")
    if not year_val and start_date:
        m = re.match(r'(\d{4})', start_date)
        if m:
            year_val = int(m.group(1))

    return {
        "company": str(raw.get("company", "")).strip(),
        "plateNo": str(raw.get("plateNo", "")).strip().upper(),
        "vin": str(raw.get("vin", "")).strip().upper(),
        "owner": str(raw.get("owner", "")).strip(),
        "year": int(year_val) if year_val else datetime.datetime.now().year,
        "startDate": start_date,
        "endDate": end_date,
        "commercialPolicyNo": str(raw.get("commercialPolicyNo", "")).strip(),
        "compulsoryPolicyNo": str(raw.get("compulsoryPolicyNo", "")).strip(),
        "accidentPolicyNo": str(raw.get("accidentPolicyNo", "")).strip(),
        "commercialPremium": commercial_prem,
        "compulsoryPremium": compulsory_prem,
        "tax": tax,
        "accidentPremium": accident_prem,
        "totalPremium": total_prem,
        "hasDamage": bool(raw.get("hasDamage", False)),
        "hasMedicalExcluded": bool(raw.get("hasMedicalExcluded", False)),
        "thirdPartyAmount": str(raw.get("thirdPartyAmount", "")).strip(),
        "driverAmount": str(raw.get("driverAmount", "")).strip(),
        "extra": str(raw.get("extra", "")).strip(),
        "detectedPolicies": raw.get("detectedPolicies", [])
    }
