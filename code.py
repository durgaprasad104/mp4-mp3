import streamlit as st
import requests
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import os
import time

# Function to download audio from YouTube video
def download_audio_from_youtube(video_url, output_path="audio.mp4"):
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    if audio_stream:
        audio_stream.download(filename=output_path)
        return output_path
    else:
        raise ValueError("No audio stream found.")

# Function to download video from YouTube and merge with audio if necessary
def download_video_from_youtube(video_url, quality, output_path="video.mp4"):
    yt = YouTube(video_url)
    
    video_stream = None
    if quality == 'Low':
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first()
    elif quality == 'High (HD)':
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4', res="1080p").first()
        if not video_stream:
            st.write("1080p not available, trying 720p...")
            video_stream = yt.streams.filter(progressive=True, file_extension='mp4', res="720p").first()
        if not video_stream:
            st.write("720p not available, trying highest available resolution with audio...")
            video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

    if video_stream:
        downloaded_path = video_stream.download(filename=output_path)
        return downloaded_path
    else:
        raise ValueError(f"Unable to download video at the selected quality: {quality}")

# Function to transcribe audio using Whisper model
def transcribe_audio(file):
   API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
   headers = {"Authorization": "Bearer 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"}
    
    with open(file, "rb") as f:
        data = f.read()
    
    for _ in range(10):  # Retry up to 10 times
        response = requests.post(API_URL, headers=headers, data=data)
        result = response.json()
        
        if 'error' not in result:
            return result
        elif 'estimated_time' in result:
            st.write(f"Model is loading, estimated time: {result['estimated_time']} seconds")
            time.sleep(result['estimated_time'])  # Wait for the estimated time
        else:
            st.write("Unexpected error occurred:", result)
            return result
    
    return {"error": "Failed to load model after multiple attempts"}

# Streamlit configuration
st.set_page_config(page_title="YouTube Video Downloader & Transcriber",
                   page_icon='🎥',
                   layout='centered',
                   initial_sidebar_state='expanded')

# User name input
username = st.sidebar.text_input("Enter your name")

if not username:
    st.sidebar.warning("Please enter your name to use the app.")
    st.stop()

st.sidebar.title(f"Welcome, {username}!")
st.sidebar.title("About the App")
st.sidebar.info(
    """
    This app allows you to download and transcribe the audio or video of a YouTube video.
    - Enter the YouTube video URL
    - Download the audio or video
    - Transcribe the audio to text

    *Note:* The download and transcription processes may take some time depending on the length of the video and server load.
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    *Developed by DP*
    """
)

st.header("YouTube Video/Audio Downloader & Transcriber 🎥")

# Input field for YouTube URL
video_url = st.text_input("Enter the YouTube Video URL")

# Dropdown menu for selecting video quality
video_quality = st.selectbox(
    "Select Video Quality",
    ("Low", "High (HD)")
)

# Download video button
if st.button("Download Video", key="download_video_button", help="Click to download the YouTube video"):
    if video_url:
        try:
            st.write(f"Downloading {video_quality} quality video...")
            video_file = download_video_from_youtube(video_url, video_quality)
            
            if video_file:
                # Provide download link for the video file
                st.write("Download the video file:")
                with open(video_file, "rb") as file:
                    btn = st.download_button(label="Download video file", 
                                             data=file, 
                                             file_name="downloaded_video.mp4", 
                                             mime="video/mp4")
        except ValueError as ve:
            st.write(str(ve))
        except Exception as e:
            st.write(f"An error occurred: {e}")
    else:
        st.write("Please enter a valid YouTube URL")

# Download audio button
if st.button("Download Audio", key="download_audio_button", help="Click to download the audio of the YouTube video"):
    if video_url:
        try:
            st.write("Downloading audio...")
            audio_file = download_audio_from_youtube(video_url)
            
            if audio_file:
                # Provide download link for the audio file
                st.write("Download the audio file:")
                with open(audio_file, "rb") as file:
                    btn = st.download_button(label="Download audio file", 
                                             data=file, 
                                             file_name="downloaded_audio.mp4", 
                                             mime="audio/mp4")
        except Exception as e:
            st.write(f"An error occurred: {e}")
    else:
        st.write("Please enter a valid YouTube URL")

# Transcribe audio button
if st.button("Transcribe Audio", key="transcribe_audio_button", help="Click to transcribe the audio of the YouTube video"):
    if video_url:
        try:
            st.write("Downloading audio for transcription...")
            audio_file = download_audio_from_youtube(video_url)
            
            if audio_file:
                with st.spinner("Transcribing audio..."):
                    transcription_result = transcribe_audio(audio_file)
                
                if 'text' in transcription_result:
                    st.write("Transcription:")
                    st.write(transcription_result['text'])
                else:
                    st.write("Error in transcription:")
                    st.write(transcription_result)
        except Exception as e:
            st.write(f"An error occurred: {e}")
    else:
        st.write("Please enter a valid YouTube URL")

# Add CSS for styling buttons
st.markdown("""
    <style>
    .stButton > button {
        background: linear-gradient(45deg, #FF6F61, #FFB399, #FFD700, #32CD32, #87CEEB, #9370DB);
        background-size: 600% 600%;
        color: white;
        padding: 14px 20px;
        margin: 8px 0;
        border: none;
        cursor: pointer;
        width: 100%;
        opacity: 0.9;
        transition: all 0.5s ease;
        animation: gradient 5s ease infinite;
    }
    .stButton > button:hover {
        opacity: 1;
        transform: scale(1.05);
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
    """, unsafe_allow_html=True)
