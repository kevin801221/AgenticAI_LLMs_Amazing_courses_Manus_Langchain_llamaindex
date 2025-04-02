import os
import sys
import PyPDF2
from pathlib import Path
import openai
from dotenv import load_dotenv
import time

# 加載環境變數
load_dotenv()

# 設置 OpenAI API 金鑰
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("錯誤：未找到 OPENAI_API_KEY 環境變數")
    sys.exit(1)

openai.api_key = openai_api_key

def extract_text_from_pdf(pdf_path):
    """從 PDF 文件中提取文本"""
    try:
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            
            print(f"PDF 文件共有 {num_pages} 頁")
            
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
                print(f"已處理第 {page_num + 1}/{num_pages} 頁")
        
        return text
    except Exception as e:
        print(f"提取 PDF 文本時出錯：{e}")
        import traceback
        traceback.print_exc()
        return None

def extract_text_from_txt(txt_path):
    """從 TXT 文件中提取文本"""
    try:
        with open(txt_path, "r", encoding="utf-8") as file:
            text = file.read()
        return text
    except Exception as e:
        print(f"提取 TXT 文本時出錯：{e}")
        import traceback
        traceback.print_exc()
        return None

def create_one_minute_summary(text):
    """創建一分鐘的精彩摘要，重點介紹公司和CEO"""
    try:
        print("正在創建一分鐘的精彩摘要...")
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個專業的內容編輯，需要創建一個非常精彩、引人入勝的一分鐘摘要。這個摘要將被轉換成語音，應該重點介紹公司和CEO的成就與願景。使用生動的語言和引人注目的事實，確保聽眾會被吸引。"},
                {"role": "user", "content": f"請根據以下內容，創建一個約250字的精彩摘要，重點介紹YCM公司和其CEO陳冠潔。這個摘要將被轉換成大約一分鐘的語音內容，所以必須簡潔有力，同時非常引人入勝：\n\n{text}"}
            ]
        )
        
        summary = response.choices[0].message.content
        print("一分鐘摘要創建完成！")
        return summary
    
    except Exception as e:
        print(f"創建摘要時出錯：{e}")
        import traceback
        traceback.print_exc()
        return None

def text_to_speech(text, output_file, voice="alloy"):
    """將文本轉換為語音"""
    try:
        print("正在將文本轉換為語音...")
        
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        response.stream_to_file(str(output_file))
        print("語音轉換完成！")
        return output_file
    
    except Exception as e:
        print(f"轉換文本為語音時出錯：{e}")
        import traceback
        traceback.print_exc()
        return None

def txt_to_chinese_speech(txt_file, voice="alloy"):
    """將 TXT 文件轉換為精彩的一分鐘語音摘要"""
    # 提取 TXT 文本
    print(f"正在從 TXT 文件提取文本：{txt_file}")
    text = extract_text_from_txt(txt_file)
    
    if not text:
        print("無法從 TXT 文件中提取文本")
        return None
    
    print(f"成功提取文本，共 {len(text)} 字符")
    
    # 創建一分鐘的精彩摘要
    summary = create_one_minute_summary(text)
    
    if not summary:
        print("無法創建摘要")
        return None
    
    print("\n創建的一分鐘摘要：")
    print("-" * 50)
    print(summary)
    print("-" * 50)
    
    # 創建輸出目錄
    audio_dir = Path("audio_outputs")
    audio_dir.mkdir(exist_ok=True)
    
    # 設置輸出文件路徑
    output_file = audio_dir / f"{Path(txt_file).stem}_one_minute_summary.mp3"
    
    # 轉換為語音
    audio_file = text_to_speech(summary, output_file, voice)
    
    if audio_file:
        print(f"一分鐘摘要語音文件已生成: {audio_file}")
        print(f"您可以在 {os.path.abspath(audio_file)} 找到語音文件")
        
        # 保存摘要文本
        text_file = audio_dir / f"{Path(txt_file).stem}_one_minute_summary.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"摘要文本已保存到: {text_file}")
    else:
        print("語音文件生成失敗")
    
    return audio_file

def main():
    if len(sys.argv) < 2:
        print("用法: python txt_to_one_minute_speech.py <TXT文件路徑> [--voice 語音類型]")
        sys.exit(1)
    
    txt_file = sys.argv[1]
    voice = "alloy"  # 默認語音類型
    
    # 解析命令行參數
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == "--voice" and i + 1 < len(sys.argv):
            voice = sys.argv[i + 1]
    
    print(f"開始處理 TXT 文件：{txt_file}")
    print(f"使用語音類型：{voice}")
    
    txt_to_chinese_speech(txt_file, voice)

if __name__ == "__main__":
    main()