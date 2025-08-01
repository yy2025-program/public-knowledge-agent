from http.server import BaseHTTPRequestHandler
import json
import sqlite3
import os
from urllib.parse import parse_qs

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
            
            question = data.get('question', '')
            
            # 简单的知识库匹配（实际项目中会连接数据库）
            knowledge_base = {
                "人工智能": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。它包括机器学习、深度学习、自然语言处理等多个子领域。",
                "机器学习": "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。通过算法分析数据，识别模式，并做出预测或决策。",
                "深度学习": "深度学习是机器学习的一个子集，使用多层神经网络来模拟人脑的工作方式。它在图像识别、语音识别和自然语言处理等领域表现出色。",
                "爬虫": "网络爬虫是一种自动化程序，用于从网站提取数据。它可以系统地浏览网页，收集信息并存储到数据库中，常用于数据挖掘和信息聚合。",
                "API": "API（应用程序编程接口）是不同软件应用程序之间通信的桥梁。它定义了请求和响应的格式，使开发者能够集成不同的服务和功能。"
            }
            
            # 查找匹配的答案
            answer = "抱歉，我暂时没有找到相关信息。"
            for keyword, content in knowledge_base.items():
                if keyword in question:
                    answer = content
                    break
            
            # 如果没有直接匹配，提供智能回答
            if answer == "抱歉，我暂时没有找到相关信息。":
                if any(word in question for word in ["什么", "如何", "怎么", "为什么"]):
                    answer = f"关于'{question}'的问题很有价值！我的知识库正在不断更新中。目前我可以回答关于人工智能、机器学习、深度学习、爬虫和API等技术话题的问题。"
                else:
                    answer = "请尝试询问更具体的技术问题，比如'什么是人工智能'或'如何使用爬虫'等。"
            
            response = {
                "answer": answer,
                "sources": ["知识库"],
                "confidence": 0.8
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_response = {
                "answer": "抱歉，服务出现错误，请稍后再试。",
                "error": str(e)
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
