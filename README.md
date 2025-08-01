# AI Knowledge Agent

基于网页爬取的智能问答助手 - 完全免费方案

## 🚀 快速部署

### 方案1: GitHub Pages + Vercel (推荐)

1. **GitHub Pages 部署前端**
   ```bash
   # 1. 创建GitHub仓库
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yy2025-program/public-knowledge-agent.git
   git push -u origin main
   
   # 2. 在GitHub仓库设置中启用Pages
   # Settings -> Pages -> Source: Deploy from a branch -> main
   ```

2. **Vercel 部署API**
   - 访问 [vercel.com](https://vercel.com)
   - 连接GitHub账号
   - 导入这个仓库
   - 自动部署API端点

### 方案2: 完全静态部署 (GitHub Pages)

如果不需要实时爬取，可以只使用GitHub Pages：

1. 将 `index.html` 中的API调用改为本地数据
2. 预先爬取数据存储为JSON文件
3. 纯前端实现，完全免费

## 🛠️ 技术栈

- **前端**: 纯HTML/CSS/JavaScript
- **后端**: Python + Vercel Serverless
- **数据库**: JSON文件 / SQLite
- **爬虫**: requests + BeautifulSoup
- **部署**: GitHub Pages + Vercel (免费)

## 📁 项目结构

```
ai-knowledge-agent/
├── index.html          # 主页面
├── api/               # Vercel API函数
│   ├── ask.py         # 问答接口
│   ├── crawl.py       # 爬虫接口
├── vercel.json        # Vercel配置
├── requirements.txt   # Python依赖
└── README.md         # 说明文档
```

## 🔧 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/yy2025-program/public-knowledge-agent.git
cd public-knowledge-agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 本地测试API
python -m http.server 8000

# 4. 访问 http://localhost:8000
```

## 🌟 功能特性

- ✅ 完全免费部署
- ✅ 响应式设计
- ✅ 实时问答
- ✅ 网页爬取
- ✅ 智能分类
- ✅ 简洁界面

## 🔄 升级计划

1. **集成FireCrawl** - 更强大的爬虫能力
2. **添加数据库** - Supabase免费层
3. **AI模型集成** - Hugging Face免费API
4. **定时任务** - GitHub Actions
5. **搜索功能** - 全文搜索

## 📝 使用说明

1. 访问部署的网站
2. 在输入框中输入问题
3. 系统会基于爬取的知识库回答
4. 支持中文问答

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
# Updated Fri Aug  1 16:40:43 CST 2025
