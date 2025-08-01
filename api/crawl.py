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
                url = data.get('url', '')
                use_firecrawl = data.get('use_firecrawl', False)
            else:
                url = ''
                use_firecrawl = False
            
            if not url:
                raise ValueError("URL不能为空")
            
            # 检查是否有FireCrawl API密钥
            firecrawl_api_key = os.environ.get('FIRECRAWL_API_KEY')
            
            if use_firecrawl and firecrawl_api_key:
                # 使用FireCrawl API
                result = self.crawl_with_firecrawl(url, firecrawl_api_key)
            else:
                # 使用简单爬虫
                result = self.crawl_simple(url)
            
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e),
                "message": "爬取失败，请检查URL是否正确"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def crawl_with_firecrawl(self, url, api_key):
        """使用FireCrawl API爬取"""
        try:
            # FireCrawl API调用
            firecrawl_url = "https://api.firecrawl.dev/v0/scrape"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            payload = {
                'url': url,
                'formats': ['markdown', 'html'],
                'includeTags': ['p', 'h1', 'h2', 'h3', 'article'],
                'excludeTags': ['nav', 'footer', 'aside'],
                'onlyMainContent': True
            }
            
            req = urllib.request.Request(
                firecrawl_url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            if result.get('success'):
                return {
                    "success": True,
                    "title": result.get('data', {}).get('metadata', {}).get('title', '无标题'),
                    "content": result.get('data', {}).get('markdown', ''),
                    "url": url,
                    "method": "FireCrawl",
                    "scraped_at": self.get_current_time()
                }
            else:
                raise Exception(f"FireCrawl API错误: {result.get('error', '未知错误')}")
                
        except Exception as e:
            # FireCrawl失败时降级到简单爬虫
            return self.crawl_simple(url, f"FireCrawl失败({str(e)})，使用简单爬虫")
    
    def crawl_simple(self, url, fallback_reason=""):
        """简单爬虫实现"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
            
            # 简单的HTML解析（提取文本）
            import re
            
            # 提取标题
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else "无标题"
            
            # 移除脚本和样式
            html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
            html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
            
            # 提取文本内容
            text_content = re.sub(r'<[^>]+>', ' ', html_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # 限制内容长度
            if len(text_content) > 3000:
                text_content = text_content[:3000] + "..."
            
            method_info = "简单爬虫"
            if fallback_reason:
                method_info += f" ({fallback_reason})"
            
            return {
                "success": True,
                "title": title,
                "content": text_content,
                "url": url,
                "method": method_info,
                "scraped_at": self.get_current_time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"简单爬虫也失败了: {str(e)}"
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
        # 处理GET请求（测试用）
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        firecrawl_available = bool(os.environ.get('FIRECRAWL_API_KEY'))
        
        response = {
            "message": "Enhanced Crawl API is running!",
            "features": {
                "firecrawl": firecrawl_available,
                "simple_crawler": True
            },
            "usage": "POST with {\"url\": \"https://example.com\", \"use_firecrawl\": true}",
            "status": "ok"
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
