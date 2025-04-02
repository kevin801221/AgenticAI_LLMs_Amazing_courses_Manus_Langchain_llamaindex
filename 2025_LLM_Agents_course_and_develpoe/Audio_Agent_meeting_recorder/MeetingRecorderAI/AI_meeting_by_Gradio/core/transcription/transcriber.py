"""
Transcription module for the meeting recorder application.
"""

import os
import datetime
from typing import Optional, Dict, Any, List
import openai

class Transcriber:
    """Class to handle audio transcription functionality."""
    
    def __init__(self):
        """Initialize the transcriber."""
        self.transcriptions = []
        
        # Check if OpenAI API key is set in environment
        if "OPENAI_API_KEY" not in os.environ:
            try:
                # Try to load from .env file if exists
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass
    
    def transcribe_audio(self, audio_file: str) -> str:
        """Transcribe audio file to text using OpenAI's Whisper model."""
        try:
            with open(audio_file, "rb") as file:
                transcription = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=file,
                    language="zh"  # Chinese language
                )
            
            text = transcription.text
            self.add_transcription(text)
            
            return text
        except Exception as e:
            return f"轉錄失敗: {str(e)}"
    
    def add_transcription(self, text: str) -> None:
        """Add a transcription to the history."""
        self.transcriptions.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text": text
        })
    
    def get_all_transcriptions(self) -> List[Dict[str, str]]:
        """Get all transcriptions."""
        return self.transcriptions
    
    def get_combined_text(self) -> str:
        """Get all transcriptions combined into a single text."""
        return "\n".join([t["text"] for t in self.transcriptions])
    
    def clear_transcriptions(self) -> None:
        """Clear all transcriptions."""
        self.transcriptions = []
