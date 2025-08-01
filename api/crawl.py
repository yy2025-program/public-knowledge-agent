import json
from http.server import BaseHTTPRequestHandler

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
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                url = data.get('url', '')
            else:
                url = ''
            
            if not url:
                raise ValueError("URL不能为空")
            
            # 模拟爬取结果（实际项目中会使用真实爬虫）
            response_data = {
                "success": True,
                "title": f"来自 {url} 的内容",
                "content": f"这是从 {url} 爬取的模拟内容。在实际部署中，这里会使用真实的网页爬虫来获取内容。",
                "url": url,
                "scraped_at": "2024-08-01 16:20:00"
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
    
    def do_GET(self):
        # 处理GET请求（测试用）
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "Crawl API is running!",
            "usage": "POST with {\"url\": \"https://example.com\"}",
            "status": "ok"
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
