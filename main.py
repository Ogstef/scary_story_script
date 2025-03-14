import ollama
import os
import random
import time
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from datetime import datetime

AUDIO_PATH = "C:\\Users\\sdavg\\Projects\\GtaVids\\TTS\\story.wav"  # Output audio in WAV format
VIDEO_FOLDER = "C:\\Users\\sdavg\\Projects\\GtaVids\\Gameplay"
VIDEO_FOLDER_2 = "C:\\Users\\sdavg\\Projects\\MinecraftVids"
OUTPUT_VIDEO_PATH = "C:\\Users\\sdavg\\Projects\\GtaVids\\Final"
MUSIC_FOLDER = "C:\\Users\\sdavg\\Projects\\BackGroundMusic"  # Folder with eerie music

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
    return AudioFileClip(output_file)  # Return the audio file as a clip

def select_random_video(video_folders):
    """Select a random video file from one of the provided folders."""
    selected_folder = random.choice(video_folders)  # Randomly choose one folder
    videos = [f for f in os.listdir(selected_folder) if f.endswith((".mp4", ".avi", ".mov"))]
    if not videos:
        raise FileNotFoundError(f"No video files found in folder: {selected_folder}")
    return os.path.join(selected_folder, random.choice(videos))

def select_random_music(music_folder):
    """Select a random background music file from the given folder."""
    music_files = [f for f in os.listdir(music_folder) if f.endswith((".mp3", ".wav"))]
    if not music_files:
        raise FileNotFoundError(f"No music files found in folder: {music_folder}")
    return os.path.join(music_folder, random.choice(music_files))

def combine_audio_with_music(speech_audio, music_audio):
    """Combine speech audio with background music while keeping the music at lower volume."""
    # Set the music audio volume lower (this volume can be adjusted further)
    music_audio = music_audio.volumex(0.2)  # Adjust the volume multiplier as needed
    
    # Combine both audios (speech and music) to play simultaneously
    final_audio = CompositeAudioClip([speech_audio, music_audio])
    return final_audio

def create_video_with_audio(video_path, tts_audio_clip, music_audio_clip, output_path):
    """Merges a video and audio into a final video."""
    video = VideoFileClip(video_path)
    
    # Ensure the video duration matches the TTS audio duration
    video = video.subclip(0, min(video.duration, tts_audio_clip.duration))
    
    # Combine TTS audio with background music while keeping the music at a lower volume
    final_audio = CompositeAudioClip([tts_audio_clip, music_audio_clip.volumex(0.2)])  # Lower music volume
    
    # Set the final audio for the video
    video = video.set_audio(final_audio)
    
    # Write the final video to the output file
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
    speech_audio = text_to_speech(story, AUDIO_PATH)
    
    print("Selecting a random gameplay or other video...")
    video_folders = [VIDEO_FOLDER, VIDEO_FOLDER_2]  # List both folders
    video_path = select_random_video(video_folders)
    
    print("Selecting random eerie background music...")
    music_path = select_random_music(MUSIC_FOLDER)
    music_audio = AudioFileClip(music_path)
    
    print("Combining speech audio with background music...")
    final_audio = combine_audio_with_music(speech_audio, music_audio)
    
    print("Merging video and audio...")
    print("Merging video and audio...")
    output_video_path = generate_unique_filename()

    # Corrected function call by passing final_audio directly as the second argument
    create_video_with_audio(video_path, speech_audio, music_audio, output_video_path)

    
