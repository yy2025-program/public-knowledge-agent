from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = {
            "message": "Database API is running!",
            "status": "ok",
            "storage": ["local_cache", "supabase_ready"],
            "version": "1.0"
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                action = data.get('action', '')
            else:
                action = ''
            
            if action == 'store_article':
                # 模拟存储
                response_data = {
                    "success": True,
                    "message": "文章已存储到本地缓存",
                    "storage_type": "local_cache",
                    "data": {
                        "title": data.get('title', ''),
                        "url": data.get('url', ''),
                        "stored_at": "2024-08-01 16:50:00"
                    }
                }
            
            elif action == 'search_articles':
                # 模拟搜索
                query = data.get('query', '')
                mock_articles = [
                    {
                        "id": 1,
                        "title": f"关于'{query}'的文章",
                        "content": f"这是关于{query}的模拟内容。",
                        "url": "https://example.com/mock-article",
                        "category": "technology"
                    }
                ]
                
                response_data = {
                    "success": True,
                    "articles": mock_articles,
                    "count": len(mock_articles),
                    "storage_type": "local_cache"
                }
            
            else:
                response_data = {
                    "success": False,
                    "message": f"未知操作: {action}"
                }
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e),
                "message": "数据库操作失败"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
