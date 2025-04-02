// mycology-researcher-api.js - 與 GPT Researcher 後端 API 集成

class MycologyResearcherAPI {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.socket = null;
        this.callbacks = {
            onLogs: null,
            onProgress: null,
            onReportComplete: null,
            onResearchComplete: null,
            onError: null,
            onLanggraphUpdate: null
        };
    }

    // 設置回調函數
    setCallbacks(callbacks) {
        this.callbacks = { ...this.callbacks, ...callbacks };
    }

    // 連接 WebSocket
    connectWebSocket() {
        return new Promise((resolve, reject) => {
            try {
                this.socket = new WebSocket(`ws://${this.baseUrl.replace(/^https?:\/\//, '')}/ws`);
                
                this.socket.onopen = () => {
                    console.log('WebSocket 連接已建立');
                    resolve(this.socket);
                };
                
                this.socket.onmessage = (event) => {
                    this._handleSocketMessage(event);
                };
                
                this.socket.onerror = (error) => {
                    console.error('WebSocket 錯誤:', error);
                    if (this.callbacks.onError) {
                        this.callbacks.onError(error);
                    }
                    reject(error);
                };
                
                this.socket.onclose = () => {
                    console.log('WebSocket 連接已關閉');
                };
            } catch (error) {
                console.error('連接 WebSocket 時出錯:', error);
                reject(error);
            }
        });
    }

    // 處理 WebSocket 消息
    _handleSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
                case 'logs':
                    if (this.callbacks.onLogs) {
                        this.callbacks.onLogs(data.content, data.output);
                    }
                    break;
                    
                case 'research_progress':
                    if (this.callbacks.onProgress) {
                        this.callbacks.onProgress(data.content, data.output);
                    }
                    break;
                    
                case 'path':
                    if (this.callbacks.onReportComplete) {
                        this.callbacks.onReportComplete(data.output);
                    }
                    break;
                    
                case 'langgraph_update':
                    if (this.callbacks.onLanggraphUpdate) {
                        this.callbacks.onLanggraphUpdate(data.content);
                    }
                    break;
                    
                case 'pong':
                    // 心跳檢測響應，不需要額外處理
                    break;
                    
                default:
                    console.log('收到未處理的消息類型:', data.type, data);
            }
        } catch (error) {
            console.error('解析 WebSocket 消息時出錯:', error, event.data);
        }
    }

    // 啟動研究
    async startResearch(researchParams) {
        const {
            query,
            report_type = 'research_report',
            tone = 'objective',
            data_sources = ['pubmed', 'arxiv', 'web'],
            filters = ['mycology'],
            additional_params = {}
        } = researchParams;
        
        // 增強領域特定參數
        const mycologyEnhancedParams = {
            ...additional_params,
            headers: {
                ...(additional_params.headers || {}),
                mycology_specific: true,
                prioritize_recent: true
            }
        };
        
        // 為黴菌研究定制查詢
        let enhancedQuery = query;
        if (filters.includes('mycology') && !query.toLowerCase().includes('fungi') && 
            !query.toLowerCase().includes('mushroom') && !query.toLowerCase().includes('mold') &&
            !query.toLowerCase().includes('mycology')) {
            enhancedQuery = `${query} (fungi OR mycology)`;
        }
        
        // 預處理源域
        let source_urls = [];
        const document_urls = [];
        let query_domains = [];
        
        // 處理數據源
        const reportSource = data_sources.includes('local') ? 'hybrid' : 'web';
        
        // 基於過濾器添加科學網站域名
        if (filters.includes('mycology')) {
            query_domains.push('ncbi.nlm.nih.gov', 'mycobank.org', 'mycology.net');
        }
        if (filters.includes('microbiology')) {
            query_domains.push('microbiologyresearch.org', 'asm.org');
        }
        if (filters.includes('medical')) {
            query_domains.push('cdc.gov', 'who.int', 'nih.gov');
        }
        
        // 確保 WebSocket 連接已建立
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            await this.connectWebSocket();
        }
        
        // 發送研究請求
        const startCommand = {
            task: enhancedQuery,
            report_type: report_type,
            report_source: reportSource,
            source_urls: source_urls,
            document_urls: document_urls,
            tone: tone,
            query_domains: query_domains,
            headers: mycologyEnhancedParams.headers
        };
        
        this.socket.send(`start${JSON.stringify(startCommand)}`);
        
        // 啟動心跳檢測
        this._startHeartbeat();
        
        return true;
    }
    
    // 發送聊天消息
    sendChatMessage(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(`chat${JSON.stringify({ message })}`);
            return true;
        }
        return false;
    }
    
    // 上傳文件
    async uploadFile(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${this.baseUrl}/upload/`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`上傳失敗: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('上傳文件時出錯:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
            throw error;
        }
    }
    
    // 獲取已上傳文件列表
    async getUploadedFiles() {
        try {
            const response = await fetch(`${this.baseUrl}/files/`);
            
            if (!response.ok) {
                throw new Error(`獲取文件列表失敗: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('獲取文件列表時出錯:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
            throw error;
        }
    }
    
    // 刪除上傳的文件
    async deleteFile(filename) {
        try {
            const response = await fetch(`${this.baseUrl}/files/${filename}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`刪除文件失敗: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('刪除文件時出錯:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
            throw error;
        }
    }
    
    // 心跳檢測
    _startHeartbeat() {
        // 每 30 秒發送一次心跳檢測
        this.heartbeatInterval = setInterval(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send('ping');
            }
        }, 30000);
    }
    
    // 停止心跳檢測
    _stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
    
    // 關閉連接
    disconnect() {
        this._stopHeartbeat();
        
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
}

// 加強的、專注於真菌學的查詢生成器，優化關鍵字以改進搜索結果
class MycologyQueryEnhancer {
    constructor() {
        // 真菌學常用關鍵詞
        this.mycologyKeywords = {
            general: ['fungus', 'fungi', 'mycology', 'mold', 'yeast', 'mushroom', 'mycobiome'],
            taxonomy: ['Ascomycota', 'Basidiomycota', 'Zygomycota', 'Chytridiomycota', 'hyphae', 'mycelium', 'spore'],
            medical: ['pathogenic fungi', 'mycosis', 'antifungal', 'fungal infection', 'aspergillosis', 'candidiasis'],
            agricultural: ['plant pathogen', 'mycorrhiza', 'biological control', 'crop disease', 'phytopathology'],
            biochemical: ['secondary metabolite', 'mycotoxin', 'enzyme', 'fermentation', 'antibiotic']
        };
    }
    
    // 優化查詢
    enhanceQuery(originalQuery, categories = ['general']) {
        let enhancedQuery = originalQuery;
        
        // 檢查查詢是否已包含真菌學術語
        const hasMycoTerms = Object.values(this.mycologyKeywords)
            .flat()
            .some(term => originalQuery.toLowerCase().includes(term.toLowerCase()));
            
        if (!hasMycoTerms) {
            const selectedKeywords = categories
                .filter(cat => this.mycologyKeywords[cat])
                .flatMap(cat => this.mycologyKeywords[cat])
                .slice(0, 3); // 只選擇最多 3 個關鍵詞
                
            if (selectedKeywords.length > 0) {
                const keywordsPart = selectedKeywords.join(' OR ');
                enhancedQuery = `${originalQuery} (${keywordsPart})`;
            }
        }
        
        return enhancedQuery;
    }
    
    // 建議相關查詢
    suggestRelatedQueries(originalQuery, mainCategory) {
        const relatedQueries = [];
        
        // 根據主類別推薦相關查詢
        if (mainCategory && this.mycologyKeywords[mainCategory]) {
            const keywords = this.mycologyKeywords[mainCategory].slice(0, 3);
            keywords.forEach(keyword => {
                relatedQueries.push(`${originalQuery} ${keyword}`);
            });
        }
        
        // 添加一些通用的查詢修飾詞
        const modifiers = [
            'latest research',
            'mechanism',
            'applications',
            'review'
        ];
        
        modifiers.forEach(modifier => {
            relatedQueries.push(`${originalQuery} ${modifier}`);
        });
        
        return relatedQueries.slice(0, 5); // 返回最多 5 個相關查詢
    }
}

// 導出模塊
export { MycologyResearcherAPI, MycologyQueryEnhancer };