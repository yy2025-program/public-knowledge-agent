#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests

class AIHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, ngrok-skip-browser-warning')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"status": "healthy", "message": "AI Server Running"}
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        if self.path == '/api/ask':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            question = data.get('question', '')
            
            try:
                # GitHub Models API
                headers = {
                    'Accept': 'application/vnd.github+json',
                    'Authorization': 'Bearer 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',
                    'X-GitHub-Api-Version': '2022-11-28',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": question}],
                    "max_tokens": 500
                }
                
                response = requests.post('https://models.github.ai/inference/chat/completions', 
                                       headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    ai_response = response.json()
                    answer = ai_response['choices'][0]['message']['content']
                    result = {
                        "answer": answer,
                        "api_used": "GitHub Models (gpt-4o-mini)",
                        "status": "ok"
                    }
                else:
                    result = {"answer": "AI服务暂时不可用", "status": "error"}
                    
            except Exception as e:
                result = {"answer": f"错误: {str(e)}", "status": "error"}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

if __name__ == '__main__':
    server = HTTPServer(('localhost', 3000), AIHandler)
    print("🚀 AI Server running on port 3000")
    server.serve_forever()
