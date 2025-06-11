# 🔎 Web Search Agent with LangChain and Llama 3.3

使用 LangChain 和 Llama 3.3 70B 構建的智能網路搜索代理，能夠從 ArXiv 和 Wikipedia 等外部知識源檢索資訊並提供準確的回答。

## 🌟 專案特色

- **多模態搜索**: 整合 ArXiv 學術論文和 Wikipedia 百科全書搜索
- **實時對話**: 基於 Streamlit 的互動式聊天介面
- **智能推理**: 使用 Llama 3.3 70B 模型進行自然語言理解和生成
- **模組化設計**: 易於擴展和維護的架構
- **錯誤處理**: 優雅的錯誤處理機制

## 🏗️ 系統架構

```mermaid
graph TB
    subgraph "前端介面"
        UI[Streamlit 使用者介面]
        CHAT[聊天介面]
        INPUT[使用者輸入]
    end
    
    subgraph "核心處理"
        AGENT[搜索代理]
        LLM[Llama 3.3 70B]
        PROMPT[提示模板]
    end
    
    subgraph "外部工具"
        ARXIV[ArXiv API]
        WIKI[Wikipedia API]
        SEARCH[搜索引擎]
    end
    
    subgraph "資料處理"
        PARSER[結果解析器]
        MEMORY[會話記憶]
        STATE[狀態管理]
    end
    
    UI --> CHAT
    CHAT --> INPUT
    INPUT --> AGENT
    AGENT --> LLM
    AGENT --> ARXIV
    AGENT --> WIKI
    AGENT --> SEARCH
    LLM --> PROMPT
    ARXIV --> PARSER
    WIKI --> PARSER
    PARSER --> MEMORY
    MEMORY --> STATE
    STATE --> UI
```

## 🔄 工作流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant UI as Streamlit 介面
    participant Agent as 搜索代理
    participant LLM as Llama 3.3
    participant ArXiv as ArXiv API
    participant Wiki as Wikipedia API
    
    User->>UI: 輸入查詢問題
    UI->>Agent: 傳送問題
    Agent->>LLM: 分析問題
    LLM->>Agent: 決定搜索策略
    
    par 並行搜索
        Agent->>ArXiv: 搜索學術論文
        Agent->>Wiki: 搜索百科資料
    end
    
    ArXiv->>Agent: 返回搜索結果
    Wiki->>Agent: 返回搜索結果
    Agent->>LLM: 整合搜索結果
    LLM->>Agent: 生成回答
    Agent->>UI: 返回最終回答
    UI->>User: 顯示回答
```

## 📦 安裝與設置

### 環境需求

- Python 3.8+
- 穩定的網路連接
- Groq API 金鑰

### 安裝步驟

```mermaid
flowchart TD
    A[建立虛擬環境] --> B[啟動環境]
    B --> C[安裝依賴套件]
    C --> D[配置 API 金鑰]
    D --> E[執行應用程式]
    
    A1[python -m venv env] --> A
    B1[source env/bin/activate] --> B
    C1[pip install -r requirements.txt] --> C
    D1[設置 .env 文件] --> D
    E1[streamlit run app.py] --> E
```

#### 1. 建立虛擬環境

```bash
# 建立虛擬環境
python -m venv env

# Windows 啟動
.\env\Scripts\activate

# macOS/Linux 啟動
source env/bin/activate
```

#### 2. 安裝依賴套件

```bash
# 方法一：直接從本專案安裝
pip install -r requirements.txt

# 方法二：從原作者 GitHub 安裝
pip install -r https://raw.githubusercontent.com/Gouravlohar/Search-Agent/refs/heads/master/requirements.txt

# 方法三：手動安裝核心套件
pip install streamlit langchain langchain-community langchain-groq python-dotenv arxiv wikipedia requests
```

#### 3. 配置 API 金鑰

建立 `.env` 文件並添加您的 Groq API 金鑰：

```env
GROQ_API_KEY="your_api_key_here"
```

> 📝 **取得 API 金鑰**: 訪問 [Groq 官網](https://groq.com) 註冊並獲取免費的 API 金鑰

## 🚀 使用方法

### 啟動應用程式

```bash
streamlit run app.py
```

### 功能展示

```mermaid
graph LR
    subgraph "使用者互動流程"
        A[開啟應用程式] --> B[輸入問題]
        B --> C[選擇搜索來源]
        C --> D[獲得回答]
        D --> E[繼續對話]
        E --> B
    end
    
    subgraph "系統處理流程"
        F[接收問題] --> G[LLM 分析]
        G --> H[工具選擇]
        H --> I[執行搜索]
        I --> J[結果整合]
        J --> K[生成回答]
    end
```

## 🛠️ 技術架構詳解

### 核心組件

```mermaid
classDiagram
    class WebSearchAgent {
        +ChatGroq llm
        +List~Tool~ tools
        +AgentExecutor executor
        +initialize()
        +run(query)
        +handle_errors()
    }
    
    class ArxivWrapper {
        +top_k_results: int
        +doc_content_chars_max: int
        +search(query)
        +format_results()
    }
    
    class WikipediaWrapper {
        +top_k_results: int
        +doc_content_chars_max: int
        +search(query)
        +format_results()
    }
    
    class StreamlitInterface {
        +session_state: Dict
        +chat_interface()
        +handle_input()
        +display_messages()
    }
    
    WebSearchAgent --> ArxivWrapper
    WebSearchAgent --> WikipediaWrapper
    StreamlitInterface --> WebSearchAgent
```

### 資料流程

```mermaid
flowchart LR
    subgraph "輸入處理"
        A[使用者問題] --> B[預處理]
        B --> C[問題分析]
    end
    
    subgraph "搜索執行"
        C --> D{選擇工具}
        D -->|學術資料| E[ArXiv 搜索]
        D -->|百科資料| F[Wikipedia 搜索]
        D -->|綜合搜索| G[多源搜索]
    end
    
    subgraph "結果處理"
        E --> H[結果整合]
        F --> H
        G --> H
        H --> I[LLM 生成回答]
        I --> J[格式化輸出]
    end
    
    J --> K[返回使用者]
```

## 📚 API 參考

### 主要類別

#### `WebSearchAgent`
負責協調整個搜索流程的核心類別。

```python
class WebSearchAgent:
    def __init__(self, api_key: str, model_name: str):
        self.llm = ChatGroq(groq_api_key=api_key, model_name=model_name)
        self.tools = [ArxivQueryRun(), WikipediaQueryRun()]
    
    def search(self, query: str) -> str:
        """執行搜索並返回結果"""
        pass
```

#### `ToolWrapper`
封裝外部 API 調用的基礎類別。

```python
class ToolWrapper:
    def __init__(self, top_k_results: int = 1, doc_content_chars_max: int = 200):
        self.top_k_results = top_k_results
        self.doc_content_chars_max = doc_content_chars_max
```

## 🎯 使用案例

### 學術研究

```mermaid
journey
    title 學術研究工作流程
    section 問題定義
      提出研究問題: 5: 研究者
      關鍵詞提取: 4: 系統
    section 資料搜索
      ArXiv 搜索: 5: 系統
      結果篩選: 4: 系統
    section 資訊整合
      摘要生成: 5: LLM
      相關性分析: 4: LLM
    section 結果呈現
      格式化回答: 5: 系統
      後續建議: 3: 系統
```

### 知識查詢

```mermaid
graph TD
    A[一般知識問題] --> B{問題類型}
    B -->|概念解釋| C[Wikipedia 搜索]
    B -->|技術細節| D[ArXiv 搜索]
    B -->|綜合資訊| E[多源搜索]
    
    C --> F[百科資訊]
    D --> G[學術資料]
    E --> H[綜合資料]
    
    F --> I[LLM 整合]
    G --> I
    H --> I
    
    I --> J[生成回答]
```

## ⚙️ 配置選項

### 模型參數

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `model_name` | "llama-3.3-70b-versatile" | 使用的 LLM 模型 |
| `streaming` | `True` | 是否啟用串流回應 |
| `top_k_results` | `1` | 每個工具返回的結果數量 |
| `doc_content_chars_max` | `200` | 文檔內容最大字符數 |

### 環境變數

```env
# 必需
GROQ_API_KEY=your_groq_api_key

# 可選
MODEL_NAME=llama-3.3-70b-versatile
MAX_TOKENS=4096
TEMPERATURE=0.7
```

## 🔧 自定義和擴展

### 添加新的搜索工具

```mermaid
flowchart TB
    A[建立新工具類別] --> B[實現 BaseTool 介面]
    B --> C[配置 API 包裝器]
    C --> D[註冊到工具列表]
    D --> E[測試整合]
    
    subgraph "實現細節"
        F[定義搜索方法]
        G[處理 API 回應]
        H[格式化結果]
        I[錯誤處理]
    end
    
    B --> F
    F --> G
    G --> H
    H --> I
```

### 範例：添加 Google Scholar 工具

```python
from langchain.tools import BaseTool

class GoogleScholarTool(BaseTool):
    name = "google_scholar"
    description = "搜索 Google Scholar 學術文獻"
    
    def _run(self, query: str) -> str:
        # 實現 Google Scholar API 調用
        pass
```

## 🐛 故障排除

### 常見問題

```mermaid
flowchart TD
    A[遇到錯誤] --> B{錯誤類型}
    
    B -->|API 錯誤| C[檢查 API 金鑰]
    B -->|網路錯誤| D[檢查網路連接]
    B -->|模組錯誤| E[檢查依賴安裝]
    B -->|搜索錯誤| F[檢查查詢格式]
    
    C --> G[重新配置金鑰]
    D --> H[檢查防火牆設置]
    E --> I[重新安裝套件]
    F --> J[調整查詢參數]
    
    G --> K[重啟應用程式]
    H --> K
    I --> K
    J --> K
```

### 除錯步驟

1. **檢查日誌**: 查看詳細的錯誤資訊
2. **驗證配置**: 確認所有配置參數正確
3. **測試連接**: 驗證外部 API 的連接狀態
4. **更新依賴**: 確保所有套件為最新版本

## 📈 效能優化

### 快取策略

```mermaid
graph LR
    A[使用者查詢] --> B{查詢快取}
    B -->|命中| C[返回快取結果]
    B -->|未命中| D[執行搜索]
    D --> E[儲存到快取]
    E --> F[返回結果]
    
    subgraph "快取層級"
        G[記憶體快取]
        H[磁碟快取]
        I[資料庫快取]
    end
```

### 效能監控

- **回應時間**: 監控平均回應時間
- **API 調用次數**: 追蹤外部 API 使用量
- **錯誤率**: 監控系統錯誤發生率
- **使用者滿意度**: 收集使用者回饋

## 🤝 貢獻指南

### 開發流程

```mermaid
gitgraph
    commit id: "初始化專案"
    branch develop
    checkout develop
    commit id: "新功能開發"
    commit id: "測試完成"
    checkout main
    merge develop
    commit id: "發布版本"
```

### 提交規範

- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文檔更新
- `style`: 代碼格式調整
- `refactor`: 代碼重構
- `test`: 測試相關
- `chore`: 構建過程或輔助工具的變動

## 📄 授權條款

本專案採用 MIT 授權條款。詳細資訊請參閱 [LICENSE](LICENSE) 文件。

## 📞 聯絡方式

- **作者**: Gourav Lohar
- **問題回報**: [GitHub Issues](https://github.com/Gouravlohar/Search-Agent/issues)
- **功能建議**: [GitHub Discussions](https://github.com/Gouravlohar/Search-Agent/discussions)

## 🙏 致謝

感謝以下開源專案和服務：

- [LangChain](https://langchain.com/) - 強大的 LLM 應用框架
- [Streamlit](https://streamlit.io/) - 簡潔的 Web 應用框架  
- [Groq](https://groq.com/) - 高效能的 AI 推理平台
- [ArXiv](https://arxiv.org/) - 開放存取的學術論文庫
- [Wikipedia](https://wikipedia.org/) - 自由的百科全書

---

⭐ 如果這個專案對您有幫助，請給我們一個星星！