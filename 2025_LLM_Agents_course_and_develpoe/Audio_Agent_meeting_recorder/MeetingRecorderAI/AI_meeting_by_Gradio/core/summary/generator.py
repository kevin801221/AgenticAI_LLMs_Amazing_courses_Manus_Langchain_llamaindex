"""
Summary generator module for the meeting recorder application.
"""

import os
from typing import Optional, Dict, Any
import openai

class SummaryGenerator:
    """Class to handle meeting summary generation functionality."""
    
    def __init__(self):
        """Initialize the summary generator."""
        self.summary = ""
        
        # Check if OpenAI API key is set in environment
        if "OPENAI_API_KEY" not in os.environ:
            try:
                # Try to load from .env file if exists
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass
    
    def generate_summary(self, transcription: str, meeting_title: str = "", participants: list = None) -> str:
        """Generate a summary from the meeting transcription."""
        if not transcription:
            return "沒有足夠的內容來生成摘要。"
        
        if participants is None:
            participants = []
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "你是一個專業的會議記錄助手。請根據提供的會議記錄生成一個簡潔但全面的摘要，包括主要討論點、決策和行動項目。使用繁體中文回答。"},
                    {"role": "user", "content": f"會議標題: {meeting_title}\n參與者: {', '.join(participants)}\n\n會議記錄:\n{transcription}"}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            summary = response.choices[0].message.content
            self.summary = summary
            return summary
        except Exception as e:
            return f"生成摘要失敗: {str(e)}"
    
    def get_summary(self) -> str:
        """Get the current summary."""
        return self.summary
    
    def clear_summary(self) -> None:
        """Clear the current summary."""
        self.summary = ""
