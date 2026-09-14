.PHONY: help dev start build install clean

# 默认指令：显示可用命令帮助
help:
	@echo "================================================================="
	@echo "  🏠 家庭保险资产管理系统 - 指令清单"
	@echo "================================================================="
	@echo "  make dev      - 启动开发环境（后端 API + 前端 Vite 热更新 HMR）"
	@echo "  make start    - 启动生产/静态托管环境（运行后端并托管 dist）"
	@echo "  make build    - 编译前端生产静态包到 frontend/dist"
	@echo "  make install  - 安装前端与后端所需依赖"
	@echo "  make clean    - 清理前端构建产物"
	@echo "================================================================="

# 开发模式：同时启动 Python 后端与前端 Vite 热更新开发服务器
dev:
	@echo "🚀 正在启动全栈开发模式..."
	@if [ ! -d "frontend/node_modules" ]; then \
		echo "📦 检测到未安装前端依赖，正在执行 npm install..."; \
		npm --prefix frontend install; \
	fi
	@echo "-----------------------------------------------------------------"
	@echo "  🌐 前端热更新地址: http://localhost:5173"
	@echo "  ⚙️  后端 API 接口:  http://localhost:8088"
	@echo "  💡 提示: 按 Ctrl+C 可一并停止所有前后端进程"
	@echo "-----------------------------------------------------------------"
	@bash -c '\
		trap "echo -e \"\n🛑 正在停止所有服务...\"; kill \$$BACKEND_PID \$$FRONTEND_PID 2>/dev/null; exit 0" INT TERM EXIT; \
		NO_BROWSER=1 python3 backend/main.py & \
		BACKEND_PID=$$!; \
		npm --prefix frontend run dev & \
		FRONTEND_PID=$$!; \
		wait \
	'

# 编译前端生产静态包
build:
	@echo "📦 正在编译前端..."
	@if [ ! -d "frontend/node_modules" ]; then \
		echo "📦 正在安装前端依赖..."; \
		npm --prefix frontend install; \
	fi
	@npm --prefix frontend run build
	@echo "✅ 前端编译完成，产物已输出至 frontend/dist"

# 生产/直接运行模式（后端直接托管 frontend/dist）
start:
	@if [ ! -d "frontend/dist" ]; then \
		echo "📦 未检测到前端构建产物，正在自动编译..."; \
		$(MAKE) build; \
	fi
	@echo "🏠 正在启动服务..."
	@python3 backend/main.py

# 安装依赖
install:
	@echo "📦 正在安装前端依赖..."
	@npm --prefix frontend install
	@if [ -f "backend/requirements.txt" ]; then \
		echo "📦 正在安装后端依赖 (可选)..."; \
		pip3 install -r backend/requirements.txt || true; \
	fi
	@echo "✅ 所有依赖安装完成"

# 清理构建产物
clean:
	@echo "🧹 正在清理前端构建文件..."
	@rm -rf frontend/dist
	@echo "✅ 清理完成"
