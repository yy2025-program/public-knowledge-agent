#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.parse
import requests
from datetime import datetime
import threading

# API配置
FIRECRAWL_API_KEY = "fc-b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8"
AI_API_KEY = "sk-jjhtgselzbsadzvxtqfiqeajhznfrxbqlwdaglorelklxzqf"
AI_API_URL = "https://api.siliconflow.cn/v1/chat/completions"

# 简单的内存数据库
articles_db = []

class APIHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # 减少日志输出
        pass
        
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/':
            response = {
                "message": "AI Knowledge Agent API Server",
                "status": "running",
                "endpoints": ["/api/ask", "/api/crawl", "/api/database"],
                "version": "3.0",
                "timestamp": datetime.now().isoformat()
            }
        elif self.path.startswith('/api/ask'):
            response = {
                "message": "Ask API is running!",
                "status": "ok",
                "usage": "POST with {\"question\": \"your question\"}"
            }
        elif self.path.startswith('/api/crawl'):
            response = {
                "message": "Crawl API is running!",
                "status": "ok",
                "usage": "POST with {\"url\": \"https://example.com\"}"
            }
        elif self.path.startswith('/api/database'):
            response = {
                "message": "Database API is running!",
                "status": "ok",
                "actions": ["store_article", "search_articles", "test_connection"],
                "stored_articles": len(articles_db)
            }
        elif self.path == '/health':
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "ask_api": "running",
                    "crawl_api": "running", 
                    "database_api": "running"
                }
            }
        else:
            response = {"error": "Not found"}
        
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            data = {}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/api/ask':
            response = self.handle_ask(data)
        elif self.path == '/api/crawl':
            response = self.handle_crawl(data)
        elif self.path == '/api/database':
            response = self.handle_database(data)
        else:
            response = {"error": "Not found"}
        
        self.wfile.write(json.dumps(response).encode())

    def handle_ask(self, data):
        question = data.get('question', '')
        
        if not question:
            return {
                "message": "Ask API is running!",
                "status": "ok",
                "usage": "POST with {\"question\": \"your question\"}"
            }
        
        # 尝试使用AI API
        try:
            headers = {
                'Authorization': f'Bearer {AI_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "Qwen/QwQ-32B",
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(AI_API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                ai_response = response.json()
                answer = ai_response['choices'][0]['message']['content']
                
                return {
                    "answer": answer,
                    "sources": ["AI API"],
                    "confidence": 0.9,
                    "status": "ok",
                    "api_used": "SiliconFlow"
                }
            else:
                raise Exception(f"AI API error: {response.status_code}")
                
        except Exception as e:
            # 回退到简单回答
            return {
                "answer": f"AI服务暂时不可用。您的问题是：{question}。请稍后再试。",
                "sources": ["local"],
                "confidence": 0.3,
                "status": "ok",
                "fallback": True,
                "error": str(e)
            }

    def handle_crawl(self, data):
        url = data.get('url', '')
        
        if not url:
            return {
                "message": "Crawl API is running!",
                "status": "ok",
                "usage": "POST with {\"url\": \"https://example.com\"}"
            }
        
        # 尝试使用FireCrawl API
        try:
            headers = {
                'Authorization': f'Bearer {FIRECRAWL_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": True
            }
            
            response = requests.post('https://api.firecrawl.dev/v1/scrape', 
                                   headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                crawl_data = response.json()
                
                return {
                    "success": True,
                    "title": crawl_data.get('data', {}).get('metadata', {}).get('title', 'Unknown Title'),
                    "content": crawl_data.get('data', {}).get('markdown', 'No content extracted'),
                    "url": url,
                    "method": "FireCrawl API",
                    "scraped_at": datetime.now().isoformat()
                }
            else:
                raise Exception(f"FireCrawl API error: {response.status_code}")
                
        except Exception as e:
            # 回退到简单爬取
            try:
                response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                content = response.text[:1000] + "..." if len(response.text) > 1000 else response.text
                
                return {
                    "success": True,
                    "title": f"来自 {url} 的内容",
                    "content": f"FireCrawl服务暂时不可用，使用简单爬取：\n\n{content}",
                    "url": url,
                    "method": "简单爬虫（回退）",
                    "scraped_at": datetime.now().isoformat(),
                    "fallback": True,
                    "error": str(e)
                }
            except Exception as simple_error:
                return {
                    "success": False,
                    "error": str(simple_error),
                    "message": f"无法访问URL: {url}"
                }

    def handle_database(self, data):
        action = data.get('action', '')
        
        if not action:
            return {
                "message": "Database API is running!",
                "status": "ok",
                "actions": ["store_article", "search_articles", "test_connection"],
                "stored_articles": len(articles_db)
            }
        
        if action == 'test_connection':
            return {
                "success": True,
                "message": "数据库连接正常",
                "storage_type": "memory_cache",
                "stored_articles": len(articles_db),
                "timestamp": datetime.now().isoformat()
            }
        
        elif action == 'store_article':
            article = {
                "id": len(articles_db) + 1,
                "title": data.get('title', ''),
                "content": data.get('content', ''),
                "url": data.get('url', ''),
                "stored_at": datetime.now().isoformat()
            }
            articles_db.append(article)
            
            return {
                "success": True,
                "message": "文章已存储到内存数据库",
                "storage_type": "memory_cache",
                "data": article
            }
        
        elif action == 'search_articles':
            query = data.get('query', '').lower()
            
            if not query:
                return {
                    "success": True,
                    "articles": articles_db,
                    "count": len(articles_db),
                    "storage_type": "memory_cache"
                }
            
            # 搜索匹配的文章
            matching_articles = []
            for article in articles_db:
                if (query in article.get('title', '').lower() or 
                    query in article.get('content', '').lower()):
                    matching_articles.append(article)
            
            return {
                "success": True,
                "articles": matching_articles,
                "count": len(matching_articles),
                "storage_type": "memory_cache",
                "query": query
            }
        
        else:
            return {
                "success": False,
                "message": f"未知操作: {action}"
            }

def start_server():
    PORT = 3000
    
    print(f"🚀 Starting AI Knowledge Agent on port {PORT}")
    print("📡 Available endpoints:")
    print("  - GET  / (API info)")
    print("  - POST /api/ask (AI问答)")
    print("  - POST /api/crawl (网页爬取)") 
    print("  - POST /api/database (数据库操作)")
    print("  - GET  /health (健康检查)")
    print(f"🔑 FireCrawl API: {'✅ 已配置' if FIRECRAWL_API_KEY else '❌ 未配置'}")
    print(f"🤖 AI API: {'✅ 已配置' if AI_API_KEY else '❌ 未配置'}")
    print(f"\n🌐 Server running at: http://localhost:{PORT}")
    print("🔗 Update your admin.html API_BASE_URL to: http://localhost:3000")
    
    try:
        with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
            print("✅ Server started successfully!")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {PORT} is already in use. Trying port 3001...")
            PORT = 3001
            with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
                print(f"✅ Server started successfully on port {PORT}!")
                print(f"🔗 Update your admin.html API_BASE_URL to: http://localhost:{PORT}")
                httpd.serve_forever()
        else:
            raise

if __name__ == "__main__":
    start_server()
