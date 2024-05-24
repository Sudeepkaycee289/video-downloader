import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pytube import YouTube
from moviepy.editor import AudioFileClip
from datetime import datetime,timedelta
import subprocess
import threading

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube to MP3 Downloader")
        self.root.geometry("700x500")

        self.history = []

        self.create_nav_frame()
        self.frames = {}

        self.create_main_frame()
        self.create_history_frame()
        self.create_about_frame()
        self.create_contact_frame()

        self.show_frame("Main")

    def create_nav_frame(self):
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(side=tk.TOP, fill=tk.X)
        
        main_button = tk.Button(nav_frame, text="Main", command=lambda: self.show_frame("Main"))
        main_button.pack(side=tk.LEFT, padx=10, pady=10)

        history_button = tk.Button(nav_frame, text="History", command=lambda: self.show_frame("History"))
        history_button.pack(side=tk.LEFT, padx=10, pady=10)

        about_button = tk.Button(nav_frame, text="About Us", command=lambda: self.show_frame("About"))
        about_button.pack(side=tk.LEFT, padx=10, pady=10)

        contact_button = tk.Button(nav_frame, text="Contact Us", command=lambda: self.show_frame("Contact"))
        contact_button.pack(side=tk.LEFT, padx=10, pady=10)

    def create_main_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill="both")
        
        container = tk.Frame(frame)
        container.pack(pady=20)

        tk.Label(container, text="YouTube URL:").pack(pady=5)
        self.url_entry = tk.Entry(container, width=60)
        self.url_entry.pack(pady=5)

        tk.Label(container, text="Save Location:").pack(pady=5)
        location_frame = tk.Frame(container)
        location_frame.pack(pady=5)
        self.location_entry = tk.Entry(location_frame, width=40)
        self.location_entry.pack(side=tk.LEFT, padx=(20, 0))

        browse_button = tk.Button(location_frame, text="Browse", command=self.browse_location)
        browse_button.pack(side=tk.LEFT)

        download_button = tk.Button(container, text="Download as MP3", command=self.download_mp3_thread)
        download_button.pack(pady=10)

        self.frames["Main"] = frame

    def create_history_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill="both")
        
        tk.Label(frame, text="Download History", font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        columns = ("filename", "youtube_link", "duration")
        self.treeview = ttk.Treeview(frame, columns=columns, show="headings")
        self.treeview.heading("filename", text="Filename")
        self.treeview.heading("youtube_link", text="YouTube Link")
        self.treeview.heading("duration", text="Duration")
        self.treeview.pack(pady=20, fill=tk.BOTH, expand=True)
        
        self.update_history()

        self.frames["History"] = frame

    def create_about_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill="both")
        
        tk.Label(frame, text="About Us", font=('Helvetica', 16, 'bold')).pack(pady=10)
        about_text = """This application allows you to download YouTube videos and convert them to MP3 format.
        It is developed using Python and Tkinter for the GUI, Pytube for downloading videos, and MoviePy for converting videos to audio."""
        tk.Label(frame, text=about_text, wraplength=600, justify=tk.LEFT).pack(pady=10)

        self.frames["About"] = frame

    def create_contact_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill="both")
        
        tk.Label(frame, text="Contact Us", font=('Helvetica', 16, 'bold')).pack(pady=10)
        contact_text = "For any inquiries, please contact us at: sudipkc289@gmail.com"
        tk.Label(frame, text=contact_text, wraplength=600, justify=tk.LEFT).pack(pady=10)

        self.frames["Contact"] = frame
    
    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

        # Ensure all frames are properly packed
        for f in self.frames.values():
            f.pack_forget()
        frame.pack(expand=True, fill="both")

    def browse_location(self):
        download_path = filedialog.askdirectory()
        if download_path:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, download_path)
    
    def download_mp3_thread(self):
        # Use a thread to avoid blocking the UI
        threading.Thread(target=self.download_mp3).start()

    def download_mp3(self):
        url = self.url_entry.get()
        save_location = self.location_entry.get()
        
        if not url:
            messagebox.showwarning("Input Error", "Please enter a YouTube URL")
            return
        
        if not save_location:
            messagebox.showwarning("Input Error", "Please select a save location")
            return
        
        try:
            yt = YouTube(url)
            video = yt.streams.filter(only_audio=True).first()
            out_file = video.download(output_path=save_location)
            
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            audio_clip = AudioFileClip(out_file)
            audio_clip.write_audiofile(new_file)
            audio_clip.close()
            
            os.remove(out_file)
            
            duration = str(timedelta(seconds=int(yt.length)))
            self.history.append((os.path.basename(new_file), url, duration))
            
            self.update_history()
            
            messagebox.showinfo("Success", f"Downloaded and converted to MP3: {new_file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_history(self):
        for row in self.treeview.get_children():
            self.treeview.delete(row)
        for record in self.history:
            self.treeview.insert("", "end", values=record)

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

if __name__ == "__main__":
    if not check_ffmpeg():
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("FFmpeg Error", "FFmpeg is not installed or not found in PATH. Please install FFmpeg and try again.")
    else:
        root = tk.Tk()
        app = YouTubeDownloaderApp(root)
        root.mainloop()
