#!/bin/bash

echo "🌐 启动公网访问服务..."

# 检查ngrok是否安装
if ! command -v ngrok &> /dev/null; then
    echo "📦 安装ngrok..."
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
    sudo apt update && sudo apt install ngrok -y
fi

# 启动API服务器
echo "🚀 启动API服务器..."
python3 final_api_server.py &
API_PID=$!

# 等待服务器启动
sleep 3

# 启动ngrok
echo "🌍 启动ngrok隧道..."
ngrok http 3000 &
NGROK_PID=$!

echo ""
echo "✅ 服务启动完成！"
echo ""
echo "📋 访问信息："
echo "1. 等待10秒后访问: http://localhost:4040"
echo "2. 复制ngrok提供的公网地址"
echo "3. 在admin_railway.html中输入该地址"
echo ""
echo "🛑 按Ctrl+C停止所有服务"

# 等待用户停止
trap 'echo ""; echo "🛑 停止服务..."; kill $API_PID $NGROK_PID 2>/dev/null; echo "✅ 已停止"; exit 0' INT

while true; do
    sleep 1
done
