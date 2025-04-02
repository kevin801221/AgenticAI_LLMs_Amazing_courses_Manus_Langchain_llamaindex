import os
import time
import datetime
import tempfile
import gradio as gr
import pyaudio
import wave
import threading
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
import openai
import json

# Check if OpenAI API key is set in environment
if "OPENAI_API_KEY" not in os.environ:
    try:
        # Try to load from .env file if exists
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

# Constants
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1024
RECORD_SECONDS = 5  # Default chunk size for recording

class MeetingRecorder:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.record_thread = None
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.meeting_title = "未命名會議"
        self.participants = []
        self.transcriptions = []
        self.summary = ""
        self.exports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
        os.makedirs(self.exports_dir, exist_ok=True)
    
    def start_recording(self):
        if self.recording:
            return "已經在錄音中..."
        
        self.recording = True
        self.audio_data = []
        
        # Start recording in a separate thread
        self.record_thread = threading.Thread(target=self._record_audio)
        self.record_thread.daemon = True
        self.record_thread.start()
        
        return "開始錄音..."
    
    def _record_audio(self):
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        while self.recording:
            data = self.stream.read(CHUNK, exception_on_overflow=False)
            self.audio_data.append(data)
        
        # Close the stream
        self.stream.stop_stream()
        self.stream.close()
    
    def stop_recording(self):
        if not self.recording:
            return "沒有正在進行的錄音。"
        
        self.recording = False
        if self.record_thread:
            self.record_thread.join(timeout=2.0)
        
        # Save the recorded audio to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name
            
            wf = wave.open(temp_filename, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b"".join(self.audio_data))
            wf.close()
        
        return temp_filename, "錄音已停止。正在處理音頻..."
    
    def transcribe_audio(self, audio_file):
        try:
            with open(audio_file, "rb") as file:
                transcription = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=file,
                    language="zh"  # Chinese language
                )
            
            text = transcription.text
            self.transcriptions.append({
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "text": text
            })
            
            return text
        except Exception as e:
            return f"轉錄失敗: {str(e)}"
    
    def generate_summary(self, transcription):
        if not transcription:
            return "沒有足夠的內容來生成摘要。"
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "你是一個專業的會議記錄助手。請根據提供的會議記錄生成一個簡潔但全面的摘要，包括主要討論點、決策和行動項目。使用繁體中文回答。"},
                    {"role": "user", "content": f"會議標題: {self.meeting_title}\n參與者: {', '.join(self.participants)}\n\n會議記錄:\n{transcription}"}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            summary = response.choices[0].message.content
            self.summary = summary
            return summary
        except Exception as e:
            return f"生成摘要失敗: {str(e)}"
    
    def export_meeting(self):
        if not self.transcriptions:
            return "沒有會議記錄可以導出。"
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.meeting_title.replace(' ', '_')}_{timestamp}.json"
        filepath = os.path.join(self.exports_dir, filename)
        
        data = {
            "meeting_title": self.meeting_title,
            "participants": self.participants,
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "transcriptions": self.transcriptions,
            "summary": self.summary
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return f"會議記錄已導出至 {filepath}"
    
    def set_meeting_info(self, title, participants_str):
        self.meeting_title = title if title else "未命名會議"
        self.participants = [p.strip() for p in participants_str.split(",") if p.strip()]
        return f"會議信息已設置: {self.meeting_title} (參與者: {', '.join(self.participants)})"

# Create the Gradio interface
def create_gradio_interface():
    recorder = MeetingRecorder()
    
    with gr.Blocks(title="智能會議記錄助手", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 智能會議記錄助手")
        gr.Markdown("### 自動記錄會議內容，識別說話者，並生成摘要")
        
        with gr.Tab("會議設置"):
            with gr.Row():
                meeting_title = gr.Textbox(label="會議標題", placeholder="輸入會議標題", value="未命名會議")
                participants = gr.Textbox(label="參與者 (用逗號分隔)", placeholder="例如: 張三, 李四, 王五")
            
            set_info_btn = gr.Button("設置會議信息")
            info_output = gr.Textbox(label="信息", interactive=False)
            
            set_info_btn.click(
                fn=recorder.set_meeting_info,
                inputs=[meeting_title, participants],
                outputs=info_output
            )
        
        with gr.Tab("錄音與轉錄"):
            with gr.Row():
                start_btn = gr.Button("開始錄音", variant="primary")
                stop_btn = gr.Button("停止錄音", variant="stop")
            
            status = gr.Textbox(label="狀態", interactive=False)
            audio_output = gr.Audio(label="錄音結果", type="filepath", interactive=False)
            
            transcription = gr.Textbox(label="轉錄結果", interactive=False, lines=10)
            transcribe_btn = gr.Button("轉錄音頻")
            
            # Connect the buttons to their respective functions
            start_btn.click(fn=recorder.start_recording, outputs=status)
            
            def stop_and_process():
                audio_file, message = recorder.stop_recording()
                return audio_file, message
            
            stop_btn.click(fn=stop_and_process, outputs=[audio_output, status])
            transcribe_btn.click(fn=recorder.transcribe_audio, inputs=audio_output, outputs=transcription)
        
        with gr.Tab("摘要生成"):
            generate_btn = gr.Button("生成會議摘要")
            summary_output = gr.Textbox(label="會議摘要", interactive=False, lines=15)
            
            generate_btn.click(fn=recorder.generate_summary, inputs=transcription, outputs=summary_output)
        
        with gr.Tab("導出"):
            export_btn = gr.Button("導出會議記錄")
            export_output = gr.Textbox(label="導出狀態", interactive=False)
            
            export_btn.click(fn=recorder.export_meeting, outputs=export_output)
    
    return app

if __name__ == "__main__":
    app = create_gradio_interface()
    app.launch(share=False)
import os
import time
import datetime
import tempfile
import gradio as gr
import pyaudio
import wave
import threading
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
import openai
import json

# Check if OpenAI API key is set in environment
if "OPENAI_API_KEY" not in os.environ:
    try:
        # Try to load from .env file if exists
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

# Constants
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1024
RECORD_SECONDS = 5  # Default chunk size for recording

class MeetingRecorder:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.record_thread = None
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.meeting_title = "未命名會議"
        self.participants = []
        self.transcriptions = []
        self.summary = ""
        self.exports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
        os.makedirs(self.exports_dir, exist_ok=True)
    
    def start_recording(self):
        if self.recording:
            return "已經在錄音中..."
        
        self.recording = True
        self.audio_data = []
        
        # Start recording in a separate thread
        self.record_thread = threading.Thread(target=self._record_audio)
        self.record_thread.daemon = True
        self.record_thread.start()
        
        return "開始錄音..."
