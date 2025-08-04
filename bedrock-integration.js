// Amazon Bedrock API 集成
class BedrockAI {
    constructor(region = 'us-east-1') {
        this.region = region;
        this.endpoint = `https://bedrock-runtime.${region}.amazonaws.com`;
        this.apiKey = localStorage.getItem('bedrock_api_key') || '';
    }

    // 设置API密钥
    setApiKey(apiKey) {
        this.apiKey = apiKey;
        localStorage.setItem('bedrock_api_key', apiKey);
    }

    // 调用Claude模型
    async callClaude(prompt, context = '') {
        const payload = {
            modelId: 'anthropic.claude-3-sonnet-20240229-v1:0',
            contentType: 'application/json',
            accept: 'application/json',
            body: JSON.stringify({
                anthropic_version: "bedrock-2023-05-31",
                max_tokens: 1000,
                messages: [
                    {
                        role: "user",
                        content: `Context: ${context}\n\nQuestion: ${prompt}\n\nPlease provide a helpful answer focused on logistics and seller operations.`
                    }
                ]
            })
        };

        try {
            const response = await fetch(`${this.endpoint}/model/anthropic.claude-3-sonnet-20240229-v1:0/invoke`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`,
                    'X-Amzn-Bedrock-Accept': 'application/json',
                    'X-Amzn-Bedrock-Content-Type': 'application/json'
                },
                body: payload.body
            });

            if (!response.ok) {
                throw new Error(`Bedrock API error: ${response.status}`);
            }

            const data = await response.json();
            return data.content[0].text;
        } catch (error) {
            console.error('Bedrock API call failed:', error);
            throw error;
        }
    }

    // 调用Llama模型
    async callLlama(prompt, context = '') {
        const payload = {
            prompt: `Context: ${context}\n\nQuestion: ${prompt}\n\nAnswer:`,
            max_gen_len: 1000,
            temperature: 0.7,
            top_p: 0.9
        };

        try {
            const response = await fetch(`${this.endpoint}/model/meta.llama2-70b-chat-v1/invoke`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            return data.generation;
        } catch (error) {
            console.error('Llama API call failed:', error);
            throw error;
        }
    }

    // 智能问答增强
    async enhancedQA(question, crawledContent = []) {
        // 构建上下文
        let context = '';
        if (crawledContent.length > 0) {
            context = crawledContent.map(item => 
                `Title: ${item.title}\nContent: ${item.content.substring(0, 1000)}...`
            ).join('\n\n');
        }

        // 构建专业提示词
        const enhancedPrompt = `
You are an AI assistant specialized in Amazon logistics and seller operations. 
Please provide accurate, helpful answers based on the context provided.

If the context doesn't contain enough information, clearly state what information is missing and suggest where the user might find it.

Focus on:
- Seller Central operations
- FBA and logistics
- Inventory management
- Shipping and fulfillment
- Policy compliance

Question: ${question}
        `;

        try {
            // 优先使用Claude（更适合对话）
            return await this.callClaude(enhancedPrompt, context);
        } catch (error) {
            console.warn('Claude failed, trying Llama:', error);
            try {
                return await this.callLlama(enhancedPrompt, context);
            } catch (llamaError) {
                console.error('All AI models failed:', llamaError);
                throw new Error('AI服务暂时不可用，请稍后重试');
            }
        }
    }

    // 测试API连接
    async testConnection() {
        try {
            const testResponse = await this.callClaude('Hello, please respond with "API connection successful"');
            return testResponse.includes('successful');
        } catch (error) {
            return false;
        }
    }
}

// 导出实例
window.BedrockAI = BedrockAI;
