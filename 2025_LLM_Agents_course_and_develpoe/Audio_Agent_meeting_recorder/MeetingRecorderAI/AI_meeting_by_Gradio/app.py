"""
Main application for the AI meeting recorder using Gradio.
"""

import os
import gradio as gr
from core.audio import AudioRecorder
from core.transcription import Transcriber
from core.summary import SummaryGenerator
from core.export import Exporter
from utils import Config

class MeetingRecorderApp:
    """Main application class for the meeting recorder."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = Config()
        self.audio_recorder = AudioRecorder()
        self.transcriber = Transcriber()
        self.summary_generator = SummaryGenerator()
        self.exporter = Exporter()
        
        self.meeting_title = self.config.get_app_config()["default_meeting_title"]
        self.participants = []
    
    def set_meeting_info(self, title, participants_str):
        """Set meeting information."""
        self.meeting_title = title if title else self.config.get_app_config()["default_meeting_title"]
        self.participants = [p.strip() for p in participants_str.split(",") if p.strip()]
        return f"會議信息已設置: {self.meeting_title} (參與者: {', '.join(self.participants)})"
    
    def start_recording(self):
        """Start recording audio."""
        return self.audio_recorder.start_recording()
    
    def stop_recording(self):
        """Stop recording audio."""
        return self.audio_recorder.stop_recording()
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio to text."""
        if not audio_file:
            return "請先錄製音頻。"
        return self.transcriber.transcribe_audio(audio_file)
    
    def generate_summary(self, transcription):
        """Generate meeting summary."""
        return self.summary_generator.generate_summary(
            transcription, 
            meeting_title=self.meeting_title, 
            participants=self.participants
        )
    
    def export_meeting(self):
        """Export meeting record."""
        return self.exporter.export_meeting(
            self.meeting_title,
            self.participants,
            self.transcriber.get_all_transcriptions(),
            self.summary_generator.get_summary()
        )
    
    def create_interface(self):
        """Create the Gradio interface."""
        with gr.Blocks(title="YCM智能會議記錄助手", theme=gr.themes.Soft()) as app:
            gr.Markdown("# YCM智能會議記錄助手")
            gr.Markdown("### 自動記錄會議內容，識別說話者，並生成摘要")
            
            with gr.Tab("會議設置"):
                with gr.Row():
                    meeting_title = gr.Textbox(label="會議標題", placeholder="輸入會議標題", value=self.meeting_title)
                    participants = gr.Textbox(label="參與者 (用逗號分隔)", placeholder="例如: 張三, 李四, 王五")
                
                set_info_btn = gr.Button("設置會議信息")
                info_output = gr.Textbox(label="信息", interactive=False)
                
                set_info_btn.click(
                    fn=self.set_meeting_info,
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
                start_btn.click(fn=self.start_recording, outputs=status)
                
                def stop_and_process():
                    audio_file, message = self.stop_recording()
                    return audio_file, message
                
                stop_btn.click(fn=stop_and_process, outputs=[audio_output, status])
                transcribe_btn.click(fn=self.transcribe_audio, inputs=audio_output, outputs=transcription)
            
            with gr.Tab("摘要生成"):
                generate_btn = gr.Button("生成會議摘要")
                summary_output = gr.Textbox(label="會議摘要", interactive=False, lines=15)
                
                generate_btn.click(fn=self.generate_summary, inputs=transcription, outputs=summary_output)
            
            with gr.Tab("導出"):
                export_btn = gr.Button("導出會議記錄")
                export_output = gr.Textbox(label="導出狀態", interactive=False)
                
                export_btn.click(fn=self.export_meeting, outputs=export_output)
        
        return app

def main():
    """Main entry point for the application."""
    app = MeetingRecorderApp().create_interface()
    app.launch(share=False)

if __name__ == "__main__":
    main()
