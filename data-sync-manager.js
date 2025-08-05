// 数据同步管理器
class DataSyncManager {
    constructor() {
        this.syncInterval = 30 * 60 * 1000; // 30分钟
        this.maxCacheAge = 24 * 60 * 60 * 1000; // 24小时
        this.syncInProgress = false;
        this.lastSyncTime = localStorage.getItem('last_sync_time') || 0;
        
        this.initializeSync();
    }

    // 初始化同步
    initializeSync() {
        // 页面加载时检查是否需要同步
        this.checkAndSync();
        
        // 设置定时同步
        setInterval(() => {
            this.checkAndSync();
        }, this.syncInterval);
        
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.checkAndSync();
            }
        });
    }

    // 检查并同步数据
    async checkAndSync() {
        const now = Date.now();
        const timeSinceLastSync = now - parseInt(this.lastSyncTime);
        
        if (timeSinceLastSync > this.maxCacheAge && !this.syncInProgress) {
            await this.performSync();
        }
    }

    // 执行数据同步
    async performSync() {
        if (this.syncInProgress) return;
        
        this.syncInProgress = true;
        console.log('开始数据同步...');
        
        try {
            // 1. 同步知识库数据
            await this.syncKnowledgeBase();
            
            // 2. 清理过期缓存
            this.cleanExpiredCache();
            
            // 3. 优化数据结构
            this.optimizeDataStructure();
            
            // 4. 更新同步时间
            localStorage.setItem('last_sync_time', Date.now().toString());
            
            console.log('数据同步完成');
            this.notifyUI('sync_complete');
            
        } catch (error) {
            console.error('数据同步失败:', error);
            this.notifyUI('sync_error', error.message);
        } finally {
            this.syncInProgress = false;
        }
    }

    // 同步知识库数据
    async syncKnowledgeBase() {
        const knowledgeBase = JSON.parse(localStorage.getItem('crawled_knowledge_base') || '[]');
        const outdatedItems = knowledgeBase.filter(item => {
            const itemAge = Date.now() - new Date(item.crawledAt || 0).getTime();
            return itemAge > this.maxCacheAge;
        });

        if (outdatedItems.length > 0) {
            console.log(`发现 ${outdatedItems.length} 个过期项目，开始更新...`);
            
            const crawler = new EnhancedCrawler();
            const urls = outdatedItems.map(item => item.url);
            
            try {
                const results = await crawler.batchCrawl(urls, {
                    maxConcurrent: 2,
                    delay: 2000
                });
                
                console.log(`成功更新 ${results.filter(r => r.status === 'fulfilled').length} 个项目`);
            } catch (error) {
                console.error('批量更新失败:', error);
            }
        }
    }

    // 清理过期缓存
    cleanExpiredCache() {
        const cacheKeys = [
            'crawled_knowledge_base',
            'ai_response_cache',
            'search_cache'
        ];

        cacheKeys.forEach(key => {
            const data = JSON.parse(localStorage.getItem(key) || '[]');
            if (Array.isArray(data)) {
                const cleaned = data.filter(item => {
                    if (!item.timestamp) return true;
                    const age = Date.now() - item.timestamp;
                    return age < this.maxCacheAge;
                });
                
                if (cleaned.length !== data.length) {
                    localStorage.setItem(key, JSON.stringify(cleaned));
                    console.log(`清理了 ${data.length - cleaned.length} 个过期缓存项 (${key})`);
                }
            }
        });
    }

    // 优化数据结构
    optimizeDataStructure() {
        const knowledgeBase = JSON.parse(localStorage.getItem('crawled_knowledge_base') || '[]');
        
        if (knowledgeBase.length === 0) return;

        // 1. 去重
        const uniqueItems = this.removeDuplicates(knowledgeBase);
        
        // 2. 按质量排序
        const sortedItems = uniqueItems.sort((a, b) => (b.quality || 0) - (a.quality || 0));
        
        // 3. 限制数量
        const optimizedItems = sortedItems.slice(0, 800);
        
        // 4. 压缩内容
        const compressedItems = optimizedItems.map(item => ({
            ...item,
            content: this.compressContent(item.content),
            summary: item.summary || this.generateSummary(item.content)
        }));

        localStorage.setItem('crawled_knowledge_base', JSON.stringify(compressedItems));
        
        console.log(`数据优化完成: ${knowledgeBase.length} -> ${compressedItems.length} 项`);
    }

    // 去重
    removeDuplicates(items) {
        const seen = new Set();
        return items.filter(item => {
            const key = item.url || item.title;
            if (seen.has(key)) {
                return false;
            }
            seen.add(key);
            return true;
        });
    }

    // 压缩内容
    compressContent(content) {
        if (!content || content.length <= 2000) return content;
        
        // 保留重要段落
        const paragraphs = content.split('\n').filter(p => p.trim().length > 50);
        const important = paragraphs.slice(0, 3);
        
        return important.join('\n') + (paragraphs.length > 3 ? '\n...' : '');
    }

    // 生成摘要
    generateSummary(content, maxLength = 150) {
        if (!content || content.length <= maxLength) return content;
        
        const sentences = content.split(/[.!?。！？]/).filter(s => s.trim().length > 10);
        let summary = '';
        
        for (const sentence of sentences) {
            if (summary.length + sentence.length > maxLength) break;
            summary += sentence.trim() + '。';
        }
        
        return summary || content.substring(0, maxLength) + '...';
    }

    // 智能缓存管理
    async cacheResponse(key, data, ttl = this.maxCacheAge) {
        const cacheItem = {
            data,
            timestamp: Date.now(),
            ttl,
            key
        };

        const cache = JSON.parse(localStorage.getItem('ai_response_cache') || '[]');
        
        // 移除旧的相同key缓存
        const filtered = cache.filter(item => item.key !== key);
        
        // 添加新缓存
        filtered.push(cacheItem);
        
        // 限制缓存大小
        const limited = filtered.slice(-100);
        
        localStorage.setItem('ai_response_cache', JSON.stringify(limited));
    }

    // 获取缓存
    getCachedResponse(key) {
        const cache = JSON.parse(localStorage.getItem('ai_response_cache') || '[]');
        const item = cache.find(c => c.key === key);
        
        if (!item) return null;
        
        const age = Date.now() - item.timestamp;
        if (age > item.ttl) {
            // 缓存过期，异步清理
            this.removeCachedResponse(key);
            return null;
        }
        
        return item.data;
    }

    // 移除缓存
    removeCachedResponse(key) {
        const cache = JSON.parse(localStorage.getItem('ai_response_cache') || '[]');
        const filtered = cache.filter(item => item.key !== key);
        localStorage.setItem('ai_response_cache', JSON.stringify(filtered));
    }

    // 获取存储使用情况
    getStorageUsage() {
        let totalSize = 0;
        const breakdown = {};
        
        for (let key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
                const size = localStorage[key].length;
                totalSize += size;
                breakdown[key] = {
                    size,
                    sizeKB: Math.round(size / 1024 * 100) / 100
                };
            }
        }
        
        return {
            total: totalSize,
            totalMB: Math.round(totalSize / 1024 / 1024 * 100) / 100,
            breakdown,
            limit: 5 * 1024 * 1024, // 5MB 大概限制
            usage: totalSize / (5 * 1024 * 1024)
        };
    }

    // 清理存储空间
    cleanupStorage() {
        const usage = this.getStorageUsage();
        
        if (usage.usage > 0.8) { // 超过80%使用率
            console.log('存储空间不足，开始清理...');
            
            // 1. 清理AI响应缓存
            localStorage.removeItem('ai_response_cache');
            
            // 2. 压缩知识库
            const kb = JSON.parse(localStorage.getItem('crawled_knowledge_base') || '[]');
            const compressed = kb.slice(0, 500); // 只保留500个最好的
            localStorage.setItem('crawled_knowledge_base', JSON.stringify(compressed));
            
            // 3. 清理其他临时数据
            const keysToClean = Object.keys(localStorage).filter(key => 
                key.startsWith('temp_') || key.startsWith('cache_')
            );
            keysToClean.forEach(key => localStorage.removeItem(key));
            
            console.log('存储清理完成');
        }
    }

    // 通知UI
    notifyUI(event, data = null) {
        const customEvent = new CustomEvent('dataSync', {
            detail: { event, data, timestamp: Date.now() }
        });
        document.dispatchEvent(customEvent);
    }

    // 手动触发同步
    async forcSync() {
        await this.performSync();
    }

    // 获取同步状态
    getSyncStatus() {
        return {
            inProgress: this.syncInProgress,
            lastSync: new Date(parseInt(this.lastSyncTime)),
            nextSync: new Date(parseInt(this.lastSyncTime) + this.syncInterval),
            cacheAge: Date.now() - parseInt(this.lastSyncTime)
        };
    }
}

// 导出
window.DataSyncManager = DataSyncManager;
