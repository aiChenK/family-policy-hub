# AGENTS.md - 家庭保险资产管理系统

## 项目概述
Python + Vue 3 全栈家庭保险管理系统，支持 FastAPI 异步模式与标准库零依赖降级双模运行。

## 快速启动

### 本地开发
```bash
# 方式一（推荐）：使用 Makefile 一键启动热更新全栈环境
make dev

# 方式二：手动分终端启动
# 终端 1 启动后端服务 (端口 8088)
python3 backend/main.py

# 终端 2 启动前端热更新开发服务器 (端口 5173，自动反向代理到 8088)
cd frontend && npm run dev

# 构建前端生产包
make build   # 或 cd frontend && npm run build
```

### Docker 部署
```bash
cp .env.example .env  # 可选：设置 ACCESS_PASSWORD
docker compose up -d
```

## 架构要点

### 双模运行机制
- **FastAPI 模式**：安装 `backend/requirements.txt` 后自动启用，高性能异步
- **标准库模式**：无依赖时自动降级为 `ThreadingHTTPServer`，零配置运行
- 入口文件：`backend/main.py`（亦支持 `backend/server.py`）根据依赖自动选择引擎

### 数据存储
- JSON 文件存储于 `data/` 目录，原子写入 + 自动备份轮转
- 核心文件：`policies.json`、`history_payments.json`、`vehicles.json`、`payment_records.json`
- 修改数据时务必理解 `storage.py` 的拆分保存逻辑

### 前端技术栈
- Vue 3 + Vite + Tailwind CSS + Chart.js
- 构建产物输出到 `frontend/dist/`，后端自动托管
- 开发时通过 Vite proxy 转发 `/api` 请求到后端

## 环境配置

复制 `.env.example` 为 `.env`，可配置：
- `ACCESS_PASSWORD`：留空=免密，填写后开启 HMAC 鉴权
- `PORT`：服务端口，默认 8088
- `HOST`：监听地址，默认 0.0.0.0

## 开发注意事项

### 后端修改
- `backend/config.py`：路径与环境变量解析，修改目录结构时需同步更新
- `backend/storage.py`：原子写入逻辑，新增数据文件需在此注册
- `backend/app_fastapi.py`：API 路由定义，新增接口在此添加
- 认证逻辑：`ACCESS_PASSWORD` 为空时所有接口免鉴权

### 前端修改
- 开发服务器自动代理 API，无需处理跨域
- 构建后需重新启动后端才能看到变更（`dist/` 是静态托管）
- 组件位于 `frontend/src/components/`，视图位于 `frontend/src/views/`

### 数据表格规范（列宽与吸顶交互）
系统中涉及多列展示的数据列表（如车险列表、缴费台账等），必须统一遵循以下表格交互与排版规范：
- **容器与结构声明**：
  - 外层容器使用 `overflow-x-auto custom-scrollbar`，表格标签声明 `w-full border-separate border-spacing-0 text-xs`，并根据列数设定合理的最小总宽度（如 `min-w-[1180px]` 或 `min-w-[1260px]`）。
  - 使用 `border-separate border-spacing-0` 配合单元格的 `border-b border-slate-100`，确保 Sticky 固定列在横向滚动时边框和背景不穿透、无错位。
- **头尾吸顶固定（Sticky 布局）**：
  - **头部核心标识列**（如车牌号、应缴日期等）：
    - `th` 声明 `sticky left-0 z-20 bg-slate-50 py-3.5 px-4 whitespace-nowrap min-w-[...] shadow-[2px_0_4px_-1px_rgba(0,0,0,0.06)] border-r border-slate-200/80`；
    - `td` 声明 `sticky left-0 z-10 py-3 px-4 whitespace-nowrap shadow-[2px_0_4px_-1px_rgba(0,0,0,0.06)] border-r border-slate-200/80`。
  - **尾部核心操作列**：
    - `th` 声明 `sticky right-0 z-20 bg-slate-50 py-3.5 px-4 text-right whitespace-nowrap min-w-[...] shadow-[-2px_0_4px_-1px_rgba(0,0,0,0.06)] border-l border-slate-200/80`；
    - `td` 声明 `sticky right-0 z-10 py-3 px-4 text-right whitespace-nowrap shadow-[-2px_0_4px_-1px_rgba(0,0,0,0.06)] border-l border-slate-200/80`。
  - **中间字段列**：均必须设置显式的 `whitespace-nowrap` 与具体的 `min-w-[...]`（禁止自适应缩窄折行），在不同分辨率下平滑横向滚动。
- **整行 Hover 底色联动**：
  - 行标签 `tr` 增加 `group hover:bg-slate-50/80 transition-colors`；
  - 固定列的 `td` 必须显式声明对应底色并联动悬停，例如：`:class="item.status === 'due' ? 'bg-amber-50/90 group-hover:bg-amber-100/90' : 'bg-white group-hover:bg-slate-50/90'"`，坚决杜绝因固定列背景缺失或白底盖住导致的底色割裂。
- **参考实现样例**：
  - 车险列表：`frontend/src/components/vehicle/VehicleTable.vue`
  - 缴费台账：`frontend/src/views/PaymentsView.vue`

### 验证与测试规范
- 接口与服务验证可以使用 `curl` 等命令行工具，**不使用浏览器处理**
- 需浏览器验证时仅指出具体操作步骤与预期效果，进行后续手动验证

### 数据兼容
- `data/insurance_data.json` 是旧版聚合文件，系统自动兼容读取
- 新数据写入时会同步备份到 legacy 文件（冷备）
- `data/backups/` 保留最近 10 个版本的自动备份

## 常见问题

### 端口占用
后端启动时若 8088 被占用，会自动尝试 8089

### 前端未构建
启动脚本会检测 `frontend/dist/` 是否存在，缺失时自动执行 `npm install && npm run build`

### 数据损坏恢复与备份管理

系统采用多层次的容灾与恢复机制，确保在人为误操作、意外损坏或多环境迁移时数据绝对安全：

#### 1. 智能防冗余备份机制
- **变更感知**：在写入落盘前自动校验业务数据实质变动（忽略时间戳），未变动时不产生多余 `.bak` 文件，彻底杜绝无用副本堆积；
- **滚动配额**：各分表独立维护最多 10 个历史版本快照（冷备文件保留 5 个）。

#### 2. 方式一：一键命令行安全恢复（推荐）
系统提供开箱即用的安全恢复脚本 `backend/restore.py`：
```bash
# 查看所有可用历史快照（亦可按模块筛选，如: vehicles, policies, companies）
python3 backend/restore.py list [模块名]

# 执行恢复（支持指定快照序号或完整文件名）
python3 backend/restore.py restore 1
```
> **安全保底**：脚本在执行覆盖前，会自动对当前最新数据生成一份 `*.pre_restore_<时间戳>.bak` 快照，确保任何恢复操作 100% 可逆、可随时反悔撤销。

#### 3. 方式二：手动单表精准替换（直接复制）
数据已彻底分表解耦，单模块误删或异常时无需全量回滚，直接复制对应备份即可：

| 业务模块 | 数据主文件 | 对应恢复命令示例 |
| :--- | :--- | :--- |
| **车险与爱车** | `data/vehicles.json` | `cp data/backups/vehicles.json.<时间戳>.bak data/vehicles.json` |
| **家庭人身保单** | `data/policies.json` | `cp data/backups/policies.json.<时间戳>.bak data/policies.json` |
| **缴费台账与确认** | `data/payment_records.json` | `cp data/backups/payment_records.json.<时间戳>.bak data/payment_records.json` |
| **历史已缴明细** | `data/history_payments.json` | `cp data/backups/history_payments.json.<时间戳>.bak data/history_payments.json` |
| **关联企业备查** | `data/companies.json` | `cp data/backups/companies.json.<时间戳>.bak data/companies.json` |
| **全量冷备还原** | `data/insurance_data.json` | `cp data/backups/insurance_data.json.<时间戳>.bak data/insurance_data.json` |

#### 4. 方式三：系统内置容灾自愈降级
- 后端在读取各分表时，若遇到文件缺失或格式损坏，会自动回退读取全量聚合冷备文件 `data/insurance_data.json` 并提取对应数据，保障服务正常启动与加载；
- 若机构电话文件 `insurance_phones.json` 损坏，系统会自动从代码预设库自愈重建。

#### 5. 方式四：前端 Web 界面离线导出与导入
- **导出**：在界面设置中点击导出全量数据为 `family_insurance_backup_YYYY-MM-DD.json` 文件；
- **导入**：在界面上传历史导出的 JSON 文件，前端会自动校验结构完整性并提交保存落盘。

## 版本发布与 CHANGELOG 规范

每当需要更新或发布新版本（如 `vX.Y.Z`）时，所有 AI Agent 及开发者必须严格遵守以下规范：

1. **版本号多文件同步更新**：必须**同时更新** `package.json`、`package-lock.json` 中的 `version` 字段。
2. **CHANGELOG 保持精简干练**：在 `CHANGELOG.md` 中撰写更新说明时，内容必须**保持简洁干练**，使用短句精准概括核心改进点，严禁大段冗长叙述。
3. **禁止直接执行 Git 提交**：严禁直接调用命令执行 `git commit`、`git push` 或创建标签等提交操作；应在回复中生成规范精准的建议 Git 命令（包含推荐的提交信息与 Tag 命令），由用户确认后手动执行。



