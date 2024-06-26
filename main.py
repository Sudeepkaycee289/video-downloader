import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.ttk import Progressbar
from pytube import YouTube
from moviepy.editor import AudioFileClip
from datetime import timedelta
import threading
import subprocess

HISTORY_FILE = "download_history.json"

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube to MP3/MP4 Downloader")
        self.root.geometry("700x500")

        self.history = self.load_history()  # Load history from file

        # Create GUI layout
        self.create_layout()

    def create_layout(self):
        # Navigation buttons
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(side=tk.TOP, fill=tk.X)

        self.main_btn = tk.Button(nav_frame, text="Main", command=self.show_main)
        self.main_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.history_btn = tk.Button(nav_frame, text="History", command=self.show_history)
        self.history_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.download_btn = tk.Button(nav_frame, text="Downloading", command=self.show_download)
        self.download_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.about_btn = tk.Button(nav_frame, text="About Us", command=self.show_about)
        self.about_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.contact_btn = tk.Button(nav_frame, text="Contact Us", command=self.show_contact)
        self.contact_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        tk.Label(self.main_frame, text="YouTube URL:").pack(pady=5)
        self.url_entry = tk.Entry(self.main_frame, width=50)
        self.url_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Save Location:").pack(pady=5)
        self.save_location_entry = tk.Entry(self.main_frame, width=50)
        self.save_location_entry.pack(pady=5)
        tk.Button(self.main_frame, text="Browse", command=self.browse_save_location).pack(pady=5)

        tk.Label(self.main_frame, text="Select Format:").pack(pady=5)
        self.format_var = tk.StringVar(value="MP3")
        tk.OptionMenu(self.main_frame, self.format_var, "MP3", "MP4").pack(pady=5)

        tk.Button(self.main_frame, text="Download", command=self.download_thread).pack(pady=20)

        # Downloading frame
        self.download_frame = tk.Frame(self.root)
        tk.Label(self.download_frame, text="Downloading", font=('Helvetica', 16, 'bold')).pack(pady=5)
        self.progressbar = Progressbar(self.download_frame, orient="horizontal", length=300, mode="determinate")
        self.progressbar.pack(pady=20)

        # History frame
        self.history_frame = tk.Frame(self.root)

        tk.Label(self.history_frame, text="Download History", font=('Helvetica', 16, 'bold')).pack(pady=5)
        self.history_table = ttk.Treeview(self.history_frame, columns=("Filename", "YouTube Link", "Duration"), show='headings')
        self.history_table.heading("Filename", text="Filename")
        self.history_table.heading("YouTube Link", text="YouTube Link")
        self.history_table.heading("Duration", text="Duration")
        self.history_table.pack(fill=tk.BOTH, expand=1)
        self.update_history()

        # About frame
        self.about_frame = tk.Frame(self.root)

        tk.Label(self.about_frame, text="About Us", font=('Helvetica', 16, 'bold')).pack(pady=5)
        tk.Label(self.about_frame, text=("This application allows you to download YouTube videos and convert them to MP3 or MP4 format. "
                                         "It is developed using Python and Tkinter for the GUI, Pytube for downloading videos, and MoviePy for converting videos to audio."), wraplength=600).pack(pady=5)

        # Contact frame
        self.contact_frame = tk.Frame(self.root)

        tk.Label(self.contact_frame, text="Contact Us", font=('Helvetica', 16, 'bold')).pack(pady=5)
        tk.Label(self.contact_frame, text="For any inquiries, please contact us at: sudipkc289@gmail.com", wraplength=600).pack(pady=5)

        # Initially show main frame
        self.show_main()

    def show_main(self):
        self.hide_frames()
        self.main_frame.pack(fill=tk.BOTH, expand=1)

    def show_history(self):
        self.hide_frames()
        self.history_frame.pack(fill=tk.BOTH, expand=1)
        self.update_history()

    def show_download(self):
        self.hide_frames()
        self.download_frame.pack(fill=tk.BOTH, expand=1)

    def show_about(self):
        self.hide_frames()
        self.about_frame.pack(fill=tk.BOTH, expand=1)

    def show_contact(self):
        self.hide_frames()
        self.contact_frame.pack(fill=tk.BOTH, expand=1)

    def hide_frames(self):
        self.main_frame.pack_forget()
        self.history_frame.pack_forget()
        self.about_frame.pack_forget()
        self.contact_frame.pack_forget()
        self.download_frame.pack_forget()

    def browse_save_location(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.save_location_entry.delete(0, tk.END)
            self.save_location_entry.insert(0, folder_selected)

    def download_thread(self):
        url = self.url_entry.get()
        save_location = self.save_location_entry.get()
        file_format = self.format_var.get()
        threading.Thread(target=self.download, args=(url, save_location, file_format)).start()

    def download(self, url, save_location, file_format):
        if not url:
            messagebox.showwarning("Warning", "Please enter a YouTube URL")
            return

        if not save_location:
            messagebox.showwarning("Warning", "Please select a save location")
            return

        self.root.after(0, self.show_download)
        self.progressbar['value'] = 0

        try:
            yt = YouTube(url, on_progress_callback=self.progress_callback)
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
            self.history.insert(0, (os.path.basename(final_file), url, duration))
            self.save_history()  # Save the updated history

            messagebox.showinfo("Success", f"Downloaded and converted to {file_format}: {final_file}")
            self.update_history()
            self.root.after(0, self.show_main)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            self.root.after(0, self.show_main)

    def progress_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 100
        print (percentage_of_completion)
        self.progressbar['value'] = percentage_of_completion

    def update_history(self):
        for row in self.history_table.get_children():
            self.history_table.delete(row)
        for item in self.history:
            self.history_table.insert('', tk.END, values=item)

    def save_history(self):
        # Save the history to a JSON file
        with open(HISTORY_FILE, "w") as f:
            json.dump(self.history, f)

    def load_history(self):
        # Load the history from the JSON file if it exists
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        return []

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

if __name__ == "__main__":
    if not check_ffmpeg():
        messagebox.showerror("Error", "FFmpeg is not installed or not found in PATH. Please install FFmpeg and try again.")
    else:
        root = tk.Tk()
        app = YouTubeDownloaderApp(root)
        root.mainloop()
