"""
啟動網頁介面的快速腳本
"""
import os
import subprocess
import sys
from core.config import initialize, validate_api_keys

def main():
    """主函數"""
    print("="*60)
    print("智能會議記錄助手 - 網頁介面啟動器")
    print("="*60)
    
    # 初始化配置
    print("正在檢查設定...")
    try:
        validate_api_keys()
    except ValueError as e:
        print(f"錯誤: {e}")
        print("\n請在 .env 檔案中設定所需的 API 金鑰")
        print("範例:")
        print("DEEPGRAM_API_KEY=your_deepgram_api_key")
        print("OPENAI_API_KEY=your_openai_api_key")
        sys.exit(1)
    
    # 初始化應用
    if not initialize():
        print("應用初始化失敗，請檢查錯誤訊息")
        sys.exit(1)
    
    print("設定檢查完成!")
    print("正在啟動網頁介面...")
    
    # 啟動 Streamlit 應用
    subprocess.run(["streamlit", "run", "streamlit_app.py"])

if __name__ == "__main__":
    main()