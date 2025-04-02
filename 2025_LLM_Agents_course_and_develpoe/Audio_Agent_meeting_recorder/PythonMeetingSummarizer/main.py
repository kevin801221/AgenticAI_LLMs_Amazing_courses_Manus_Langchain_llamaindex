import os
import gradio as gr
import openai
from dotenv import load_dotenv
import tempfile
from pydub import AudioSegment

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Preprocess audio file
def preprocess_audio(audio_file_path):
    """
    Preprocesses the audio file to ensure it's in a format compatible with Whisper.
    
    Args:
        audio_file_path (str): Path to the input audio file
        
    Returns:
        str: Path to the preprocessed audio file
    """
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Convert audio to WAV format with 16kHz sample rate
        audio = AudioSegment.from_file(audio_file_path)
        audio = audio.set_frame_rate(16000)
        audio = audio.set_channels(1)
        audio.export(temp_file_path, format="wav")
        
        return temp_file_path
    except Exception as e:
        print(f"Error preprocessing audio: {e}")
        return audio_file_path

# Transcribe audio using OpenAI Whisper API
def transcribe_audio(audio_file_path, whisper_model_name="base"):
    """
    Transcribes audio to text using the OpenAI Whisper API.
    
    Args:
        audio_file_path (str): Path to the audio file
        whisper_model_name (str): Name of the Whisper model to use
        
    Returns:
        str: The transcribed text
    """
    try:
        # Preprocess the audio file
        processed_audio_path = preprocess_audio(audio_file_path)
        
        # Map the model name to OpenAI's model names
        model_mapping = {
            "tiny": "whisper-1",
            "base": "whisper-1",
            "small": "whisper-1",
            "medium": "whisper-1",
            "large": "whisper-1"
        }
        
        openai_model = model_mapping.get(whisper_model_name, "whisper-1")
        
        print(f"Transcribing audio: {processed_audio_path}")
        
        # Open the audio file
        with open(processed_audio_path, "rb") as audio_file:
            # Call the OpenAI API
            transcript = openai.audio.transcriptions.create(
                model=openai_model,
                file=audio_file
            )
        
        # Clean up the temporary file if it was created
        if processed_audio_path != audio_file_path:
            os.remove(processed_audio_path)
        
        return transcript.text
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return f"Error transcribing audio: {str(e)}"

# Generate summary using OpenAI API
def generate_summary(transcript, context="", model="gpt-4o"):
    """
    Generates a summary of the meeting transcript using OpenAI API.
    
    Args:
        transcript (str): The meeting transcript
        context (str): Optional context for the summary
        model (str): The OpenAI model to use
        
    Returns:
        str: The generated summary
    """
    try:
        prompt = f"""You are a professional meeting summarizer. Your task is to create a comprehensive summary of the following meeting transcript.
        
Context about the meeting: {context if context else 'No additional context provided.'}

The transcript is as follows:

{transcript}

Please provide a detailed summary that includes:
1. Main topics discussed
2. Key decisions made
3. Action items (with assignees if mentioned)
4. Important points raised by participants
5. Any unresolved issues or questions
6. Overall sentiment and tone of the meeting

Format your response in a clear, structured manner with appropriate headings."""

        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional meeting summarizer that creates concise, accurate, and well-structured summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return f"Error generating summary: {str(e)}"

# Save transcript to a file
def save_transcript(transcript):
    """
    Saves the transcript to a file for download.
    
    Args:
        transcript (str): The transcript text
        
    Returns:
        str: Path to the saved transcript file
    """
    transcript_file = "transcript.txt"
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript)
    return transcript_file

# Process the meeting recording
def process_meeting(audio, context, whisper_model_name, openai_model_name):
    """
    Processes the meeting recording: transcribes audio and generates a summary.
    
    Args:
        audio (str): Path to the uploaded audio file
        context (str): Optional context for the summary
        whisper_model_name (str): Whisper model to use
        openai_model_name (str): OpenAI model to use
        
    Returns:
        tuple: (summary, transcript_file_path)
    """
    try:
        # Transcribe the audio
        transcript = transcribe_audio(audio, whisper_model_name)
        
        # Save the transcript to a file
        transcript_file = save_transcript(transcript)
        
        # Generate a summary
        summary = generate_summary(transcript, context, openai_model_name)
        
        return summary, transcript_file, transcript
    except Exception as e:
        error_message = f"Error processing meeting: {str(e)}"
        print(error_message)
        return error_message, None, error_message

# Available Whisper models (note: OpenAI API currently only supports one model, but we keep the options for UI consistency)
WHISPER_MODELS = ["tiny", "base", "small", "medium", "large"]

# Available OpenAI models
OPENAI_MODELS = ["gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"]

# Main Gradio interface
def create_gradio_interface():
    """
    Creates and configures the Gradio interface.
    
    Returns:
        gr.Interface: The configured Gradio interface
    """
    with gr.Blocks(title="AI Meeting Summarizer") as iface:
        gr.Markdown("# AI Meeting Summarizer")
        gr.Markdown("Upload an audio recording of a meeting to get a detailed summary.")
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(type="filepath", label="Upload Meeting Recording")
                context_input = gr.Textbox(
                    label="Meeting Context (Optional)", 
                    placeholder="Provide any additional context about the meeting (e.g., project name, participants, purpose)"
                )
                
                with gr.Row():
                    whisper_model = gr.Dropdown(
                        choices=WHISPER_MODELS,
                        label="Select Whisper Model for Transcription",
                        value="base",
                        info="Note: OpenAI API currently uses the same model regardless of selection"
                    )
                    
                    openai_model = gr.Dropdown(
                        choices=OPENAI_MODELS,
                        label="Select OpenAI Model for Summarization",
                        value="gpt-4o-mini",
                        info="More powerful models provide better summaries but cost more"
                    )
                
                submit_btn = gr.Button("Process Meeting Recording", variant="primary")
            
            with gr.Column():
                summary_output = gr.Textbox(
                    label="Meeting Summary", 
                    placeholder="Summary will appear here...",
                    lines=15,
                    show_copy_button=True
                )
                transcript_output = gr.Textbox(
                    label="Full Transcript", 
                    placeholder="Transcript will appear here...",
                    lines=10,
                    show_copy_button=True
                )
                file_output = gr.File(label="Download Transcript")
        
        # Set up the submission action
        submit_btn.click(
            fn=process_meeting,
            inputs=[audio_input, context_input, whisper_model, openai_model],
            outputs=[summary_output, file_output, transcript_output]
        )
        
        # Add usage instructions
        gr.Markdown("""
        ## How to Use
        1. Upload an audio recording of your meeting
        2. Optionally provide context about the meeting
        3. Select the models to use for transcription and summarization
        4. Click "Process Meeting Recording"
        5. View and download the summary and transcript
        
        ## Notes
        - The OpenAI Whisper API is used for transcription (currently only one model is available)
        - The GPT-4o model provides the most detailed summaries but costs more to use
        - Make sure your OpenAI API key is set in the .env file
        """)
    
    return iface

# Main function
if __name__ == "__main__":
    # Create and launch the Gradio interface
    iface = create_gradio_interface()
    iface.launch(share=True)
