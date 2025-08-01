from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # 启用CORS

# 知识库
knowledge_base = {
    "人工智能": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。它包括机器学习、深度学习、自然语言处理等多个子领域。",
    "机器学习": "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。通过算法分析数据，识别模式，并做出预测或决策。",
    "深度学习": "深度学习是机器学习的一个子集，使用多层神经网络来模拟人脑的工作方式。它在图像识别、语音识别和自然语言处理等领域表现出色。",
    "爬虫": "网络爬虫是一种自动化程序，用于从网站提取数据。它可以系统地浏览网页，收集信息并存储到数据库中，常用于数据挖掘和信息聚合。",
    "API": "API（应用程序编程接口）是不同软件应用程序之间通信的桥梁。它定义了请求和响应的格式，使开发者能够集成不同的服务和功能。",
    "FireCrawl": "FireCrawl是一个强大的网页爬取服务，能够处理JavaScript渲染的页面，提取结构化数据，并支持多种输出格式。",
    "Supabase": "Supabase是一个开源的Firebase替代品，提供实时数据库、身份验证、存储等服务。"
}

@app.route('/')
def home():
    return jsonify({
        "message": "AI Knowledge Agent API Server",
        "status": "running",
        "endpoints": ["/api/ask", "/api/crawl", "/api/database"],
        "version": "2.0"
    })

@app.route('/api/ask', methods=['GET', 'POST', 'OPTIONS'])
def ask():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            question = data.get('question', '')
        else:
            question = request.args.get('question', '')
        
        if not question:
            return jsonify({
                "message": "Ask API is running!",
                "status": "ok",
                "usage": "POST with {\"question\": \"your question\"}"
            })
        
        # 查找答案
        answer = "抱歉，我暂时没有找到相关信息。"
        matched = False
        
        # 精确匹配
        for keyword, content in knowledge_base.items():
            if keyword in question:
                answer = content
                matched = True
                break
        
        # 模糊匹配
        if not matched:
            question_lower = question.lower()
            if any(word in question_lower for word in ["ai", "智能", "artificial"]):
                answer = knowledge_base["人工智能"]
                matched = True
            elif any(word in question_lower for word in ["学习", "learning", "ml"]):
                answer = knowledge_base["机器学习"]
                matched = True
            elif any(word in question_lower for word in ["神经", "网络", "deep", "深度"]):
                answer = knowledge_base["深度学习"]
                matched = True
            elif any(word in question_lower for word in ["爬虫", "spider", "crawl", "scrape"]):
                answer = knowledge_base["爬虫"]
                matched = True
            elif any(word in question_lower for word in ["api", "接口", "interface"]):
                answer = knowledge_base["API"]
                matched = True
            elif any(word in question_lower for word in ["firecrawl", "fire"]):
                answer = knowledge_base["FireCrawl"]
                matched = True
            elif any(word in question_lower for word in ["supabase", "数据库", "database"]):
                answer = knowledge_base["Supabase"]
                matched = True
        
        # 默认回答
        if not matched:
            if any(word in question for word in ["什么", "如何", "怎么", "为什么", "是什么"]):
                answer = f"关于'{question}'的问题很有价值！我的知识库目前包含人工智能、机器学习、深度学习、爬虫、API、FireCrawl和Supabase等技术话题。请尝试询问这些领域的具体问题。"
            else:
                answer = "请尝试询问更具体的技术问题，比如'什么是人工智能'、'如何使用FireCrawl'或'Supabase是什么'等。"
        
        return jsonify({
            "answer": answer,
            "sources": ["builtin"],
            "confidence": 0.8 if matched else 0.3,
            "status": "ok"
        })
        
    except Exception as e:
        return jsonify({
            "answer": "抱歉，服务出现错误，请稍后再试。",
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/crawl', methods=['GET', 'POST', 'OPTIONS'])
def crawl():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            url = data.get('url', '')
        else:
            url = request.args.get('url', '')
        
        if not url:
            return jsonify({
                "message": "Crawl API is running!",
                "status": "ok",
                "usage": "POST with {\"url\": \"https://example.com\"}"
            })
        
        # 模拟爬取结果
        return jsonify({
            "success": True,
            "title": f"来自 {url} 的内容",
            "content": f"这是从 {url} 爬取的模拟内容。在实际部署中，这里会使用真实的网页爬虫来获取内容。",
            "url": url,
            "method": "简单爬虫",
            "scraped_at": "2024-08-01 17:00:00"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "爬取失败，请检查URL是否正确"
        }), 500

@app.route('/api/database', methods=['GET', 'POST', 'OPTIONS'])
def database():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            action = data.get('action', '')
        else:
            action = request.args.get('action', '')
        
        if not action:
            return jsonify({
                "message": "Database API is running!",
                "status": "ok",
                "actions": ["store_article", "search_articles"]
            })
        
        if action == 'store_article':
            return jsonify({
                "success": True,
                "message": "文章已存储到本地缓存",
                "storage_type": "local_cache",
                "data": {
                    "title": data.get('title', ''),
                    "url": data.get('url', ''),
                    "stored_at": "2024-08-01 17:00:00"
                }
            })
        
        elif action == 'search_articles':
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
            
            return jsonify({
                "success": True,
                "articles": mock_articles,
                "count": len(mock_articles),
                "storage_type": "local_cache"
            })
        
        else:
            return jsonify({
                "success": False,
                "message": f"未知操作: {action}"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "数据库操作失败"
        }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
