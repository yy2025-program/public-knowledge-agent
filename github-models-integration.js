// GitHub Models API 集成
class GitHubModelsAI {
    constructor() {
        this.baseURL = 'https://models.inference.ai.azure.com';
        this.apiKey = localStorage.getItem('github_models_token') || '';
        this.availableModels = {
            'gpt-4o': 'GPT-4o (OpenAI)',
            'gpt-4o-mini': 'GPT-4o Mini (OpenAI)',
            'claude-3-5-sonnet': 'Claude 3.5 Sonnet (Anthropic)',
            'llama-3.1-405b-instruct': 'Llama 3.1 405B (Meta)',
            'llama-3.1-70b-instruct': 'Llama 3.1 70B (Meta)',
            'phi-3.5-mini-instruct': 'Phi-3.5 Mini (Microsoft)'
        };
        this.currentModel = localStorage.getItem('github_models_current') || 'gpt-4o-mini';
    }

    // 设置GitHub Personal Access Token
    setApiKey(token) {
        this.apiKey = token;
        localStorage.setItem('github_models_token', token);
    }

    // 设置当前使用的模型
    setModel(modelId) {
        this.currentModel = modelId;
        localStorage.setItem('github_models_current', modelId);
    }

    // 调用GitHub Models API
    async callModel(messages, model = null) {
        const modelId = model || this.currentModel;
        
        const payload = {
            messages: messages,
            max_tokens: 1000,
            temperature: 0.7,
            top_p: 0.9,
            stream: false
        };

        try {
            const response = await fetch(`${this.baseURL}/${modelId}/chat/completions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`GitHub Models API error: ${response.status} - ${errorData.error?.message || 'Unknown error'}`);
            }

            const data = await response.json();
            return data.choices[0].message.content;
        } catch (error) {
            console.error('GitHub Models API call failed:', error);
            throw error;
        }
    }

    // 智能问答增强
    async enhancedQA(question, crawledContent = []) {
        // 构建上下文
        let contextContent = '';
        if (crawledContent.length > 0) {
            contextContent = crawledContent.map(item => 
                `**${item.title}**\n${item.content.substring(0, 1500)}...`
            ).join('\n\n---\n\n');
        }

        // 构建消息数组
        const messages = [
            {
                role: "system",
                content: `You are an AI assistant specialized in Amazon logistics and seller operations. You help sellers with:

- Seller Central operations and navigation
- FBA (Fulfillment by Amazon) processes
- Inventory management and planning  
- Shipping and fulfillment options
- Amazon policies and compliance
- Supply chain optimization
- Performance metrics and reporting

Guidelines:
- Provide accurate, actionable advice based on current Amazon policies
- If you're not certain about specific policy details, recommend checking Seller Central or contacting Amazon support
- Focus on practical solutions that help sellers succeed
- Use clear, professional language
- If the provided context doesn't contain enough information, clearly state what's missing

Always prioritize accuracy over completeness - it's better to admit uncertainty than provide incorrect information that could harm a seller's business.`
            },
            {
                role: "user", 
                content: contextContent ? 
                    `Context from seller resources:\n\n${contextContent}\n\n---\n\nQuestion: ${question}` :
                    `Question: ${question}`
            }
        ];

        try {
            const response = await this.callModel(messages);
            return response;
        } catch (error) {
            console.error('GitHub Models enhanced QA failed:', error);
            throw new Error(`AI服务暂时不可用: ${error.message}`);
        }
    }

    // 测试API连接
    async testConnection() {
        try {
            const testMessages = [
                {
                    role: "user",
                    content: "Please respond with exactly: 'GitHub Models API connection successful'"
                }
            ];
            
            const response = await this.callModel(testMessages);
            return response.includes('successful');
        } catch (error) {
            console.error('GitHub Models connection test failed:', error);
            return false;
        }
    }

    // 获取可用模型列表
    getAvailableModels() {
        return this.availableModels;
    }

    // 获取当前模型信息
    getCurrentModelInfo() {
        return {
            id: this.currentModel,
            name: this.availableModels[this.currentModel] || this.currentModel
        };
    }
}

// 导出实例
window.GitHubModelsAI = GitHubModelsAI;
