from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# API配置 - 使用你提供的密钥
FIRECRAWL_API_KEY = "fc-b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8"
AI_API_KEY = "sk-jjhtgselzbsadzvxtqfiqeajhznfrxbqlwdaglorelklxzqf"
AI_API_URL = "https://api.siliconflow.cn/v1/chat/completions"

# 简单的内存数据库
articles_db = []
knowledge_base = {
    "人工智能": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
    "机器学习": "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。",
    "深度学习": "深度学习是机器学习的一个子集，使用多层神经网络来模拟人脑的工作方式。"
}

@app.route('/')
def home():
    return jsonify({
        "message": "AI Knowledge Agent API Server",
        "status": "running",
        "endpoints": ["/api/ask", "/api/crawl", "/api/database"],
        "version": "3.0",
        "timestamp": datetime.now().isoformat()
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
                
                return jsonify({
                    "answer": answer,
                    "sources": ["AI API"],
                    "confidence": 0.9,
                    "status": "ok",
                    "api_used": "SiliconFlow"
                })
            else:
                print(f"AI API Error: {response.status_code} - {response.text}")
                raise Exception(f"AI API error: {response.status_code}")
                
        except Exception as ai_error:
            print(f"AI API Exception: {ai_error}")
            
            # 回退到本地知识库
            answer = "抱歉，AI服务暂时不可用。"
            matched = False
            
            for keyword, content in knowledge_base.items():
                if keyword in question:
                    answer = content
                    matched = True
                    break
            
            if not matched:
                answer = "AI服务暂时不可用，请稍后再试。您可以询问关于人工智能、机器学习、深度学习等技术问题。"
            
            return jsonify({
                "answer": answer,
                "sources": ["local"],
                "confidence": 0.6 if matched else 0.3,
                "status": "ok",
                "fallback": True,
                "error": str(ai_error)
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
        
        # 尝试使用FireCrawl API
        try:
            headers = {
                'Authorization': f'Bearer {FIRECRAWL_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "url": url,
                "formats": ["markdown", "html"],
                "onlyMainContent": True
            }
            
            response = requests.post('https://api.firecrawl.dev/v1/scrape', 
                                   headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                crawl_data = response.json()
                
                return jsonify({
                    "success": True,
                    "title": crawl_data.get('data', {}).get('metadata', {}).get('title', 'Unknown Title'),
                    "content": crawl_data.get('data', {}).get('markdown', 'No content extracted'),
                    "url": url,
                    "method": "FireCrawl API",
                    "scraped_at": datetime.now().isoformat(),
                    "metadata": crawl_data.get('data', {}).get('metadata', {})
                })
            else:
                print(f"FireCrawl API Error: {response.status_code} - {response.text}")
                raise Exception(f"FireCrawl API error: {response.status_code}")
                
        except Exception as crawl_error:
            print(f"FireCrawl Exception: {crawl_error}")
            
            # 回退到简单爬取
            try:
                response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                content = response.text[:1000] + "..." if len(response.text) > 1000 else response.text
                
                return jsonify({
                    "success": True,
                    "title": f"来自 {url} 的内容",
                    "content": f"FireCrawl服务暂时不可用，使用简单爬取获得内容：\n\n{content}",
                    "url": url,
                    "method": "简单爬虫（回退）",
                    "scraped_at": datetime.now().isoformat(),
                    "fallback": True,
                    "error": str(crawl_error)
                })
            except Exception as simple_error:
                return jsonify({
                    "success": False,
                    "error": str(simple_error),
                    "message": f"无法访问URL: {url}"
                }), 500
        
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
                "actions": ["store_article", "search_articles", "test_connection"],
                "stored_articles": len(articles_db)
            })
        
        if action == 'test_connection':
            return jsonify({
                "success": True,
                "message": "数据库连接正常",
                "storage_type": "memory_cache",
                "stored_articles": len(articles_db),
                "timestamp": datetime.now().isoformat()
            })
        
        elif action == 'store_article':
            article = {
                "id": len(articles_db) + 1,
                "title": data.get('title', ''),
                "content": data.get('content', ''),
                "url": data.get('url', ''),
                "stored_at": datetime.now().isoformat()
            }
            articles_db.append(article)
            
            return jsonify({
                "success": True,
                "message": "文章已存储到内存数据库",
                "storage_type": "memory_cache",
                "data": article
            })
        
        elif action == 'search_articles':
            query = data.get('query', '').lower()
            
            if not query:
                # 返回所有文章
                return jsonify({
                    "success": True,
                    "articles": articles_db,
                    "count": len(articles_db),
                    "storage_type": "memory_cache"
                })
            
            # 搜索匹配的文章
            matching_articles = []
            for article in articles_db:
                if (query in article.get('title', '').lower() or 
                    query in article.get('content', '').lower()):
                    matching_articles.append(article)
            
            return jsonify({
                "success": True,
                "articles": matching_articles,
                "count": len(matching_articles),
                "storage_type": "memory_cache",
                "query": query
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

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ask_api": "running",
            "crawl_api": "running", 
            "database_api": "running"
        },
        "config": {
            "firecrawl_configured": bool(FIRECRAWL_API_KEY),
            "ai_configured": bool(AI_API_KEY),
            "stored_articles": len(articles_db)
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Starting AI Knowledge Agent on port {port}")
    print("📡 Available endpoints:")
    print("  - GET  / (API info)")
    print("  - POST /api/ask (AI问答)")
    print("  - POST /api/crawl (网页爬取)") 
    print("  - POST /api/database (数据库操作)")
    print("  - GET  /health (健康检查)")
    print(f"🔑 FireCrawl API: {'✅ 已配置' if FIRECRAWL_API_KEY else '❌ 未配置'}")
    print(f"🤖 AI API: {'✅ 已配置' if AI_API_KEY else '❌ 未配置'}")
    
    app.run(host='0.0.0.0', port=port, debug=True)
