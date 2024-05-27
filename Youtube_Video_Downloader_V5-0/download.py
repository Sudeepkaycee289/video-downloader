import os
import tkinter as tk
from tkinter import messagebox
from pytube import YouTube
from moviepy.editor import AudioFileClip
from datetime import timedelta
from history import save_history

def download_thread(url, save_location, file_format, root, progressbar, history):
    if not url:
        messagebox.showwarning("Warning", "Please enter a YouTube URL")
        return

    if not save_location:
        messagebox.showwarning("Warning", "Please select a save location")
        return

    root.after(0, lambda: show_download(root, progressbar))
    progressbar['value'] = 0

    try:
        yt = YouTube(url, on_progress_callback=lambda stream, chunk, bytes_remaining: progress_callback(stream, chunk, bytes_remaining, progressbar))
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

        duration = str(timedelta(seconds=int(yt.length)))
        history.insert(0, (os.path.basename(final_file), url, duration))
        save_history(history)  # Save the updated history

        messagebox.showinfo("Success", f"Downloaded and converted to {file_format}: {final_file}")
        root.after(0, lambda: show_main(root))
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        root.after(0, lambda: show_main(root))

def progress_callback(stream, chunk, bytes_remaining, progressbar):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    progressbar['value'] = percentage_of_completion

def show_download(root, progressbar):
    progressbar['value'] = 0
    for widget in root.winfo_children():
        widget.pack_forget()
    for widget in root.winfo_children():
        widget.pack()
    root.update_idletasks()

def show_main(root):
    for widget in root.winfo_children():
        widget.pack_forget()
    for widget in root.winfo_children():
        widget.pack()
    root.update_idletasks()
