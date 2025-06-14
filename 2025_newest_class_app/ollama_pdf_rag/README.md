# 🤖 使用 Ollama + LangChain 在本地與 PDF 對話

一個強大的本地 RAG（檢索增強生成）應用程式，讓你能夠使用 Ollama 和 LangChain 與 PDF 文件進行對話。本專案同時提供 Jupyter Notebook 供實驗用途，以及 Streamlit 網頁介面，方便進行互動。

## 專案結構
```
ollama_pdf_rag/
├── src/                      # Source code
│   ├── app/                  # Streamlit application
│   │   ├── components/       # UI components
│   │   │   ├── chat.py      # Chat interface
│   │   │   ├── pdf_viewer.py # PDF display
│   │   │   └── sidebar.py   # Sidebar controls
│   │   └── main.py          # Main app
│   └── core/                 # Core functionality
│       ├── document.py       # Document processing
│       ├── embeddings.py     # Vector embeddings
│       ├── llm.py           # LLM setup
│       └── rag.py           # RAG pipeline
├── data/                     # Data storage
│   ├── pdfs/                # PDF storage
│   │   └── sample/          # Sample PDFs
│   └── vectors/             # Vector DB storage
├── notebooks/               # Jupyter notebooks
│   └── experiments/         # Experimental notebooks
├── tests/                   # Unit tests
├── docs/                    # Documentation
└── run.py                   # Application runner
```

## ✨ 功能特色

- 🔒 完全本地處理 - 不會將數據傳輸到您的機器外部
- 📄 PDF 處理使用智能分塊技術
- 🧠 多次查詢檢索以更好地理解上下文
- 🎯 使用 LangChain 的進階 RAG 實現
- 🖥️ 乾淨的 Streamlit 使用者介面
- 📓 Jupyter Notebook 供實驗用途

## 🚀 開始使用

### 前置需求

1. **安裝 Ollama**
   - 訪問 [Ollama 官網](https://ollama.ai) 下載並安裝
   - 下載所需模型：
     ```bash
     ollama pull llama3.3  # 或您偏好的其他模型
     ollama pull nomic-embed-text
     ```

2. **複製儲存庫**
   ```bash
   git clone https://github.com/kevinluo/ollama_pdf_rag.git
   cd ollama_pdf_rag
   ```

3. **設置環境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows 系統: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

   主要依賴項及其版本：
   ```txt
   ollama==0.4.4
   streamlit==1.40.0
   pdfplumber==0.11.4
   langchain==0.1.20
   langchain-core==0.1.53
   langchain-ollama==0.0.2
   chromadb==0.4.22
   ```

### 🎮 運行應用程式

#### 選項 1: Streamlit 介面
```bash
python run.py
```
然後在瀏覽器中打開 `http://localhost:8501`

![Streamlit UI](st_app_ui.png)
*Streamlit 介面顯示 PDF 檢視器和聊天功能*

#### 選項 2: Jupyter Notebook
```bash
jupyter notebook
```
打開 `updated_rag_notebook.ipynb` 進行代碼實驗

## 💡 使用技巧

1. **上傳 PDF**: 使用 Streamlit 介面中的文件上傳器或嘗試範例 PDF
2. **選擇模型**: 從本地可用的 Ollama 模型中選擇
3. **提問**: 通過聊天介面開始與您的 PDF 對話
4. **調整顯示**: 使用縮放滑塊調整 PDF 可見度
5. **清理**: 切換文件時使用「刪除集合」按鈕

## 🤝 貢獻

歡迎：
- 為錯誤或建議開啟問題
- 提交拉取請求
- 在 YouTube 影片上留言提問
- 如果您覺得有用，請為儲存庫點星！

## ⚠️ 故障排除

- 確保 Ollama 在背景中運行
- 檢查是否已下載所需模型
- 驗證 Python 環境已啟動
- 如果使用 Ollama，請確保 Windows Subsystem for Linux (WSL2) 正確配置

### 常見錯誤

#### ONNX DLL 錯誤
如果遇到此錯誤：
```
DLL load failed while importing onnx_copy2py_export: a dynamic link Library (DLL) initialization routine failed.
```

嘗試這些解決方案：
1. 安裝 Microsoft Visual C++ Redistributable：
   - 從 [Microsoft 官方網站](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) 下載並安裝 x64 和 x86 版本
   - 安裝後重新啟動電腦

2. 如果錯誤仍然存在，嘗試手動安裝 ONNX Runtime：
   ```bash
   pip uninstall onnxruntime onnxruntime-gpu
   pip install onnxruntime
   ```

#### 僅 CPU 系統
如果您在僅 CPU 系統上運行：

1. 確保您有 ONNX Runtime 的 CPU 版本：
   ```bash
   pip uninstall onnxruntime-gpu  # 如已安裝，移除 GPU 版本
   pip install onnxruntime  # 安裝僅 CPU 版本
   ```

2. 您可能需要修改代碼中的分塊大小以防止記憶體問題：
   - 如果遇到記憶體問題，將 `chunk_size` 減少到 500-1000
   - 增加 `chunk_overlap` 以更好地保留上下文

注意：應用程式在僅 CPU 系統上運行會較慢，但仍能有效工作。

## 🧪 測試

### 運行測試
```bash
# 運行所有測試
python -m unittest discover tests

# 詳細運行測試
python -m unittest discover tests -v
```

### 預提交鉤子
本專案使用預提交鉤子確保代碼質量。設置方法：

```bash
pip install pre-commit
pre-commit install
```

這將：
- 在每次提交前運行測試
- 運行代碼風格檢查
- 確保代碼質量標準得到滿足

### 持續整合
本專案使用 GitHub Actions 進行持續整合。每次推送和拉取請求時：
- 在多個 Python 版本上運行測試（3.9、3.10、3.11）
- 安裝依賴項
- 下載 Ollama 模型
- 上傳測試結果作為成品

## 📝 授權

本專案為開源項目，根據 MIT 授權條款提供。

---

