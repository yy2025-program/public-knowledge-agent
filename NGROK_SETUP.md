# 🌐 ngrok公网访问设置

## 📋 步骤

### 1. 安装ngrok
```bash
# 下载ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin
```

### 2. 配置认证
```bash
# 从 https://dashboard.ngrok.com/get-started/your-authtoken 获取token
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

### 3. 启动服务
```bash
# 终端1: 启动API服务器
cd /home/ste92/public-knowledge-agent
python3 final_api_server.py

# 终端2: 启动ngrok
ngrok http 3000
```

### 4. 获取公网地址
- ngrok启动后会显示公网地址，如: `https://abc123.ngrok.io`
- 复制这个地址

### 5. 使用管理面板
- 打开 `admin_railway.html`
- 输入ngrok提供的地址
- 开始使用！

## 🎯 当前状态
✅ API服务器已启动: http://localhost:3000
⏳ 等待ngrok配置

## 🔧 手动操作
由于权限限制，请手动执行以下命令：

1. **安装ngrok** (如果未安装):
   ```bash
   # 方法1: 直接下载
   wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
   tar xvzf ngrok-v3-stable-linux-amd64.tgz
   
   # 方法2: 使用包管理器
   sudo snap install ngrok
   ```

2. **配置认证**:
   ```bash
   ./ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
   ```

3. **启动隧道**:
   ```bash
   ./ngrok http 3000
   ```

完成后，你就可以把ngrok提供的公网地址分享给任何人使用了！
