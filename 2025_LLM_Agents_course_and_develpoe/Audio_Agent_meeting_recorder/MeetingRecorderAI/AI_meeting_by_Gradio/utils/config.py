"""
Configuration utility for the meeting recorder application.
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for the meeting recorder application."""
    
    def __init__(self):
        """Initialize the configuration."""
        # Audio recording settings
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        
        # OpenAI API settings
        self.transcription_model = "whisper-1"
        self.summary_model = "gpt-4-turbo"
        self.summary_temperature = 0.3
        self.summary_max_tokens = 1000
        
        # Application settings
        self.default_meeting_title = "未命名會議"
        self.language = "zh"  # Chinese language
        
        # Check if OpenAI API key is set in environment
        if "OPENAI_API_KEY" not in os.environ:
            try:
                # Try to load from .env file if exists
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio recording configuration."""
        return {
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "chunk_size": self.chunk_size
        }
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI API configuration."""
        return {
            "transcription_model": self.transcription_model,
            "summary_model": self.summary_model,
            "summary_temperature": self.summary_temperature,
            "summary_max_tokens": self.summary_max_tokens
        }
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration."""
        return {
            "default_meeting_title": self.default_meeting_title,
            "language": self.language
        }
