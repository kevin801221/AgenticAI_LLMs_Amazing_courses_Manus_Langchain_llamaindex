"""
配置模組 - 集中管理所有設置和API金鑰
"""
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# API金鑰
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 應用設置
DEFAULT_MEETING_TITLE = "未命名會議"
DEFAULT_MODEL = "gpt-4o"
EXPORT_DIR = "./exports"
DB_DIRECTORY = "./conversation_db"

# 錄音設置
RECORDING_SETTINGS = {
    "language": "zh-TW",  # 轉錄語言
    "model": "nova-2",    # Deepgram模型
    "diarize": True,      # 默認開啟說話者識別
    "endpointing": 380,   # 默認自動斷句時間（毫秒）
    "sample_rate": 16000  # 音訊取樣率
}

# Web界面設置
WEB_UI_SETTINGS = {
    "page_title": "會議記錄助手",
    "page_icon": "🎙️",
    "layout": "wide",
    "theme_color": "#4682B4",
    "sidebar_width": 300
}

# 檢查必要的API金鑰
def validate_api_keys():
    """驗證必要的API金鑰
    
    Raises:
        ValueError: 如果缺少必要的API金鑰
    """
    missing_keys = []
    if not DEEPGRAM_API_KEY:
        missing_keys.append("DEEPGRAM_API_KEY")
    if not OPENAI_API_KEY:
        missing_keys.append("OPENAI_API_KEY")
    
    if missing_keys:
        raise ValueError(f"缺少以下環境變數: {', '.join(missing_keys)}")

# 確保導出目錄存在
def ensure_export_dir():
    """確保導出目錄存在"""
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

# 確保資料庫目錄存在
def ensure_db_dir():
    """確保資料庫目錄存在"""
    if not os.path.exists(DB_DIRECTORY):
        os.makedirs(DB_DIRECTORY)

# 初始化檢查
def initialize():
    """初始化應用設置
    
    Returns:
        bool: 是否初始化成功
    """
    try:
        validate_api_keys()
        ensure_export_dir()
        ensure_db_dir()
        return True
    except Exception as e:
        print(f"初始化失敗: {e}")
        return False