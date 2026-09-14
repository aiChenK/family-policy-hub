#!/bin/bash
# 切换至当前脚本所在目录
cd "$(dirname "$0")"

echo "================================================="
echo "  🏠 正在启动家庭保险管理系统..."
echo "================================================="

# 检测 Python3 是否存在
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未检测到系统安装的 python3，请先安装 Python 3。"
    read -p "按回车键退出..."
    exit 1
fi

# 检测前端构建产物是否存在，若不存在则尝试自动构建
if [ ! -d "frontend/dist" ] && command -v npm &> /dev/null; then
    echo "📦 首次检测到未构建前端，正在自动编译前端资源..."
    npm --prefix frontend install && npm --prefix frontend run build
fi

# 启动服务
python3 backend/main.py
