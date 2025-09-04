#!/bin/bash

echo "🚀 启动AI知识代理系统..."

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 进入项目目录
cd "$(dirname "$0")"

# 检查API服务器是否已在运行
if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo "✅ API服务器已在运行 (端口3000)"
else
    echo "🔄 启动API服务器..."
    python3 final_api_server.py &
    API_PID=$!
    
    # 等待服务器启动
    echo "⏳ 等待服务器启动..."
    for i in {1..10}; do
        if curl -s http://localhost:3000/health > /dev/null 2>&1; then
            echo "✅ API服务器启动成功 (PID: $API_PID)"
            break
        fi
        sleep 1
    done
    
    if ! curl -s http://localhost:3000/health > /dev/null 2>&1; then
        echo "❌ API服务器启动失败"
        exit 1
    fi
fi

echo ""
echo "🎉 系统启动完成！"
echo ""
echo "📡 API服务器: http://localhost:3000"
echo "🔧 管理面板: file://$(pwd)/admin_local.html"
echo "🌐 GitHub Pages: https://yy2025-program.github.io/public-knowledge-agent/"
echo ""
echo "📋 可用的API端点:"
echo "  - GET  http://localhost:3000/health (健康检查)"
echo "  - POST http://localhost:3000/api/ask (AI问答)"
echo "  - POST http://localhost:3000/api/crawl (网页爬取)"
echo "  - POST http://localhost:3000/api/database (数据库操作)"
echo ""
echo "🔑 已配置的服务:"
echo "  - FireCrawl API: fc-b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8"
echo "  - AI API: sk-jjhtgselzbsadzvxtqfiqeajhznfrxbqlwdaglorelklxzqf"
echo ""
echo "💡 使用说明:"
echo "  1. 打开 admin_local.html 进行管理"
echo "  2. 或者直接使用API端点进行开发"
echo "  3. 按 Ctrl+C 停止服务器"
echo ""

# 保持脚本运行，直到用户按Ctrl+C
trap 'echo ""; echo "🛑 正在停止服务器..."; kill $API_PID 2>/dev/null; echo "✅ 系统已停止"; exit 0' INT

echo "🔄 系统正在运行中... (按 Ctrl+C 停止)"
while true; do
    sleep 1
done
