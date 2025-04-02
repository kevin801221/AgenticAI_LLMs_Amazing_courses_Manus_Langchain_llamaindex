"""
Audio recorder module for the meeting recorder application.
"""

import os
import tempfile
import pyaudio
import wave
import threading
from typing import Optional, List, Dict, Any, Tuple

# Constants for audio recording
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1024

class AudioRecorder:
    """Class to handle audio recording functionality."""
    
    def __init__(self):
        """Initialize the audio recorder."""
        self.recording = False
        self.audio_data = []
        self.record_thread = None
        self.p = pyaudio.PyAudio()
        self.stream = None
    
    def start_recording(self) -> str:
        """Start recording audio."""
        if self.recording:
            return "已經在錄音中..."
        
        self.recording = True
        self.audio_data = []
        
        # Start recording in a separate thread
        self.record_thread = threading.Thread(target=self._record_audio)
        self.record_thread.daemon = True
        self.record_thread.start()
        
        return "開始錄音..."
    
    def _record_audio(self) -> None:
        """Internal method to record audio in a separate thread."""
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
    
    def stop_recording(self) -> Tuple[str, str]:
        """Stop recording and save the audio to a temporary file."""
        if not self.recording:
            return None, "沒有正在進行的錄音。"
        
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
    
    def cleanup(self) -> None:
        """Clean up resources when the recorder is no longer needed."""
        if self.p:
            self.p.terminate()
