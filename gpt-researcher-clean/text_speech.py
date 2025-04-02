# from openai import OpenAI
# client = OpenAI()

# audio_file = open("/path/to/file/speech.mp3", "rb")
# stream = client.audio.transcriptions.create(
#   model="gpt-4o-mini-transcribe", 
#   file=audio_file, 
#   response_format="text",
#   stream=True
# )

# for event in stream:
#   print(event)
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()
speech_file_path = Path(__file__).parent / "speech2.mp3"
response = client.audio.speech.create(
  model="gpt-4o-mini-tts",
  voice="ballad",
  input="今天真是美好的一天,人們都充滿愛與希望",
  instructions="Speak in a cheerful and positive tone.",
)
response.stream_to_file(speech_file_path)
