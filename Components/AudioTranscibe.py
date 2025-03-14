import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(audio_path, language="en"):
    """
    Transcribe audio file using Groq API.
    Returns list of [text, start_time, end_time] segments.
    """
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",  # Adjust model as needed
                response_format="verbose_json",  # For timestamps
                language=language
            )
        
        # Extract segments with timestamps
        segments = []
        for segment in transcription.segments:
            text = segment["text"].strip()
            start = segment["start"]
            end = segment["end"]
            segments.append([text, start, end])
        
        print(f"Transcription completed for {audio_path}")
        return segments
    
    except Exception as e:
        print(f"Error transcribing {audio_path}: {e}")
        return []

def main():
    # For standalone testing
    audio_path = input("Enter audio file path: ")
    if os.path.exists(audio_path):
        segments = transcribe_audio(audio_path)
        for text, start, end in segments:
            print(f"[{start}s - {end}s]: {text}")
    else:
        print(f"Audio file not found: {audio_path}")

if __name__ == "__main__":
    main()