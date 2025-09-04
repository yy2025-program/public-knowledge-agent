#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import requests
from datetime import datetime

# API配置
FIRECRAWL_API_KEY = "fc-b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8"
GITHUB_API_KEY = "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"
GITHUB_API_URL = "https://models.github.ai/inference/chat/completions"
SILICONFLOW_API_KEY = "sk-jjhtgselzbsadzvxtqfiqeajhznfrxbqlwdaglorelklxzqf"
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"

articles_db = []

class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
        
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, ngrok-skip-browser-warning')
        super().end_headers()
        
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == '/' or self.path == '/health':
            response = {
                "status": "healthy",
                "message": "AI Knowledge Agent API Server",
                "version": "4.1-CORS",
                "timestamp": datetime.now().isoformat(),
                "services": {"ask_api": "running", "crawl_api": "running", "database_api": "running"},
                "ai_providers": ["GitHub Models", "SiliconFlow"]
            }
        elif self.path.startswith('/api/ask'):
            response = {"message": "Ask API is running!", "status": "ok"}
        elif self.path.startswith('/api/crawl'):
            response = {"message": "Crawl API is running!", "status": "ok"}
        elif self.path.startswith('/api/database'):
            response = {"message": "Database API is running!", "status": "ok", "stored_articles": len(articles_db)}
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
            return {"message": "Ask API is running!", "status": "ok"}
        
        # 优先尝试GitHub Models API
        try:
            headers = {
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {GITHUB_API_KEY}',
                'X-GitHub-Api-Version': '2022-11-28',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": question}],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(GITHUB_API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                ai_response = response.json()
                answer = ai_response['choices'][0]['message']['content']
                
                return {
                    "answer": answer,
                    "sources": ["GitHub Models"],
                    "confidence": 0.95,
                    "status": "ok",
                    "api_used": "GitHub Models (gpt-4o-mini)"
                }
            else:
                raise Exception(f"GitHub API error: {response.status_code}")
                
        except Exception as github_error:
            # 回退到SiliconFlow API
            try:
                headers = {
                    'Authorization': f'Bearer {SILICONFLOW_API_KEY}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    "model": "Qwen/QwQ-32B",
                    "messages": [{"role": "user", "content": question}],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
                
                response = requests.post(SILICONFLOW_API_URL, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    ai_response = response.json()
                    answer = ai_response['choices'][0]['message']['content']
                    
                    return {
                        "answer": answer,
                        "sources": ["SiliconFlow"],
                        "confidence": 0.9,
                        "status": "ok",
                        "api_used": "SiliconFlow (Qwen/QwQ-32B)"
                    }
                else:
                    raise Exception(f"SiliconFlow API error: {response.status_code}")
                    
            except Exception as silicon_error:
                return {
                    "answer": f"AI服务暂时不可用。您的问题是：{question}。请稍后再试。",
                    "sources": ["local"],
                    "confidence": 0.3,
                    "status": "ok",
                    "fallback": True
                }

    def handle_crawl(self, data):
        url = data.get('url', '')
        
        if not url:
            return {"message": "Crawl API is running!", "status": "ok"}
        
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            content = response.text[:1000] + "..." if len(response.text) > 1000 else response.text
            
            return {
                "success": True,
                "title": f"来自 {url} 的内容",
                "content": content,
                "url": url,
                "method": "简单爬虫",
                "scraped_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"无法访问URL: {url}"
            }

    def handle_database(self, data):
        action = data.get('action', '')
        
        if not action:
            return {
                "message": "Database API is running!",
                "status": "ok",
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
            return {"success": False, "message": f"未知操作: {action}"}

if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 3000))
    
    print(f"🚀 Starting CORS-enabled AI Knowledge Agent on port {PORT}")
    print("🌐 CORS headers enabled for GitHub Pages")
    
    with socketserver.TCPServer(("", PORT), CORSHandler) as httpd:
        print("✅ Server started successfully!")
        httpd.serve_forever()
