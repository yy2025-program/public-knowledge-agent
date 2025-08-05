// 智能回答生成器
class SmartAnswerGenerator {
    constructor() {
        this.githubAI = new GitHubModelsAI();
        this.contextWindow = 4000; // 上下文窗口大小
        this.confidenceThreshold = 0.7;
    }

    // 主要问答入口
    async generateAnswer(question, options = {}) {
        try {
            // 1. 预处理问题
            const processedQuestion = this.preprocessQuestion(question);
            
            // 2. 检索相关内容
            const relevantContent = this.retrieveRelevantContent(processedQuestion);
            
            // 3. 评估内容质量
            const qualityContent = this.filterHighQualityContent(relevantContent);
            
            // 4. 构建上下文
            const context = this.buildContext(qualityContent, processedQuestion);
            
            // 5. 生成AI回答
            const aiAnswer = await this.generateAIAnswer(processedQuestion, context);
            
            // 6. 后处理和验证
            const finalAnswer = this.postProcessAnswer(aiAnswer, qualityContent);
            
            return {
                answer: finalAnswer,
                sources: qualityContent.map(c => ({ title: c.title, url: c.url })),
                confidence: this.calculateConfidence(qualityContent, aiAnswer),
                category: this.categorizeQuestion(processedQuestion)
            };
            
        } catch (error) {
            console.error('Smart answer generation failed:', error);
            return this.getFallbackAnswer(question);
        }
    }

    // 问题预处理
    preprocessQuestion(question) {
        return {
            original: question,
            cleaned: question.trim().replace(/[？?]+$/, ''),
            keywords: this.extractQuestionKeywords(question),
            intent: this.detectQuestionIntent(question),
            language: this.detectLanguage(question)
        };
    }

    // 检测问题意图
    detectQuestionIntent(question) {
        const intents = {
            'how_to': ['如何', '怎么', '怎样', 'how to', 'how do'],
            'what_is': ['什么是', '什么叫', 'what is', 'what are'],
            'why': ['为什么', '为何', 'why'],
            'when': ['什么时候', '何时', 'when'],
            'where': ['哪里', '在哪', 'where'],
            'comparison': ['区别', '对比', '比较', 'vs', 'versus', 'difference'],
            'troubleshooting': ['问题', '错误', '失败', 'error', 'problem', 'issue']
        };

        const questionLower = question.toLowerCase();
        
        for (const [intent, patterns] of Object.entries(intents)) {
            if (patterns.some(pattern => questionLower.includes(pattern))) {
                return intent;
            }
        }
        
        return 'general';
    }

    // 智能内容检索
    retrieveRelevantContent(processedQuestion) {
        const knowledgeBase = JSON.parse(localStorage.getItem('crawled_knowledge_base') || '[]');
        
        if (knowledgeBase.length === 0) {
            return [];
        }

        // 多维度相关性评分
        const scoredContent = knowledgeBase.map(item => {
            let score = 0;
            
            // 关键词匹配
            const keywordScore = this.calculateKeywordRelevance(
                processedQuestion.keywords, 
                item.keywords || []
            );
            score += keywordScore * 0.4;
            
            // 标题相关性
            const titleScore = this.calculateTextSimilarity(
                processedQuestion.cleaned, 
                item.title || ''
            );
            score += titleScore * 0.3;
            
            // 内容相关性
            const contentScore = this.calculateTextSimilarity(
                processedQuestion.cleaned, 
                item.content || ''
            );
            score += contentScore * 0.2;
            
            // 质量权重
            score += (item.quality || 0.5) * 0.1;
            
            return { ...item, relevanceScore: score };
        });

        // 排序并返回最相关的内容
        return scoredContent
            .sort((a, b) => b.relevanceScore - a.relevanceScore)
            .slice(0, 5)
            .filter(item => item.relevanceScore > 0.1);
    }

    // 关键词相关性计算
    calculateKeywordRelevance(questionKeywords, contentKeywords) {
        if (!questionKeywords.length || !contentKeywords.length) return 0;
        
        const matches = questionKeywords.filter(qk => 
            contentKeywords.some(ck => 
                ck.includes(qk) || qk.includes(ck) || 
                this.calculateLevenshteinDistance(qk, ck) <= 2
            )
        );
        
        return matches.length / questionKeywords.length;
    }

    // 文本相似度计算
    calculateTextSimilarity(text1, text2) {
        const words1 = text1.toLowerCase().split(/\s+/);
        const words2 = text2.toLowerCase().split(/\s+/);
        
        const intersection = words1.filter(word => words2.includes(word));
        const union = [...new Set([...words1, ...words2])];
        
        return intersection.length / union.length;
    }

    // 构建AI上下文
    buildContext(relevantContent, processedQuestion) {
        if (relevantContent.length === 0) {
            return null;
        }

        let context = "基于以下Amazon物流和卖家运营相关资料：\n\n";
        let currentLength = context.length;
        
        for (const item of relevantContent) {
            const itemText = `**${item.title}**\n${item.summary || item.content}\n来源：${item.url}\n\n`;
            
            if (currentLength + itemText.length > this.contextWindow) {
                break;
            }
            
            context += itemText;
            currentLength += itemText.length;
        }
        
        return context;
    }

    // 生成AI回答
    async generateAIAnswer(processedQuestion, context) {
        const prompt = this.buildPrompt(processedQuestion, context);
        
        try {
            return await this.githubAI.enhancedQA(processedQuestion.original, 
                context ? [{ title: "相关资料", content: context }] : []
            );
        } catch (error) {
            console.error('AI answer generation failed:', error);
            throw error;
        }
    }

    // 构建提示词
    buildPrompt(processedQuestion, context) {
        let prompt = `作为Amazon物流和卖家运营专家，请回答以下问题：\n\n`;
        prompt += `问题：${processedQuestion.original}\n`;
        prompt += `问题类型：${processedQuestion.intent}\n\n`;
        
        if (context) {
            prompt += `参考资料：\n${context}\n\n`;
        }
        
        prompt += `请提供：\n`;
        prompt += `1. 准确、实用的回答\n`;
        prompt += `2. 具体的操作步骤（如适用）\n`;
        prompt += `3. 相关注意事项\n`;
        prompt += `4. 如果信息不足，请明确说明\n\n`;
        
        return prompt;
    }

    // 回答后处理
    postProcessAnswer(aiAnswer, sources) {
        let processedAnswer = aiAnswer;
        
        // 添加来源引用
        if (sources.length > 0) {
            processedAnswer += `\n\n**参考来源：**\n`;
            sources.forEach((source, index) => {
                processedAnswer += `${index + 1}. [${source.title}](${source.url})\n`;
            });
        }
        
        // 添加免责声明
        processedAnswer += `\n\n*注：以上信息基于已爬取的资料生成，建议核实最新的Amazon政策和规定。*`;
        
        return processedAnswer;
    }

    // 计算回答置信度
    calculateConfidence(sources, answer) {
        let confidence = 0.3; // 基础置信度
        
        // 来源质量
        if (sources.length > 0) {
            const avgQuality = sources.reduce((sum, s) => sum + (s.quality || 0.5), 0) / sources.length;
            confidence += avgQuality * 0.4;
        }
        
        // 回答长度
        if (answer.length > 200) confidence += 0.2;
        if (answer.length > 500) confidence += 0.1;
        
        return Math.min(confidence, 1.0);
    }

    // 获取后备回答
    getFallbackAnswer(question) {
        return {
            answer: `抱歉，我暂时无法为您的问题"${question}"提供准确回答。建议您：\n\n1. 检查问题是否与Amazon物流、FBA或卖家运营相关\n2. 尝试使用更具体的关键词重新提问\n3. 访问Amazon Seller Central获取最新信息\n\n如果问题持续存在，请考虑联系Amazon客服获取官方支持。`,
            sources: [],
            confidence: 0.1,
            category: 'fallback'
        };
    }

    // 工具函数
    extractQuestionKeywords(question) {
        const stopWords = ['是', '什么', '的', '了', '在', '有', '和', '与', '或', '但', '如何', '怎么', '为什么', '哪里', '什么时候', '谁', '吗', '呢', 'the', 'is', 'are', 'what', 'how', 'why', 'where', 'when'];
        
        return question.toLowerCase()
            .replace(/[^\w\s]/g, ' ')
            .split(/\s+/)
            .filter(word => word.length > 2 && !stopWords.includes(word))
            .slice(0, 10);
    }

    detectLanguage(text) {
        const chineseChars = text.match(/[\u4e00-\u9fff]/g);
        return chineseChars && chineseChars.length > text.length * 0.3 ? 'zh' : 'en';
    }

    categorizeQuestion(processedQuestion) {
        const categories = {
            'FBA': ['fba', 'fulfillment', '配送', '仓储'],
            'Shipping': ['shipping', 'delivery', '物流', '运输'],
            'Account': ['account', 'seller central', '账户', '卖家中心'],
            'Policy': ['policy', 'terms', '政策', '规定'],
            'Marketing': ['advertising', 'ppc', '广告', '推广']
        };

        const questionText = processedQuestion.cleaned.toLowerCase();
        
        for (const [category, keywords] of Object.entries(categories)) {
            if (keywords.some(keyword => questionText.includes(keyword))) {
                return category;
            }
        }
        
        return 'General';
    }

    calculateLevenshteinDistance(str1, str2) {
        const matrix = [];
        
        for (let i = 0; i <= str2.length; i++) {
            matrix[i] = [i];
        }
        
        for (let j = 0; j <= str1.length; j++) {
            matrix[0][j] = j;
        }
        
        for (let i = 1; i <= str2.length; i++) {
            for (let j = 1; j <= str1.length; j++) {
                if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j - 1] + 1,
                        matrix[i][j - 1] + 1,
                        matrix[i - 1][j] + 1
                    );
                }
            }
        }
        
        return matrix[str2.length][str1.length];
    }
}

// 导出
window.SmartAnswerGenerator = SmartAnswerGenerator;
