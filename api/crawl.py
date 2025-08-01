from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
import time

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 设置CORS头
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # 读取请求数据
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            url = data.get('url', '')
            
            if not url:
                raise ValueError("URL不能为空")
            
            # 简单的网页爬取（实际项目中会使用FireCrawl）
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取主要内容
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "无标题"
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 提取文本内容
            content = soup.get_text()
            
            # 清理文本
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content_clean = ' '.join(chunk for chunk in chunks if chunk)
            
            # 限制内容长度
            if len(content_clean) > 2000:
                content_clean = content_clean[:2000] + "..."
            
            response_data = {
                "success": True,
                "title": title_text,
                "content": content_clean,
                "url": url,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e),
                "message": "爬取失败，请检查URL是否正确"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
