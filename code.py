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

# Function to download video from YouTube and convert to compatible format
def download_video_from_youtube(video_url, quality, output_path="video.mp4"):
    yt = YouTube(video_url)
    
    video_stream = None
    if quality == 'Low':
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first()
    elif quality == 'High (1080p)':
        video_stream = yt.streams.filter(file_extension='mp4', res="1080p").first()
        if not video_stream:
            st.write("1080p not available, trying 720p...")
            video_stream = yt.streams.filter(file_extension='mp4', res="720p").first()
        if not video_stream:
            st.write("720p not available, trying highest available resolution...")
            video_stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()

    if video_stream:
        downloaded_path = video_stream.download(filename=output_path)
        return downloaded_path
    else:
        raise ValueError(f"Unable to download video at the selected quality: {quality}")

# Streamlit configuration
st.set_page_config(page_title="YouTube Video Downloader",
                   page_icon='🎥',
                   layout='centered',
                   initial_sidebar_state='expanded')

# Sidebar configuration
st.sidebar.title("About the App")
st.sidebar.info(
    """
    This app allows you to download the audio or video of a YouTube video.
    - Enter the YouTube video URL
    - Download the audio or video

    **Note:** The download process may take some time depending on the length of the video and server load.
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    **Developed by DP**
    """
)

st.header("YouTube Video Downloader 🎥")

# Input field for YouTube URL
video_url = st.text_input("Enter the YouTube Video URL")

# Dropdown menu for selecting video quality
video_quality = st.selectbox(
    "Select Video Quality",
    ("Low", "High (1080p)")
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
