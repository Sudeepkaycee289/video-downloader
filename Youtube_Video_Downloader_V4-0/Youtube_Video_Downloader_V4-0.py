import os
import json
import PySimpleGUI as sg
from pytube import YouTube
from moviepy.editor import AudioFileClip
from datetime import timedelta
import threading
import subprocess
import tkthread  # Import tkthread

HISTORY_FILE = "download_history.json"

class YouTubeDownloaderApp:
    def __init__(self):
        self.history = self.load_history()  # Load history from file
        self.layout = self.create_layout()  # Create the GUI layout
        self.window = sg.Window("YouTube to MP3/MP4 Downloader", self.layout, size=(700, 500))
        tkthread.call(self.run)  # Run the main event loop within tkthread context

    def create_layout(self):
        sg.theme('DarkBlue3')  # Use a modern theme

        # Navigation buttons
        nav_buttons = [
            sg.Button("Main", key="Main", size=(10, 1)),
            sg.Button("History", key="History", size=(10, 1)),
            sg.Button("Downloading", key="Downloading", size=(10, 1)),
            sg.Button("About Us", key="About", size=(10, 1)),
            sg.Button("Contact Us", key="Contact", size=(10, 1))
    
        ]

        # Main frame layout
        main_layout = [
            [sg.Text("YouTube URL:")],
            [sg.InputText(key="url")],
            [sg.Text("Save Location:")],
            [sg.InputText(key="save_location"), sg.FolderBrowse()],
            [sg.Text("Select Format:")],
            [sg.Combo(["MP3", "MP4"], default_value="MP3", key="format")],  # Dropdown to select format
            [sg.Button("Download", key="Download")]
        ]

        # History frame layout
        history_layout = [
            [sg.Text("Download History", font=('Helvetica', 16, 'bold'))],
            [sg.Table(values=self.history, headings=["Filename", "YouTube Link", "Duration"], auto_size_columns=True, key="history_table", num_rows=10)]
        ]

        # Downloading progress layout
        downloading_layout = [
            [sg.Text("Downloading Progress", font=('Helvetica', 16, 'bold'))],
            [sg.ProgressBar(100, orientation='h', size=(20, 20), key='progress_bar')]
        ]

        # About frame layout
        about_layout = [
            [sg.Text("About Us", font=('Helvetica', 16, 'bold'))],
            [sg.Text("This application allows you to download YouTube videos and convert them to MP3 or MP4 format. "
                     "It is developed using Python and PySimpleGUI for the GUI, Pytube for downloading videos, and MoviePy for converting videos to audio.", size=(60, 10))]
        ]

        # Contact frame layout
        contact_layout = [
            [sg.Text("Contact Us", font=('Helvetica', 16, 'bold'))],
            [sg.Text("For any inquiries, please contact us at: sudipkc289@gmail.com", size=(60, 3))]
        ]

        # Combine all layouts into a dictionary for easy frame switching
        frames = {
            "Main": main_layout,
            "History": history_layout,
            "Downloading": downloading_layout,
            "About": about_layout,
            "Contact": contact_layout
        }

        # Full layout
        layout = [
            nav_buttons,
            [sg.Column(frames["Main"], key="Main_frame", visible=True),
             sg.Column(frames["History"], key="History_frame", visible=False),
             sg.Column(frames["Downloading"], key="Downloading_frame", visible=False),
             sg.Column(frames["About"], key="About_frame", visible=False),
             sg.Column(frames["Contact"], key="Contact_frame", visible=False)]
        ]

        return layout

    def run(self):
        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED:
                break

            if event in ["Main", "History", "Downloading", "About", "Contact"]:
                self.show_frame(event)

            if event == "Download":
                url = values["url"]
                save_location = values["save_location"]
                file_format = values["format"]
                self.download_thread(url, save_location, file_format)

        self.window.close()

    def show_frame(self, frame_name):
        frames = ["Main", "History","Downloading", "About", "Contact"]
        for frame in frames:
            self.window[f"{frame}_frame"].update(visible=(frame == frame_name))

        if frame_name == "History":
            self.update_history()

    def download_thread(self, url, save_location, file_format):
        # Use a thread to avoid blocking the UI during download
        threading.Thread(target=self.download, args=(url, save_location, file_format)).start()

    def download(self, url, save_location, file_format):
        if not url:
            tkthread.call(sg.popup_warning, "Please enter a YouTube URL")  # Ensure popup runs in main thread
            return

        if not save_location:
            tkthread.call(sg.popup_warning, "Please select a save location")  # Ensure popup runs in main thread
            return

        try:
            yt = YouTube(url)
            
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

            tkthread.call(sg.popup, "Success", f"Downloaded and converted to {file_format}: {final_file}")  # Ensure popup runs in main thread
            tkthread.call(self.update_history)  # Ensure history update runs in main thread
        except Exception as e:
            tkthread.call(sg.popup_error, f"Error: {str(e)}")  # Ensure popup runs in main thread

    def update_history(self):
        history_data = self.history
        self.window["history_table"].update(values=history_data)

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
        sg.popup_error("FFmpeg is not installed or not found in PATH. Please install FFmpeg and try again.")
    else:
        YouTubeDownloaderApp()
