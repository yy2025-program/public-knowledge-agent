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
                question = data.get('question', '')
                use_ai = data.get('use_ai', False)
                search_database = data.get('search_database', True)
            else:
                question = ''
                use_ai = False
                search_database = True
            
            # 1. 首先尝试从数据库搜索
            database_results = []
            if search_database:
                database_results = self.search_database(question)
            
            # 2. 如果数据库有结果，使用数据库内容
            if database_results:
                answer = self.generate_answer_from_database(question, database_results)
                sources = [{"type": "database", "count": len(database_results)}]
                confidence = 0.9
            
            # 3. 否则使用内置知识库
            else:
                answer, matched = self.search_builtin_knowledge(question)
                sources = [{"type": "builtin", "matched": matched}]
                confidence = 0.8 if matched else 0.3
            
            # 4. 如果启用AI增强，尝试改进答案
            if use_ai and self.has_ai_api():
                try:
                    enhanced_answer = self.enhance_with_ai(question, answer)
                    if enhanced_answer:
                        answer = enhanced_answer
                        sources.append({"type": "ai_enhanced"})
                        confidence = min(confidence + 0.1, 1.0)
                except:
                    pass  # AI增强失败时继续使用原答案
            
            response = {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "features_used": {
                    "database_search": search_database,
                    "ai_enhancement": use_ai and self.has_ai_api(),
                    "builtin_knowledge": True
                }
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_response = {
                "answer": "抱歉，服务出现错误，请稍后再试。",
                "error": str(e),
                "sources": [{"type": "error"}],
                "confidence": 0.0
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def search_database(self, question):
        """搜索数据库中的文章"""
        try:
            # 调用数据库API
            database_url = "https://public-knowledge-agent.vercel.app/api/database"
            
            payload = {
                "action": "search_articles",
                "query": question,
                "limit": 3
            }
            
            req = urllib.request.Request(
                database_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            if result.get('success'):
                return result.get('articles', [])
            
        except:
            pass  # 数据库搜索失败时静默处理
        
        return []
    
    def generate_answer_from_database(self, question, articles):
        """基于数据库文章生成答案"""
        if not articles:
            return "抱歉，没有找到相关信息。"
        
        # 合并文章内容
        combined_content = ""
        for article in articles[:2]:  # 最多使用前2篇文章
            content = article.get('content', '')[:500]  # 限制长度
            combined_content += f"{content}\n\n"
        
        # 简单的答案生成
        answer = f"根据我的知识库，关于'{question}'的信息如下：\n\n{combined_content.strip()}"
        
        if len(answer) > 800:
            answer = answer[:800] + "..."
        
        return answer
    
    def search_builtin_knowledge(self, question):
        """搜索内置知识库"""
        knowledge_base = {
            "人工智能": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。它包括机器学习、深度学习、自然语言处理等多个子领域。",
            "机器学习": "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。通过算法分析数据，识别模式，并做出预测或决策。",
            "深度学习": "深度学习是机器学习的一个子集，使用多层神经网络来模拟人脑的工作方式。它在图像识别、语音识别和自然语言处理等领域表现出色。",
            "爬虫": "网络爬虫是一种自动化程序，用于从网站提取数据。它可以系统地浏览网页，收集信息并存储到数据库中，常用于数据挖掘和信息聚合。",
            "API": "API（应用程序编程接口）是不同软件应用程序之间通信的桥梁。它定义了请求和响应的格式，使开发者能够集成不同的服务和功能。",
            "FireCrawl": "FireCrawl是一个强大的网页爬取服务，能够处理JavaScript渲染的页面，提取结构化数据，并支持多种输出格式如Markdown和HTML。",
            "Supabase": "Supabase是一个开源的Firebase替代品，提供实时数据库、身份验证、存储等服务，特别适合快速构建现代应用程序。"
        }
        
        # 精确匹配
        for keyword, content in knowledge_base.items():
            if keyword in question:
                return content, True
        
        # 模糊匹配
        question_lower = question.lower()
        if any(word in question_lower for word in ["ai", "智能", "artificial"]):
            return knowledge_base["人工智能"], True
        elif any(word in question_lower for word in ["学习", "learning", "ml"]):
            return knowledge_base["机器学习"], True
        elif any(word in question_lower for word in ["神经", "网络", "deep", "深度"]):
            return knowledge_base["深度学习"], True
        elif any(word in question_lower for word in ["爬虫", "spider", "crawl", "scrape"]):
            return knowledge_base["爬虫"], True
        elif any(word in question_lower for word in ["api", "接口", "interface"]):
            return knowledge_base["API"], True
        elif any(word in question_lower for word in ["firecrawl", "fire"]):
            return knowledge_base["FireCrawl"], True
        elif any(word in question_lower for word in ["supabase", "数据库", "database"]):
            return knowledge_base["Supabase"], True
        
        # 默认回答
        if any(word in question for word in ["什么", "如何", "怎么", "为什么", "是什么"]):
            answer = f"关于'{question}'的问题很有价值！我的知识库目前包含人工智能、机器学习、深度学习、爬虫、API、FireCrawl和Supabase等技术话题。请尝试询问这些领域的具体问题。"
        else:
            answer = "请尝试询问更具体的技术问题，比如'什么是人工智能'、'如何使用FireCrawl'或'Supabase是什么'等。"
        
        return answer, False
    
    def has_ai_api(self):
        """检查是否配置了AI API"""
        return bool(os.environ.get('HUGGINGFACE_API_KEY') or os.environ.get('OPENAI_API_KEY'))
    
    def enhance_with_ai(self, question, base_answer):
        """使用AI API增强答案"""
        # 这里可以集成Hugging Face或OpenAI API
        # 目前返回None表示未实现
        return None
    
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
        
        features = {
            "database_search": True,
            "builtin_knowledge": True,
            "ai_enhancement": self.has_ai_api(),
            "firecrawl_integration": bool(os.environ.get('FIRECRAWL_API_KEY')),
            "supabase_storage": bool(os.environ.get('SUPABASE_URL'))
        }
        
        response = {
            "message": "Enhanced AI Knowledge Agent API is running!",
            "features": features,
            "endpoints": ["/api/ask", "/api/crawl", "/api/database"],
            "status": "ok"
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
