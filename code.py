import streamlit as st
import requests
from pytube import YouTube
import os
import time

# Function to download audio from YouTube video
def download_audio_from_youtube(video_url, output_path="audio.mp4"):
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_stream.download(filename=output_path)
    return output_path

# Function to download video from YouTube
def download_video_from_youtube(video_url, output_path="video.mp4"):
    yt = YouTube(video_url)
    video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    video_stream.download(filename=output_path)
    return output_path

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
st.set_page_config(page_title="YouTube Video Transcription",
                   page_icon='🎥',
                   layout='centered',
                   initial_sidebar_state='expanded')

# Sidebar configuration
st.sidebar.title("About the App")
st.sidebar.info(
    """
    This app allows you to transcribe the audio of a YouTube video using the Whisper model.
    - Enter the YouTube video URL
    - Download the audio
    - Transcribe the audio to text

    **Note:** The transcription process may take some time depending on the length of the audio and server load.
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    **Developed by DP**
    """
)

st.header("YouTube Video Transcription 🎥")

# Input field for YouTube URL
video_url = st.text_input("Enter the YouTube Video URL")

# Download video button
if st.button("Download Video", key="download_video_button", help="Click to download the YouTube video"):
    if video_url:
        try:
            st.write("Downloading video...")
            video_file = download_video_from_youtube(video_url)
            
            # Provide download link for the video file
            st.write("Download the video file:")
            with open(video_file, "rb") as file:
                btn = st.download_button(label="Download video file", 
                                         data=file, 
                                         file_name="downloaded_video.mp4", 
                                         mime="video/mp4")
        except Exception as e:
            st.write(f"An error occurred: {e}")
    else:
        st.write("Please enter a valid YouTube URL")

# Submit button for transcription
if st.button("Transcribe", key="transcribe_button", help="Click to transcribe the YouTube video"):
    if video_url:
        try:
            st.write("Downloading audio...")
            audio_file = download_audio_from_youtube(video_url)
            
            with st.spinner("Transcribing audio..."):
                transcription_result = transcribe_audio(audio_file)
            
            if 'text' in transcription_result:
                st.write("Transcription:")
                st.write(transcription_result['text'])
            else:
                st.write("Error in transcription:")
                st.write(transcription_result)
            
            # Provide download link for the audio file
            st.write("Download the audio file:")
            with open(audio_file, "rb") as file:
                btn = st.download_button(label="Download audio file", 
                                         data=file, 
                                         file_name="transcribed_audio.mp4", 
                                         mime="audio/mp4")
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
