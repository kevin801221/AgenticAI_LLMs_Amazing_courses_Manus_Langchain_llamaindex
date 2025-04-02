import os
import gradio as gr
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def process_text(transcript, context, model_name):
    """
    Generate a summary of the provided transcript using OpenAI.
    
    Args:
        transcript (str): The meeting transcript text
        context (str): Optional context for the summary
        model_name (str): The OpenAI model to use
        
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
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a professional meeting summarizer that creates concise, accurate, and well-structured summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# Available OpenAI models
OPENAI_MODELS = ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"]

# Create Gradio interface
def create_interface():
    with gr.Blocks(title="Simple Meeting Summarizer") as iface:
        gr.Markdown("# Simple Meeting Summarizer")
        gr.Markdown("Paste your meeting transcript to get a detailed summary.")
        
        with gr.Row():
            with gr.Column():
                transcript_input = gr.Textbox(
                    label="Meeting Transcript", 
                    placeholder="Paste your meeting transcript here...",
                    lines=10
                )
                context_input = gr.Textbox(
                    label="Meeting Context (Optional)", 
                    placeholder="Provide any additional context about the meeting (e.g., project name, participants, purpose)"
                )
                model_select = gr.Dropdown(
                    choices=OPENAI_MODELS,
                    label="Select OpenAI Model",
                    value="gpt-4o-mini"
                )
                submit_btn = gr.Button("Generate Summary", variant="primary")
            
            with gr.Column():
                summary_output = gr.Textbox(
                    label="Meeting Summary", 
                    placeholder="Summary will appear here...",
                    lines=15,
                    show_copy_button=True
                )
        
        # Set up the submission action
        submit_btn.click(
            fn=process_text,
            inputs=[transcript_input, context_input, model_select],
            outputs=summary_output
        )
        
        # Add usage instructions
        gr.Markdown("""
        ## How to Use
        1. Paste your meeting transcript in the text box
        2. Optionally provide context about the meeting
        3. Select the OpenAI model to use for summarization
        4. Click "Generate Summary"
        
        ## Notes
        - The GPT-4o model provides the most detailed summaries but costs more to use
        - Make sure your OpenAI API key is set in the .env file
        """)
    
    return iface

# Main function
if __name__ == "__main__":
    # Create and launch the Gradio interface
    iface = create_interface()
    iface.launch(share=True)
