#!/usr/bin/env python3
import http.server
import socketserver
import json
import requests
from datetime import datetime

# API配置
GITHUB_API_KEY = "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"
GITHUB_API_URL = "https://models.github.ai/inference/chat/completions"
SILICONFLOW_API_KEY = "sk-jjhtgselzbsadzvxtqfiqeajhznfrxbqlwdaglorelklxzqf"
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"

class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, ngrok-skip-browser-warning')
        super().end_headers()
        
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if self.path == '/' or self.path == '/health':
                response = {
                    "status": "healthy",
                    "message": "AI Knowledge Agent API Server",
                    "version": "4.2-Fixed",
                    "timestamp": datetime.now().isoformat(),
                    "services": {"ask_api": "running", "crawl_api": "running", "database_api": "running"},
                    "ai_providers": ["GitHub Models", "SiliconFlow"]
                }
            else:
                response = {"message": "API is running!", "status": "ok"}
            
            self.wfile.write(json.dumps(response).encode())
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_POST(self):
        try:
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
            else:
                response = {"message": "API is running!", "status": "ok"}
            
            self.wfile.write(json.dumps(response).encode())
        except (BrokenPipeError, ConnectionResetError):
            pass

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

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    PORT = 3001
    print(f"🚀 Starting Fixed AI Server on port {PORT}")
    
    with ReusableTCPServer(("", PORT), CORSHandler) as httpd:
        print("✅ Server started successfully!")
        httpd.serve_forever()
