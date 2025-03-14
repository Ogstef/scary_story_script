import ollama
import os
import random
import time
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip
from datetime import datetime



AUDIO_PATH = "C:\\Users\\sdavg\\Projects\\GtaVids\\TTS\\story.wav"  # Output audio in WAV format
VIDEO_FOLDER = "C:\\Users\\sdavg\\Projects\\GtaVids\\Gameplay"
VIDEO_FOLDER_2 = "C:\\Users\\sdavg\\Projects\\MinecraftVids"
OUTPUT_VIDEO_PATH = "C:\\Users\\sdavg\\Projects\\GtaVids\\Final"

def generate_scary_story():
    """Generate a scary story using Ollama's Mistral model."""
    story = ollama.chat("deepseek-llm", [
        {
            "role": "user",
            "content": "Write a short, terrifying horror story in a randomly chosen setting and subgenre. Pick from: cosmic horror, psychological horror, ghost story, urban legend, or sci-fi horror. Make the ending shocking and unexpected. Keep it between 200-100 words and make the ending make sense."
        }

    ]) 
    print("Generated story:\n" + story['message']['content'])
    return story['message']['content']

def text_to_speech(text, output_file):
    """Convert text to speech using gTTS (Google Text-to-Speech)."""
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            print(f"Deleted existing file: {output_file}")
        except PermissionError:
            print("File is in use. Retrying in 2 seconds...")
            time.sleep(2)
            os.remove(output_file)

    tts = gTTS(text=text, lang="en")
    tts.save(output_file)
    print(f"Audio saved as {output_file}")

def select_random_video(video_folders):
    """Select a random video file from one of the provided folders."""
    selected_folder = random.choice(video_folders)  # Randomly choose one folder
    videos = [f for f in os.listdir(selected_folder) if f.endswith((".mp4", ".avi", ".mov"))]
    if not videos:
        raise FileNotFoundError(f"No video files found in folder: {selected_folder}")
    return os.path.join(selected_folder, random.choice(videos))

def create_video_with_audio(video_path, audio_path, output_path):
    """Merges a video and audio into a final video."""
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    video = video.subclip(0, min(video.duration, audio.duration))
    video = video.set_audio(audio)
    
    video.write_videofile(output_path, codec="libx264", fps=video.fps)
    print(f"Final video saved to: {output_path}")

def generate_unique_filename():
    """Generate a unique filename with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(OUTPUT_VIDEO_PATH, f"scary_story_{timestamp}.mp4")

if __name__ == "__main__":
    print("Generating scary story...")
    story = generate_scary_story()
    
    print("Converting story to speech...")
    text_to_speech(story, AUDIO_PATH)
    
    print("Selecting a random gameplay or other video...")
    video_folders = [VIDEO_FOLDER, VIDEO_FOLDER_2]  # List both folders
    video_path = select_random_video(video_folders)
    
    print("Merging video and audio...")
    output_video_path = generate_unique_filename()
    create_video_with_audio(video_path, AUDIO_PATH, output_video_path)