#!/bin/bash

echo "🧪 测试AI知识代理API..."
echo ""

API_URL="http://localhost:3000"

# 测试健康检查
echo "1️⃣ 测试健康检查..."
curl -s "$API_URL/health" | python3 -m json.tool
echo ""

# 测试Ask API
echo "2️⃣ 测试AI问答..."
curl -s -X POST "$API_URL/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是机器学习？"}' | python3 -m json.tool
echo ""

# 测试Crawl API
echo "3️⃣ 测试网页爬取..."
curl -s -X POST "$API_URL/api/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://httpbin.org/json"}' | python3 -m json.tool
echo ""

# 测试Database API
echo "4️⃣ 测试数据库连接..."
curl -s -X POST "$API_URL/api/database" \
  -H "Content-Type: application/json" \
  -d '{"action":"test_connection"}' | python3 -m json.tool
echo ""

# 测试存储文章
echo "5️⃣ 测试存储文章..."
curl -s -X POST "$API_URL/api/database" \
  -H "Content-Type: application/json" \
  -d '{"action":"store_article","title":"测试文章","content":"这是一篇测试文章的内容","url":"https://example.com/test"}' | python3 -m json.tool
echo ""

# 测试搜索文章
echo "6️⃣ 测试搜索文章..."
curl -s -X POST "$API_URL/api/database" \
  -H "Content-Type: application/json" \
  -d '{"action":"search_articles","query":"测试"}' | python3 -m json.tool
echo ""

echo "✅ API测试完成！"
