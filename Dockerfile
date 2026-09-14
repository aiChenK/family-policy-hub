# ==================== Stage 1: 前端静态资源编译 ====================
FROM node:20-alpine AS frontend-builder

WORKDIR /build
# 优先拷贝包清单以充分利用 Docker 缓存层
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build


# ==================== Stage 2: Python 极轻量生产镜像 ====================
FROM python:3.11-alpine

# 设置环境变量与时区
ENV PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai \
    PORT=8088 \
    HOST=0.0.0.0 \
    NO_BROWSER=1

WORKDIR /app

# 安装 tzdata 确保时区正确
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# 安装 Python 依赖
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码与前端构建产物 (彻底剥离前端源码与 node_modules，大幅减小镜像体积)
COPY backend/ ./backend/
COPY --from=frontend-builder /build/dist ./frontend/dist
COPY favicon.ico ./favicon.ico

# 预先创建数据卷挂载点
RUN mkdir -p /app/data/attachments /app/data/backups

# 暴露服务端口
EXPOSE 8088

# 挂载卷
VOLUME ["/app/data"]

# 启动服务
CMD ["python3", "backend/main.py"]
