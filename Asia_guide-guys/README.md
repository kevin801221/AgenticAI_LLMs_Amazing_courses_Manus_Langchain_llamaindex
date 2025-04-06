# 亞洲觀光機器人前端

基於 NextJS 的亞洲觀光機器人前端界面。這是一個基於大型語言模型技術的智慧旅遊助手，專為亞洲地區旅遊設計。

## 功能特點

- 基於對話的智能旅遊助手
- 個性化旅遊建議和行程規劃
- 即時旅遊資訊（天氣、交通等）
- 地圖視圖與景點展示
- 用戶偏好設置
- 多語言支持

## 技術棧

- Next.js
- React
- Material-UI
- i18next (多語言支持)

## 快速開始

### 安裝依賴

```bash
npm install
# 或
yarn install
```

### 配置環境變量

創建 `.env.local` 文件在項目根目錄，並添加以下環境變量：

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws
```

### 啟動開發服務器

```bash
npm run dev
# 或
yarn dev
```

訪問 [http://localhost:3000](http://localhost:3000) 查看應用。

## 項目結構

```
.
├── components/          # React 組件
│   ├── ChatBox.js       # 聊天界面組件
│   ├── MapView.js       # 地圖視圖組件
│   ├── Sidebar.js       # 側邊欄組件
│   └── UserPreferences.js # 用戶偏好設置組件
├── pages/               # Next.js 頁面
│   ├── _app.js          # 應用入口
│   └── index.js         # 主頁
├── public/              # 靜態資源
│   └── locales/         # 翻譯文件
│       ├── en/          # 英文翻譯
│       └── zh-TW/       # 繁體中文翻譯
├── styles/              # CSS 樣式
│   ├── ChatBox.module.css
│   ├── Home.module.css
│   ├── MapView.module.css
│   └── Sidebar.module.css
├── next-i18next.config.js # i18next 配置
└── package.json         # 項目依賴和腳本
```

## 功能實現說明

### 聊天功能

聊天界面使用 React Hooks 管理消息狀態，模擬與後端 API 的交互。在實際生產環境中，需要將模擬函數替換為真實的 API 調用。

### 地圖功能

地圖視圖組件目前使用占位符，需要集成 Google Maps API 或其他地圖服務來顯示真實的地圖。模擬的地點數據和天氣數據在實際生產環境中應來自後端 API。

### 多語言支持

使用 next-i18next 實現多語言支持，翻譯文件位於 `public/locales` 目錄下。目前支持繁體中文、簡體中文、英文、日文和韓文。

### 用戶偏好設置

用戶偏好設置使用 localStorage 持久化，包括語言、位置、興趣和預算等設置。這些設置將影響聊天回復和提供的信息。

## 部署

### 構建生產版本

```bash
npm run build
# 或
yarn build
```

### 啟動生產服務器

```bash
npm start
# 或
yarn start
```

## 下一步開發計劃

1. 整合真實的 API 服務
2. 集成 Google Maps 或其他地圖服務
3. 增加真實的圖像識別功能
4. 完善多 Agent 系統架構
5. 優化移動設備體驗
6. 實現社交分享功能

## 貢獻

歡迎提交 Pull Request 或 Issue。

## 許可證

MIT