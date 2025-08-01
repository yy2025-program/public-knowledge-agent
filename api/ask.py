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
            "message": "AI Knowledge Agent API is running!",
            "status": "ok",
            "endpoints": ["GET", "POST"],
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
                question = data.get('question', '')
            else:
                question = ''
            
            # 简单的知识库
            knowledge_base = {
                "人工智能": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
                "机器学习": "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。",
                "深度学习": "深度学习是机器学习的一个子集，使用多层神经网络来模拟人脑的工作方式。",
                "爬虫": "网络爬虫是一种自动化程序，用于从网站提取数据。",
                "API": "API（应用程序编程接口）是不同软件应用程序之间通信的桥梁。"
            }
            
            # 查找答案
            answer = "抱歉，我暂时没有找到相关信息。"
            matched = False
            
            if question:
                # 精确匹配
                for keyword, content in knowledge_base.items():
                    if keyword in question:
                        answer = content
                        matched = True
                        break
                
                # 模糊匹配
                if not matched:
                    question_lower = question.lower()
                    if any(word in question_lower for word in ["ai", "智能"]):
                        answer = knowledge_base["人工智能"]
                        matched = True
                    elif any(word in question_lower for word in ["学习", "ml"]):
                        answer = knowledge_base["机器学习"]
                        matched = True
                    elif any(word in question_lower for word in ["深度", "神经"]):
                        answer = knowledge_base["深度学习"]
                        matched = True
                    elif any(word in question_lower for word in ["爬虫", "crawl"]):
                        answer = knowledge_base["爬虫"]
                        matched = True
                    elif any(word in question_lower for word in ["api", "接口"]):
                        answer = knowledge_base["API"]
                        matched = True
                
                # 默认回答
                if not matched:
                    if any(word in question for word in ["什么", "如何", "怎么", "为什么"]):
                        answer = f"关于'{question}'的问题很有价值！我可以回答关于人工智能、机器学习、深度学习、爬虫和API等技术话题的问题。"
                    else:
                        answer = "请尝试询问更具体的技术问题，比如'什么是人工智能'或'如何使用爬虫'等。"
            
            response = {
                "answer": answer,
                "sources": ["builtin"],
                "confidence": 0.8 if matched else 0.3,
                "status": "ok"
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_response = {
                "answer": "抱歉，服务出现错误，请稍后再试。",
                "error": str(e),
                "status": "error"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
