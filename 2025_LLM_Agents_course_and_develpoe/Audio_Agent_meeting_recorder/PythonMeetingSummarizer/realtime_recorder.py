import os
import time
import threading
import queue
import tempfile
import wave
import pyaudio
import numpy as np
import requests
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
SILENCE_THRESHOLD = 500  # Adjust based on your microphone and environment
SILENCE_DURATION = 2  # seconds of silence to consider a pause in speech

class RealtimeTranscriber:
    def __init__(self, model="whisper-1"):
        self.model = model
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        self.is_recording = False
        self.is_transcribing = False
        self.audio = pyaudio.PyAudio()
        self.full_transcript = ""
        self.api_key = api_key
        
    def start_recording(self):
        """Start recording audio from microphone"""
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        self.is_transcribing = True
        self.transcription_thread = threading.Thread(target=self._process_audio)
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
        
        print("Recording started. Speak into the microphone...")
        print("Press Ctrl+C to stop recording and generate summary.")
        
    def stop_recording(self):
        """Stop recording audio"""
        self.is_recording = False
        self.is_transcribing = False
        print("\nRecording stopped.")
        
    def _is_silent(self, data):
        """Check if the audio chunk is silent"""
        audio_data = np.frombuffer(data, dtype=np.int16)
        return np.abs(audio_data).mean() < SILENCE_THRESHOLD
        
    def _record_audio(self):
        """Record audio from microphone and add to queue"""
        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        current_audio = []
        silent_chunks = 0
        required_silent_chunks = int(RATE / CHUNK * SILENCE_DURATION)
        
        try:
            while self.is_recording:
                data = stream.read(CHUNK, exception_on_overflow=False)
                current_audio.append(data)
                
                # Check for silence to determine when to process a segment
                if self._is_silent(data):
                    silent_chunks += 1
                else:
                    silent_chunks = 0
                
                # If we've detected enough silence and have some audio, process it
                if silent_chunks >= required_silent_chunks and len(current_audio) > required_silent_chunks:
                    # Remove the trailing silence
                    audio_segment = current_audio[:-required_silent_chunks]
                    if audio_segment:
                        self.audio_queue.put(audio_segment)
                    current_audio = []
                    silent_chunks = 0
        finally:
            stream.stop_stream()
            stream.close()
            
            # Process any remaining audio
            if current_audio:
                self.audio_queue.put(current_audio)
    
    def _save_audio_segment(self, audio_frames):
        """Save audio frames to a temporary WAV file"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name
            
        with wave.open(temp_filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(audio_frames))
            
        return temp_filename
    
    def _process_audio(self):
        """Process audio segments from the queue and transcribe them"""
        while self.is_transcribing or not self.audio_queue.empty():
            try:
                # Get audio segment from queue (wait up to 1 second)
                audio_segment = self.audio_queue.get(timeout=1)
                
                # Save to temporary file
                temp_filename = self._save_audio_segment(audio_segment)
                
                # Transcribe the audio
                transcript = self._transcribe_audio(temp_filename)
                
                # Clean up temporary file
                os.unlink(temp_filename)
                
                if transcript:
                    self.text_queue.put(transcript)
                    self.full_transcript += transcript + " "
                    print(f"\nTranscript: {transcript}")
                    print("\nContinue speaking or press Ctrl+C to stop and generate summary.")
                
                self.audio_queue.task_done()
            except queue.Empty:
                # No audio to process, continue waiting
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")
    
    def _transcribe_audio(self, audio_file_path):
        """Transcribe audio file using OpenAI Whisper API directly with requests"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            with open(audio_file_path, "rb") as audio_file:
                files = {
                    "file": (os.path.basename(audio_file_path), audio_file, "audio/wav")
                }
                data = {
                    "model": self.model
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers=headers,
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    return response.json()["text"]
                else:
                    print(f"API Error: {response.status_code} - {response.text}")
                    return ""
                
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""
    
    def generate_summary(self, context="", model="gpt-4o-mini"):
        """Generate summary of the full transcript using direct API calls"""
        if not self.full_transcript:
            return "No transcript available to summarize."
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""You are a professional meeting summarizer. Your task is to create a comprehensive summary of the following meeting transcript.
            
Context about the meeting: {context if context else 'No additional context provided.'}

The transcript is as follows:

{self.full_transcript}

Please provide a detailed summary that includes:
1. Main topics discussed
2. Key decisions made
3. Action items (with assignees if mentioned)
4. Important points raised by participants
5. Any unresolved issues or questions
6. Overall sentiment and tone of the meeting

Format your response in a clear, structured manner with appropriate headings."""

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a professional meeting summarizer that creates concise, accurate, and well-structured summaries."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1500
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return f"Error generating summary: API returned status code {response.status_code}"
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def save_transcript(self, filename="transcript.txt"):
        """Save the full transcript to a file"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.full_transcript)
        print(f"Transcript saved to {filename}")
    
    def save_summary(self, summary, filename="summary.txt"):
        """Save the summary to a file"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Summary saved to {filename}")

def main():
    print("Real-time Meeting Recorder and Summarizer")
    print("=========================================")
    
    # Create transcriber
    transcriber = RealtimeTranscriber()
    
    try:
        # Start recording
        transcriber.start_recording()
        
        # Keep the main thread running
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        # Stop recording when Ctrl+C is pressed
        transcriber.stop_recording()
        
        # Ask for meeting context
        context = input("\nEnter any context about the meeting (optional): ")
        
        # Select model for summarization
        print("\nSelect model for summarization:")
        print("1. gpt-3.5-turbo (faster, less expensive)")
        print("2. gpt-4o-mini (balanced)")
        print("3. gpt-4o (most detailed, more expensive)")
        model_choice = input("Enter your choice (1-3) [default: 2]: ")
        
        if model_choice == "1":
            model = "gpt-3.5-turbo"
        elif model_choice == "3":
            model = "gpt-4o"
        else:
            model = "gpt-4o-mini"
        
        # Save transcript
        transcriber.save_transcript()
        
        # Generate and save summary
        print("\nGenerating summary...")
        summary = transcriber.generate_summary(context, model)
        transcriber.save_summary(summary)
        
        # Print summary
        print("\n=========== MEETING SUMMARY ===========\n")
        print(summary)
        print("\n=======================================\n")
    
    finally:
        # Clean up
        transcriber.audio.terminate()

if __name__ == "__main__":
    main()