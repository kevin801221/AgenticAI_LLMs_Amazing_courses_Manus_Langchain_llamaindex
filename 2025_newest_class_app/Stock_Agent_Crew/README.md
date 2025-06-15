# 股票分析智能代理團隊 (Stock Agent Crew)

這個專案使用 CrewAI 框架建立了一個智能代理團隊，專門用於分析公司股票並提供投資建議。該系統利用多個專業代理協同工作，從網路上收集最新的公司資訊，進行分析，並提供專業的投資建議。

## 目錄

- [專案概述](#專案概述)
- [系統架構](#系統架構)
- [檔案說明](#檔案說明)
- [安裝指南](#安裝指南)
- [使用方法](#使用方法)
- [環境變數設定](#環境變數設定)
- [常見問題](#常見問題)
- [進階功能](#進階功能)

## 專案概述

股票分析智能代理團隊是一個基於 CrewAI 和 LangChain 的應用程式，旨在自動化股票分析過程。系統包含兩個專業代理：
1. **市場研究分析師** - 負責收集和整理公司的市場和財務資訊
2. **特許財務分析師 (CFA)** - 負責分析收集到的資訊並提供投資建議

這個專案使用 Ollama 作為本地 LLM 提供者，並使用 Google Serper API 進行網路搜索，以獲取最新的公司資訊。

## 系統架構

系統的工作流程如下：
1. 用戶輸入想要分析的公司名稱
2. 市場研究分析師使用搜索工具收集該公司的最新資訊
3. 特許財務分析師分析這些資訊，並提供投資建議
4. 系統輸出完整的分析報告

## 檔案說明

### 核心檔案

- **`main.py`**: 主程式入口點，包含 `FinancialCrew` 類別，負責初始化和運行整個代理團隊。
  - 創建代理和任務
  - 設定工作流程
  - 處理用戶輸入和輸出結果

- **`agents.py`**: 定義了系統中使用的智能代理。
  - `market_research_analyst()`: 市場研究分析師，負責搜索和整理公司資訊
  - `cfa()`: 特許財務分析師，負責分析資訊並提供投資建議

- **`tasks.py`**: 定義了代理需要執行的任務。
  - `research()`: 搜索並總結公司的最新動態和新聞
  - `analysis()`: 分析收集到的資訊並提供投資建議

- **`tools/search.py`**: 提供網路搜索功能的工具類別。
  - `searchInfo()`: 使用 Google Serper API 搜索指定內容的相關資訊
  - `search()`: 實際執行搜索並格式化結果的方法

### 配置檔案

- **`.env`**: 環境變數配置檔案，用於存儲 API 金鑰。
  - `SERPER_API_KEY`: Google Serper API 金鑰
  - `OPENAI_API_KEY`: OpenAI API 金鑰（如果使用 OpenAI 模型）

- **`pyproject.toml`**: Poetry 專案配置檔案，定義了專案的依賴關係。

- **`poetry.lock`**: Poetry 鎖定檔案，確保依賴版本一致。

- **`requirements.txt`**: 簡化的依賴列表，用於非 Poetry 安裝方式。

## 安裝指南

### 前置條件

- Python 3.11 或更高版本
- [Ollama](https://ollama.ai/) 已安裝並運行（用於本地 LLM）
- Google Serper API 金鑰（用於網路搜索）

### 使用 Poetry 安裝（推薦）

1. 安裝 Poetry（如果尚未安裝）:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. 克隆專案並安裝依賴:
   ```bash
   git clone <專案URL>
   cd Stock_Agent_Crew
   poetry install
   ```

### 使用 pip 安裝

1. 克隆專案:
   ```bash
   git clone <專案URL>
   cd Stock_Agent_Crew
   ```

2. 創建並啟用虛擬環境:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # 在 Windows 上使用 .venv\Scripts\activate
   ```

3. 安裝依賴:
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 設定環境變數

1. 複製 `.env.example` 檔案（如果存在）或創建新的 `.env` 檔案:
   ```bash
   cp .env.example .env  # 如果存在
   # 或
   touch .env  # 創建新檔案
   ```

2. 在 `.env` 檔案中添加您的 API 金鑰:
   ```
   SERPER_API_KEY=your_serper_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here  # 如果使用 OpenAI 模型
   ```

### 啟動 Ollama

確保 Ollama 已經啟動並運行 llama3.1 模型:

```bash
ollama run llama3.1
```

### 運行程式

使用 Poetry:
```bash
poetry run python main.py
```

或直接使用 Python（在啟用虛擬環境後）:
```bash
python main.py
```

### 互動流程

1. 程式啟動後，會顯示歡迎訊息
2. 輸入您想要分析的公司名稱（例如：「台積電」、「Apple」、「Tesla」等）
3. 系統會開始收集和分析資訊，這可能需要幾分鐘時間
4. 最終會顯示完整的分析報告，包括公司概況和投資建議

## 環境變數設定

| 變數名 | 說明 | 必需 |
|--------|------|------|
| SERPER_API_KEY | Google Serper API 金鑰，用於網路搜索 | 是 |
| OPENAI_API_KEY | OpenAI API 金鑰，如果使用 OpenAI 模型則需要 | 否 |

## 常見問題

### 無法連接到 Ollama

確保 Ollama 已經安裝並正在運行。您可以通過以下命令檢查 Ollama 狀態:

```bash
ollama ps
```

如果 Ollama 未運行，請啟動它:

```bash
ollama serve
```

### 搜索功能無法使用

確保您已經設定了有效的 SERPER_API_KEY 環境變數。您可以在 [serper.dev](https://serper.dev/) 獲取 API 金鑰。

### 分析結果不夠詳細

可以嘗試修改 `agents.py` 中的代理設定，增加 `max_iter` 參數值，或調整代理的目標和背景故事，使其提供更詳細的分析。

## 進階功能

### 自定義 LLM 模型

您可以在 `main.py` 中修改 LLM 設定，使用不同的模型:

```python
llm = LLM(
    model="ollama/mistral:latest",  # 更改為其他模型
    base_url="http://localhost:11434",
)
```

### 添加更多代理

您可以在 `agents.py` 中添加更多專業代理，例如技術分析師、產業專家等，以提供更全面的分析。

### 擴展搜索工具

您可以在 `tools/search.py` 中添加更多搜索工具，例如專門用於搜索財務報表、技術指標等的工具。

---

由 Kevin 用 ❤️ 打造
