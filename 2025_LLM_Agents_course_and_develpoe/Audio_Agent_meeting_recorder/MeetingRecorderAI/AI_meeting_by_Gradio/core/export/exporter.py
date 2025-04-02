"""
Export module for the meeting recorder application.
"""

import os
import json
import datetime
from typing import Optional, Dict, Any, List

class Exporter:
    """Class to handle meeting record export functionality."""
    
    def __init__(self, exports_dir: str = None):
        """Initialize the exporter."""
        if exports_dir is None:
            # Default exports directory is 'exports' in the same directory as this file
            self.exports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "exports")
        else:
            self.exports_dir = exports_dir
        
        # Create the exports directory if it doesn't exist
        os.makedirs(self.exports_dir, exist_ok=True)
    
    def export_meeting(self, meeting_title: str, participants: List[str], transcriptions: List[Dict[str, str]], summary: str) -> str:
        """
        Export meeting record to a JSON file.
        
        Args:
            meeting_title: Title of the meeting
            participants: List of participant names
            transcriptions: List of transcription records
            summary: Meeting summary
            
        Returns:
            str: Status message
        """
        if not transcriptions:
            return "沒有會議記錄可以導出。"
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{meeting_title.replace(' ', '_')}_{timestamp}.json"
        filepath = os.path.join(self.exports_dir, filename)
        
        data = {
            "meeting_title": meeting_title,
            "participants": participants,
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "transcriptions": transcriptions,
            "summary": summary
        }
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return f"會議記錄已導出至 {filepath}"
        except Exception as e:
            return f"導出失敗: {str(e)}"
    
    def get_exports_dir(self) -> str:
        """Get the exports directory path."""
        return self.exports_dir
    
    def set_exports_dir(self, exports_dir: str) -> None:
        """Set the exports directory path."""
        self.exports_dir = exports_dir
        os.makedirs(self.exports_dir, exist_ok=True)
