import os
import tkinter as tk
from tkinter import messagebox
from pytube import YouTube
from moviepy.editor import AudioFileClip
from datetime import timedelta
from history import save_history

def download_thread(url, save_location, file_format, app):
    if not url:
        messagebox.showwarning("Warning", "Please enter a YouTube URL")
        return

    if not save_location:
        messagebox.showwarning("Warning", "Please select a save location")
        return

    app.root.after(0, app.show_download)
    app.progressbar['value'] = 0

    try:
        yt = YouTube(url, on_progress_callback=lambda stream, chunk, bytes_remaining: progress_callback(stream, chunk, bytes_remaining, app))
        
        song_name = yt.title
        app.song_name_label.config(text=f"Song Name: {song_name}")
        app.file_format_label.config(text=f"File Format: {file_format}")
        app.file_size_label.config(text="File Size: Calculating...")

        if file_format == "MP3":
            video = yt.streams.filter(only_audio=True).first()
            out_file = video.download(output_path=save_location)

            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            audio_clip = AudioFileClip(out_file)
            audio_clip.write_audiofile(new_file)
            audio_clip.close()

            os.remove(out_file)
            final_file = new_file

        elif file_format == "MP4":
            video = yt.streams.get_highest_resolution()
            final_file = video.download(output_path=save_location)

        file_size = os.path.getsize(final_file) / (1024 * 1024)  # Convert size to MB
        app.file_size_label.config(text=f"File Size: {file_size:.2f} MB")

        duration = str(timedelta(seconds=int(yt.length)))
        app.history.insert(0, (os.path.basename(final_file), url, duration))
        save_history(app.history)  # Save the updated history

        messagebox.showinfo("Success", f"Downloaded and converted to {file_format}: {final_file}")
        app.update_history()
        app.root.after(0, app.show_main)
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        app.root.after(0, app.show_main)

def progress_callback(stream, chunk, bytes_remaining, app):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    app.progressbar['value'] = percentage_of_completion
