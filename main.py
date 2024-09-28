import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, OptionMenu
import threading
import webview
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import speech_recognition as sr
import os

# Function to extract audio from video
def extract_audio_from_video(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

# Function to convert audio to text
def audio_to_text(audio_path, language_code):
    recognizer = sr.Recognizer()
    wav_path = "temp_audio.wav"

    # Convert audio file to wav format if needed
    if audio_path.endswith('.mp3') or audio_path.endswith('.wav'):
        sound = AudioSegment.from_file(audio_path)
        sound.export(wav_path, format="wav")
    else:
        wav_path = audio_path

    try:
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language=language_code)
            return text
    except sr.UnknownValueError:
        return "Speech Recognition could not understand audio"
    except sr.RequestError:
        return "Could not request results; check your internet connection"
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

# Function to process video/audio files
def process_media(file_path, language_code):
    if file_path.endswith(('.mp4', '.mkv', '.avi')):
        audio_path = "extracted_audio.wav"
        extract_audio_from_video(file_path, audio_path)
        text = audio_to_text(audio_path, language_code)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return text
    elif file_path.endswith(('.mp3', '.wav')):
        return audio_to_text(file_path, language_code)
    else:
        return "Unsupported file format"

# Function to format subtitles in SRT format
def format_subtitles(text):
    subtitles = ""
    for i, line in enumerate(text.split('\n')):
        start_time = f"{i * 2:02d}:{(i * 2) % 60:02d}:00,000"
        end_time = f"{(i * 2) + 2:02d}:{((i * 2) + 2) % 60:02d}:00,000"
        subtitles += f"{i + 1}\n{start_time} --> {end_time}\n{line}\n\n"
    return subtitles

# Function to save subtitles to a file
def save_subtitles():
    if transcribed_text:
        subtitle_text = format_subtitles(transcribed_text)
        file_path = filedialog.asksaveasfilename(defaultextension=".srt", filetypes=[("Subtitle Files", "*.srt")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(subtitle_text)
            messagebox.showinfo("Saved", "Subtitles saved successfully.")
    else:
        messagebox.showwarning("No Text", "There are no subtitles to save.")

# Function to animate progress line
def animate_line():
    global line_x
    if processing:
        line_x += 5
        if line_x > canvas.winfo_width():
            line_x = 0
        canvas.delete("line")
        canvas.create_line(0, canvas.winfo_height() / 2, line_x, canvas.winfo_height() / 2, fill="#007BFF", width=2, tags="line")
        root.after(50, animate_line)

# Function to handle file selection and processing in a separate thread
def process_file_thread(file_path, language_code):
    global transcribed_text, processing
    processing = True
    animate_line()

    transcribed_text = process_media(file_path, language_code)
    
    processing = False
    canvas.delete("line")
    
    text_box.delete(1.0, tk.END)
    text_box.insert(tk.END, transcribed_text)

    if transcribed_text:
        messagebox.showinfo("Success", "Transcription complete.")
    else:
        messagebox.showerror("Error", "There was an error processing the file.")

def save_text():
    if transcribed_text:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(transcribed_text)
            messagebox.showinfo("Saved", "Text saved successfully.")
    else:
        messagebox.showwarning("No Text", "There is no text to save.")

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*"), ("Video Files", "*.mp4 *.mkv *.avi"), ("Audio Files", "*.mp3 *.wav")])
    if file_path:
        language_code = language_var.get()
        threading.Thread(target=process_file_thread, args=(file_path, language_code)).start()

# Function to open a web page in the PyWebview
def open_page(url):
    global webview_window
    if webview_window:
        webview_window.destroy()
    webview_window = webview.create_window("Webview", url, width=800, height=600)
    webview.start()

def open_about():
    open_page("https://dragonlanka.github.io/speech-to-text-about/")

def open_news():
    open_page("https://dragonlanka.github.io/speech-to-text-news/")

# Create the main application window
root = tk.Tk()
root.title("Speech-to-Text Tool")
root.geometry("1000x600")
root.minsize(800, 600)
root.configure(bg='#f5f5f5')

# Create a main frame and a side menu frame
main_frame = tk.Frame(root, bg='#ffffff')
main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

menu_frame = tk.Frame(root, bg='#007BFF', width=200)
menu_frame.pack(side=tk.LEFT, fill=tk.Y)

# Side menu
tk.Label(menu_frame, text="Menu", bg='#007BFF', fg='#ffffff', font=('Arial', 18, 'bold')).pack(pady=20)
tk.Button(menu_frame, text="About", command=open_about, bg='#0056b3', fg='#ffffff', font=('Arial', 14), relief=tk.RAISED, padx=10, pady=10).pack(pady=10, fill=tk.X)
tk.Button(menu_frame, text="News", command=open_news, bg='#0056b3', fg='#ffffff', font=('Arial', 14), relief=tk.RAISED, padx=10, pady=10).pack(pady=10, fill=tk.X)

# Create and place widgets in the main frame using grid layout
label = tk.Label(main_frame, text="Select a video or audio file:", font=('Arial', 16, 'bold'), bg='#ffffff')
label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky='w')

# Language selection
language_var = StringVar(root)
language_var.set('en-US')  # Default to English
language_menu = OptionMenu(main_frame, language_var, 'en-US', 'si-LK')
language_menu.config(font=('Arial', 14), bg='#ffffff', width=10)
language_menu.grid(row=1, column=0, pady=10, padx=10, sticky='w')

select_button = tk.Button(main_frame, text="Choose File", command=select_file, font=('Arial', 14), bg='#007BFF', fg='#ffffff', relief=tk.RAISED, padx=10, pady=10)
select_button.grid(row=1, column=1, pady=10, padx=10, sticky='w')

# Text box to display transcribed text
text_box = tk.Text(main_frame, wrap='word', height=15, width=80, font=('Arial', 12), bg='#f5f5f5', padx=10, pady=10)
text_box.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky='w')

# Save text and subtitles buttons
save_button = tk.Button(main_frame, text="Save Text", command=save_text, font=('Arial', 14), bg='#28a745', fg='#ffffff', relief=tk.RAISED, padx=10, pady=10)
save_button.grid(row=3, column=0, pady=10, padx=10, sticky='w')

save_subtitles_button = tk.Button(main_frame, text="Save Subtitles", command=save_subtitles, font=('Arial', 14), bg='#17a2b8', fg='#ffffff', relief=tk.RAISED, padx=10, pady=10)
save_subtitles_button.grid(row=3, column=1, pady=10, padx=10, sticky='w')

# Canvas for animation
canvas = tk.Canvas(main_frame, bg='#ffffff', height=50)
canvas.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky='w')

line_x = 0
processing = False

# Create a webview window reference
webview_window = None

# Start the Tkinter event loop
root.mainloop()
