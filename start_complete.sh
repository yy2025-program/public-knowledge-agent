#!/bin/bash

echo "🚀 启动完整AI知识助手系统..."

# 检查API服务器
if ! curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo "⚠️  API服务器未运行，正在启动..."
    python3 final_api_server.py &
    sleep 3
fi

# 检查ngrok
if ! curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
    echo "⚠️  ngrok未运行，正在启动..."
    ngrok http 3000 &
    sleep 5
fi

# 获取ngrok地址
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data['tunnels'] else '')" 2>/dev/null)

echo ""
echo "✅ 系统启动完成！"
echo ""
echo "📱 使用方式："
echo "1. 本地访问: file://$(pwd)/complete_ui.html"
echo "2. 公网地址: ${NGROK_URL:-'获取中...'}"
echo ""
echo "🌐 在浏览器中打开 complete_ui.html 即可使用完整功能！"
echo ""

# 尝试自动打开浏览器
if command -v xdg-open > /dev/null; then
    echo "🔄 正在打开浏览器..."
    xdg-open "file://$(pwd)/complete_ui.html"
elif command -v open > /dev/null; then
    open "file://$(pwd)/complete_ui.html"
fi
