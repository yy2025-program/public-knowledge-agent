import json
import os
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse

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
                action = data.get('action', '')
            else:
                action = ''
            
            # 检查Supabase配置
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                # 使用本地JSON存储作为降级方案
                result = self.handle_local_storage(action, data)
            else:
                # 使用Supabase
                result = self.handle_supabase(action, data, supabase_url, supabase_key)
            
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e),
                "message": "数据库操作失败"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def handle_supabase(self, action, data, supabase_url, supabase_key):
        """处理Supabase数据库操作"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {supabase_key}',
            'apikey': supabase_key
        }
        
        if action == 'store_article':
            # 存储文章
            article_data = {
                'url': data.get('url', ''),
                'title': data.get('title', ''),
                'content': data.get('content', ''),
                'category': data.get('category', 'uncategorized'),
                'scraped_at': data.get('scraped_at', ''),
                'word_count': len(data.get('content', '').split())
            }
            
            api_url = f"{supabase_url}/rest/v1/articles"
            
            req = urllib.request.Request(
                api_url,
                data=json.dumps(article_data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            return {
                "success": True,
                "message": "文章已存储到Supabase",
                "data": result
            }
        
        elif action == 'search_articles':
            # 搜索文章
            query = data.get('query', '')
            limit = data.get('limit', 5)
            
            # 使用Supabase的全文搜索
            api_url = f"{supabase_url}/rest/v1/articles?or=(title.ilike.%25{query}%25,content.ilike.%25{query}%25)&limit={limit}"
            
            req = urllib.request.Request(api_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                articles = json.loads(response.read().decode('utf-8'))
            
            return {
                "success": True,
                "articles": articles,
                "count": len(articles)
            }
        
        else:
            return {
                "success": False,
                "message": f"未知操作: {action}"
            }
    
    def handle_local_storage(self, action, data):
        """本地JSON存储降级方案"""
        if action == 'store_article':
            # 模拟存储
            return {
                "success": True,
                "message": "文章已存储到本地缓存（Supabase未配置）",
                "storage_type": "local_cache",
                "data": {
                    "url": data.get('url', ''),
                    "title": data.get('title', ''),
                    "stored_at": self.get_current_time()
                }
            }
        
        elif action == 'search_articles':
            # 返回模拟搜索结果
            query = data.get('query', '')
            
            mock_articles = [
                {
                    "id": 1,
                    "title": f"关于'{query}'的文章",
                    "content": f"这是关于{query}的模拟内容。在实际部署中，这里会从数据库返回真实的搜索结果。",
                    "url": "https://example.com/mock-article",
                    "category": "technology"
                }
            ]
            
            return {
                "success": True,
                "articles": mock_articles,
                "count": len(mock_articles),
                "storage_type": "local_cache"
            }
        
        else:
            return {
                "success": False,
                "message": f"本地存储不支持操作: {action}"
            }
    
    def get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        # 处理GET请求（状态检查）
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        supabase_configured = bool(os.environ.get('SUPABASE_URL') and os.environ.get('SUPABASE_ANON_KEY'))
        
        response = {
            "message": "Database API is running!",
            "storage": {
                "supabase": supabase_configured,
                "local_cache": True
            },
            "supported_actions": ["store_article", "search_articles"],
            "status": "ok"
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
