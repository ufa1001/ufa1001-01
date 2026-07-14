#!/bin/bash
# 直播间智能分配系统 API 服务启动脚本

echo "========================================"
echo "直播间智能分配系统 - API 代理服务"
echo "========================================"

# 检查 Python
echo "[1/4] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3.11+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $PYTHON_VERSION"

# 检查 .env
echo "[2/4] 检查配置文件..."
if [ ! -f ".env" ]; then
    echo "警告: 未找到 .env 文件，正在从 .env.example 复制..."
    cp .env.example .env
    echo "请编辑 .env 文件，填入你的飞书应用凭证后再启动"
    exit 1
fi

# 检查依赖
echo "[3/4] 检查依赖..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
fi

# 启动服务
echo "[4/4] 启动服务..."
echo "服务将运行在 http://0.0.0.0:8000"
echo "API 文档: http://0.0.0.0:8000/docs"
echo "========================================"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
