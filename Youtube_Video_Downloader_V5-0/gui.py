import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.ttk import Progressbar, Notebook
import threading
from download import download_thread
from history import load_history, save_history

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube to MP3/MP4 Downloader")
        self.root.geometry("700x500")

        self.history = load_history()  # Load history from file

        # Create GUI layout
        self.create_layout()

    def create_layout(self):
        # Navigation buttons
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(side=tk.TOP, fill=tk.X)

        self.main_btn = tk.Button(nav_frame, text="Home", command=self.show_main)
        self.main_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.download_btn = tk.Button(nav_frame, text="Downloads", command=self.show_download)
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

        # Downloading frame with Notebook
        self.download_frame = tk.Frame(self.root)
        self.notebook = Notebook(self.download_frame)

        # Current Downloads tab
        self.current_downloads_frame = tk.Frame(self.notebook)
        tk.Label(self.current_downloads_frame, text="Downloading", font=('Helvetica', 16, 'bold')).pack(pady=5)
        self.song_name_label = tk.Label(self.current_downloads_frame, text="Song Name: ", font=('Helvetica', 12))
        self.song_name_label.pack(pady=5)
        self.file_format_label = tk.Label(self.current_downloads_frame, text="File Format: ", font=('Helvetica', 12))
        self.file_format_label.pack(pady=5)
        self.file_size_label = tk.Label(self.current_downloads_frame, text="File Size: ", font=('Helvetica', 12))
        self.file_size_label.pack(pady=5)
        self.progressbar = Progressbar(self.current_downloads_frame, orient="horizontal", length=300, mode="determinate")
        self.progressbar.pack(pady=20)

        self.notebook.add(self.current_downloads_frame, text='Downloading')
        self.current_downloads_frame(side=tk.LEFT, padx=5, pady=5)

        # Download History tab
        self.history_frame = tk.Frame(self.notebook)
        tk.Label(self.history_frame, text="Download History", font=('Helvetica', 14, )).pack(pady=5)
        self.history_table = ttk.Treeview(self.history_frame, columns=("Filename", "YouTube Link", "Duration"), show='headings')
        self.history_table.heading("Filename", text="Filename")
        self.history_table.heading("YouTube Link", text="YouTube Link")
        self.history_table.heading("Duration", text="Duration")
        self.history_table.pack(fill=tk.BOTH, expand=1)
        self.update_history()

        self.notebook.add(self.history_frame, text='History')

        self.notebook.pack(fill=tk.BOTH, expand=1)
        self.download_frame.pack(fill=tk.BOTH, expand=1)

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
        threading.Thread(target=download_thread, args=(url, save_location, file_format, self)).start()

    def update_history(self):
        for row in self.history_table.get_children():
            self.history_table.delete(row)
        for item in self.history:
            self.history_table.insert('', tk.END, values=item)
