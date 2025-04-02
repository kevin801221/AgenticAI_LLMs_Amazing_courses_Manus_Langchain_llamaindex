# Python Meeting Summarizer

一個純Python實現的會議摘要工具，可以將會議錄音轉換為文字並生成詳細摘要。

## 功能

- 使用 OpenAI Whisper 將會議錄音轉換為文字
- 使用 OpenAI GPT 模型生成詳細的會議摘要
- 提供友好的 Gradio 網頁界面
- 支持多種音頻格式
- 可下載完整會議記錄

## 安裝

1. 克隆此存儲庫
2. 安裝依賴項：

```bash
pip install -r requirements.txt
```

3. 創建 `.env` 文件並添加您的 OpenAI API 密鑰：

```
OPENAI_API_KEY=your_openai_api_key_here
```

## 使用方法

1. 運行應用程序：

```bash
python main.py
```

2. 在瀏覽器中打開顯示的 URL（通常是 http://127.0.0.1:7860）
3. 上傳會議錄音文件
4. 可選擇性地提供會議上下文信息
5. 選擇要使用的 Whisper 模型和 OpenAI 模型
6. 點擊「處理會議錄音」按鈕
7. 查看並下載會議摘要和完整記錄

## 模型選擇

### Whisper 模型
- **tiny**: 最快但準確度較低
- **base**: 良好的速度和準確度平衡（推薦用於大多數情況）
- **small**: 比 base 更準確，但處理時間更長
- **medium**: 高準確度，但處理時間較長
- **large**: 最高準確度，但處理時間最長

### OpenAI 模型
- **gpt-3.5-turbo**: 較快且成本較低
- **gpt-4o-mini**: 良好的性能和成本平衡（推薦用於大多數情況）
- **gpt-4o**: 最高質量的摘要，但成本較高

## 注意事項

- 需要有效的 OpenAI API 密鑰
- 處理時間取決於音頻長度和選擇的模型
- 較大的 Whisper 模型提供更準確的轉錄，但處理時間更長
- GPT-4o 模型提供最詳細的摘要，但使用成本較高
