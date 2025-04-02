import os
import openai
from dotenv import load_dotenv
import argparse

# 加載環境變量
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def text_to_speech(text, output_file, voice="alloy"):
    """將文本轉換為語音並保存為MP3文件"""
    try:
        print(f"正在將文本轉換為語音...")
        
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # 保存音頻文件
        with open(output_file, "wb") as file:
            file.write(response.content)
        
        print(f"語音文件已保存至 {output_file}")
        return True
    except Exception as e:
        print(f"轉換語音時出錯: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="將科技股市報告轉換為語音")
    parser.add_argument("--voice", default="alloy", help="語音類型 (alloy, echo, fable, onyx, nova, shimmer)")
    args = parser.parse_args()
    
    # 設置文件路徑
    input_file = "D:/Github_items/LLMs_Amazing_courses_Langchain_LlamaIndex/gpt-researcher-clean/audio_outputs/task_1741934154_幫我寫一個全球科技股市報告書_chinese.txt"
    output_file = "D:/Github_items/LLMs_Amazing_courses_Langchain_LlamaIndex/gpt-researcher-clean/audio_outputs/task_1741934154_幫我寫一個全球科技股市報告書_chinese.mp3"
    
    # 確保音頻輸出目錄存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 讀取文本文件
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            text = file.read()
        
        # 將文本分成較小的部分（每部分約2000個字符）
        max_length = 2000
        parts = []
        
        # 按段落分割文本
        paragraphs = text.split("\n\n")
        current_part = ""
        
        for paragraph in paragraphs:
            # 如果添加這個段落會超過最大長度，則保存當前部分並開始新部分
            if len(current_part) + len(paragraph) > max_length and current_part:
                parts.append(current_part)
                current_part = paragraph
            else:
                if current_part:
                    current_part += "\n\n" + paragraph
                else:
                    current_part = paragraph
        
        # 添加最後一部分
        if current_part:
            parts.append(current_part)
        
        print(f"文本已分成 {len(parts)} 個部分進行處理")
        
        # 為每個部分生成臨時音頻文件
        temp_files = []
        for i, part in enumerate(parts):
            temp_file = f"D:/Github_items/LLMs_Amazing_courses_Langchain_LlamaIndex/gpt-researcher-clean/audio_outputs/temp_part_{i}.mp3"
            success = text_to_speech(part, temp_file, args.voice)
            if success:
                temp_files.append(temp_file)
            else:
                print(f"處理第 {i+1} 部分時出錯，跳過")
        
        # 如果只有一個部分，直接重命名
        if len(temp_files) == 1:
            os.rename(temp_files[0], output_file)
            print(f"已生成語音文件: {output_file}")
        elif len(temp_files) > 1:
            # 如果有多個部分，需要合併音頻文件
            # 這裡需要使用 FFmpeg，但為了簡單起見，我們先使用第一個部分
            os.rename(temp_files[0], output_file)
            print(f"已生成第一部分語音文件: {output_file}")
            print(f"注意: 由於文本較長，只生成了第一部分的語音。要生成完整語音，請使用 FFmpeg 合併所有部分。")
        else:
            print("沒有生成任何語音文件")
            
    except Exception as e:
        print(f"處理文件時出錯: {e}")

if __name__ == "__main__":
    main()
