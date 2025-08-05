// 增强型爬虫管理器
class EnhancedCrawler {
    constructor() {
        this.crawlQueue = [];
        this.crawledData = JSON.parse(localStorage.getItem('crawled_knowledge_base') || '[]');
        this.isProcessing = false;
    }

    // 批量爬取URL列表
    async batchCrawl(urls, options = {}) {
        const results = [];
        const maxConcurrent = options.maxConcurrent || 3;
        const delay = options.delay || 1000;

        for (let i = 0; i < urls.length; i += maxConcurrent) {
            const batch = urls.slice(i, i + maxConcurrent);
            const batchPromises = batch.map(url => this.crawlSingleUrl(url));
            
            try {
                const batchResults = await Promise.allSettled(batchPromises);
                results.push(...batchResults);
                
                // 添加延迟避免被封
                if (i + maxConcurrent < urls.length) {
                    await this.sleep(delay);
                }
            } catch (error) {
                console.error('Batch crawl error:', error);
            }
        }

        return results;
    }

    // 智能内容提取
    async crawlSingleUrl(url) {
        try {
            const response = await fetch('/api/crawl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, enhanced: true })
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            
            // 增强内容处理
            const enhancedData = {
                ...data,
                keywords: this.extractKeywords(data.content),
                summary: this.generateSummary(data.content),
                category: this.categorizeContent(data.content),
                crawledAt: new Date().toISOString(),
                quality: this.assessContentQuality(data.content)
            };

            // 只保存高质量内容
            if (enhancedData.quality > 0.6) {
                this.saveToKnowledgeBase(enhancedData);
            }

            return enhancedData;
        } catch (error) {
            console.error(`Failed to crawl ${url}:`, error);
            return { url, error: error.message, success: false };
        }
    }

    // 内容质量评估
    assessContentQuality(content) {
        if (!content || content.length < 100) return 0.1;
        
        let score = 0.5;
        
        // 长度评分
        if (content.length > 500) score += 0.2;
        if (content.length > 1000) score += 0.1;
        
        // 结构评分
        if (content.includes('\n')) score += 0.1;
        if (content.match(/[.!?]/g)?.length > 3) score += 0.1;
        
        // 关键词密度
        const keywords = ['amazon', 'logistics', 'shipping', 'fba', 'seller'];
        const keywordCount = keywords.filter(kw => 
            content.toLowerCase().includes(kw)
        ).length;
        score += keywordCount * 0.05;
        
        return Math.min(score, 1.0);
    }

    // 智能分类
    categorizeContent(content) {
        const categories = {
            'FBA': ['fba', 'fulfillment by amazon', 'warehouse', 'inventory'],
            'Shipping': ['shipping', 'delivery', 'logistics', 'transport'],
            'Seller Central': ['seller central', 'account', 'dashboard', 'reports'],
            'Policies': ['policy', 'terms', 'conditions', 'compliance'],
            'Marketing': ['advertising', 'ppc', 'sponsored', 'promotion']
        };

        const contentLower = content.toLowerCase();
        
        for (const [category, keywords] of Object.entries(categories)) {
            if (keywords.some(keyword => contentLower.includes(keyword))) {
                return category;
            }
        }
        
        return 'General';
    }

    // 生成摘要
    generateSummary(content, maxLength = 200) {
        if (content.length <= maxLength) return content;
        
        // 找到最佳截断点（句子结尾）
        const truncated = content.substring(0, maxLength);
        const lastSentence = truncated.lastIndexOf('。');
        const lastPeriod = truncated.lastIndexOf('.');
        
        const cutPoint = Math.max(lastSentence, lastPeriod);
        
        if (cutPoint > maxLength * 0.7) {
            return truncated.substring(0, cutPoint + 1);
        }
        
        return truncated + '...';
    }

    // 保存到知识库
    saveToKnowledgeBase(data) {
        // 去重检查
        const exists = this.crawledData.find(item => item.url === data.url);
        if (exists) {
            // 更新现有数据
            Object.assign(exists, data);
        } else {
            this.crawledData.push(data);
        }
        
        // 限制数据库大小
        if (this.crawledData.length > 1000) {
            this.crawledData = this.crawledData
                .sort((a, b) => b.quality - a.quality)
                .slice(0, 800);
        }
        
        localStorage.setItem('crawled_knowledge_base', JSON.stringify(this.crawledData));
    }

    // 工具函数
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    extractKeywords(content) {
        const words = content.toLowerCase()
            .replace(/[^\w\s]/g, ' ')
            .split(/\s+/)
            .filter(word => word.length > 3);
        
        const frequency = {};
        words.forEach(word => {
            frequency[word] = (frequency[word] || 0) + 1;
        });
        
        return Object.entries(frequency)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 10)
            .map(([word]) => word);
    }
}

// 导出
window.EnhancedCrawler = EnhancedCrawler;
