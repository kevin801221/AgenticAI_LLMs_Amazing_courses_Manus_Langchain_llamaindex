import os
import openai
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_summary(transcript, context="", model="gpt-4o-mini"):
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
        return f"Error generating summary: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Meeting Transcript Summarizer')
    parser.add_argument('--input', '-i', type=str, help='Path to the transcript text file')
    parser.add_argument('--output', '-o', type=str, help='Path to save the summary')
    parser.add_argument('--context', '-c', type=str, default='', help='Context about the meeting')
    parser.add_argument('--model', '-m', type=str, default='gpt-4o-mini', 
                        choices=['gpt-3.5-turbo', 'gpt-4o-mini', 'gpt-4o'], 
                        help='OpenAI model to use')
    
    args = parser.parse_args()
    
    # Read transcript from file
    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                transcript = f.read()
        except Exception as e:
            print(f"Error reading transcript file: {str(e)}")
            return
    else:
        # If no input file is provided, prompt for transcript
        print("Please enter the meeting transcript (press Enter twice to finish):")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        transcript = "\n".join(lines)
    
    # Generate summary
    summary = generate_summary(transcript, args.context, args.model)
    
    # Save or print summary
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"Summary saved to {args.output}")
        except Exception as e:
            print(f"Error saving summary: {str(e)}")
            print("\nSummary:")
            print(summary)
    else:
        print("\nSummary:")
        print(summary)

if __name__ == "__main__":
    main()
