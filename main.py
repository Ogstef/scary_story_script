import ollama
import requests
import os
import random
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
import moviepy.config as cfg
import subprocess
import time




cfg.IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"



AUDIO_PATH = "C:\\Users\\sdavg\\Projects\\GtaVids\\TTS\\story.mp3"
VIDEO_FOLDER = "C:\\Users\\sdavg\\Projects\\GtaVids\\Gameplay"
OUTPUT_VIDEO_PATH = "C:\\Users\\sdavg\\Projects\\GtaVids\\Final\\scary_story_video.mp4"

def generate_scary_story():
    """Generate a scary story using Ollama's Mistral model."""
    story = ollama.chat("mistral", [
        {"role": "user", "content": "Generate for me a quality scary story. I want it to have a beginning, middle, and finish that captivates the end reader and can be read in a short minute, max 200 words. I want the format to be in a paragraph all in one."}
    ]) 
    print("Generated story:" + story['message']['content'])
    return story['message']['content']


def text_to_speech(text, output_file):
    """Convert text to speech using gTTS (Google Text-to-Speech)."""

    # Ensure the file is not in use before deleting
    if os.path.exists(output_file):
        for _ in range(5):  # Retry 5 times
            try:
                os.remove(output_file)
                print(f"Deleted existing file: {output_file}")
                break  # Successfully deleted, exit loop
            except PermissionError:
                print("File is in use. Retrying in 2 seconds...")
                time.sleep(2)
        else:
            print("Could not delete the file after multiple attempts.")
            return  # Stop execution if file cannot be deleted

    # Generate speech from text
    tts = gTTS(text=text, lang="en")
    tts.save(output_file)

    print(f"Audio saved as {output_file}")



def save_subtitles(text, subtitle_path, audio_path):
    """Splits text into 4-word chunks and adjusts subtitle timing dynamically to prevent fast transitions."""
    words = text.split()
    chunks = [" ".join(words[i:i+4]) for i in range(0, len(words), 4)]  # Split into 4-word chunks

    if not os.path.exists(audio_path):
        print("Audio file missing. Generating it now...")
        text_to_speech(text, audio_path)  # Generate the audio file first

    # Load audio and release the file properly
    with AudioFileClip(audio_path) as audio:
        total_duration = audio.duration  

    num_chunks = len(chunks)
    
    # Base duration per subtitle (equal split)
    avg_duration = total_duration / num_chunks
    
    # Enforce a minimum and maximum duration to balance speed
    min_duration = 1.8  # Minimum 1.2 sec per subtitle
    max_duration = 5.0  # Maximum 4 sec per subtitle
    
    # Adjust chunk durations
    chunk_durations = [max(min(avg_duration, max_duration), min_duration)] * num_chunks

    subtitles = []
    start_time = 0
    for i, (chunk, duration) in enumerate(zip(chunks, chunk_durations)):
        end_time = start_time + duration
        subtitles.append(f"{i+1}\n{format_time(start_time)} --> {format_time(end_time)}\n{chunk}\n\n")
        start_time = end_time

    with open(subtitle_path, "w", encoding="utf-8") as f:
        f.write("".join(subtitles))

    print(f"Subtitles saved to {subtitle_path}")




def format_time(seconds):
    """Converts seconds into SRT timestamp format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},000"







def select_random_video(video_folder):
    """Select a random video file from the folder."""
    videos = [f for f in os.listdir(video_folder) if f.endswith((".mp4", ".avi", ".mov"))]
    if not videos:
        raise FileNotFoundError("No video files found in the folder!")
    return os.path.join(video_folder, random.choice(videos))


def create_video_with_audio_and_subtitles(video_path, audio_path, subtitle_path, output_path):
    """Merges a video, audio, and subtitles into a final video."""
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    video = video.subclip(0, min(video.duration, audio.duration))
    video = video.set_audio(audio)

    # Load subtitles from file
    subtitle_clips = []
    with open(subtitle_path, "r", encoding="utf-8") as f:
        lines = f.read().strip().split("\n\n")
    
    for block in lines:
        parts = block.split("\n")
        if len(parts) < 3:
            continue

        start_time, end_time = parts[1].split(" --> ")
        text = parts[2]

        subtitle = TextClip(text, fontsize=40, color="white", size=(video.w - 250, None))  # Adjusted for better readability
        subtitle = subtitle.set_position(("center", video.h * 0.7))  # Adjust position
        subtitle = subtitle.set_start(parse_time(start_time)).set_end(parse_time(end_time))

        subtitle_clips.append(subtitle)

    final_video = CompositeVideoClip([video] + subtitle_clips)
    final_video.write_videofile(output_path, codec="libx264", fps=video.fps)



def parse_time(time_str):
    """Converts SRT timestamp format to seconds."""
    h, m, s = map(int, time_str.replace(",000", "").split(":"))
    return h * 3600 + m * 60 + s

if __name__ == "__main__":
    print("Generating scary story...")
    story = generate_scary_story()
    
    subtitle_path = "C:\\Users\\sdavg\\Projects\\YTScript\\story.srt"
    save_subtitles(story, subtitle_path, AUDIO_PATH)  # Save subtitles

    print("Converting story to speech...")
    text_to_speech(story, AUDIO_PATH)

    print("Selecting a random gameplay video...")
    video_path = select_random_video(VIDEO_FOLDER)

    print("Merging video, audio, and subtitles...")
    create_video_with_audio_and_subtitles(video_path, AUDIO_PATH, subtitle_path, OUTPUT_VIDEO_PATH)

    print(f"Final video saved to: {OUTPUT_VIDEO_PATH}")
