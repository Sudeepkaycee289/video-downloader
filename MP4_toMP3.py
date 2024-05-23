import os
from pytube import YouTube
from moviepy.editor import AudioFileClip
import tkinter as tk
from tkinter import filedialog, messagebox

def download_mp3():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a YouTube URL")
        return
    
    try:
        # Download the video
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        download_path = filedialog.askdirectory()
        out_file = video.download(output_path=download_path)
        
        # Convert the video to mp3
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        audio_clip = AudioFileClip(out_file)
        audio_clip.write_audiofile(new_file)
        audio_clip.close()
        
        # Remove the original video file
        os.remove(out_file)
        
        messagebox.showinfo("Success", f"Downloaded and converted to MP3: {new_file}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Setup GUI
root = tk.Tk()
root.title("YouTube to MP3 Downloader")

tk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

download_button = tk.Button(root, text="Download as MP3", command=download_mp3)
download_button.pack(pady=20)

root.mainloop()
