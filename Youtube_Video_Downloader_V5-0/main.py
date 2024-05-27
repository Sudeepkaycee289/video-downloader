import tkinter as tk
from tkinter import messagebox
from gui import YouTubeDownloaderApp
from utilities import check_ffmpeg

if __name__ == "__main__":
    if not check_ffmpeg():
        messagebox.showerror("Error", "FFmpeg is not installed or not found in PATH. Please install FFmpeg and try again.")
    else:
        root = tk.Tk()
        app = YouTubeDownloaderApp(root)
        root.mainloop()
