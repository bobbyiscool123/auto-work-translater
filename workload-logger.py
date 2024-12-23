import tkinter as tk
from tkinter import filedialog, messagebox
import google.generativeai as genai
from datetime import datetime
import os
from dotenv import load_dotenv
import re

load_dotenv()  # Load variables from .env file

# Get the Gemini API key from the environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Check if the API key is set
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not set in .env file.")
    exit()

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

# --- Color Palette ---
bg_color = "#f0f0f0"  # Light gray background
frame_bg = "#e0e0e0" # light gray background
button_bg = "#e0e0e0"  # Light gray for buttons
button_fg = "#333333"  # Dark gray for button text
button_hover = "#d0d0d0"  # Light gray for button hover
text_color = "#333333"  # Dark gray for text
entry_bg = "#ffffff" # White background for entry
entry_fg = "#000000" # Black foreground for entry
scroll_bg = "#d0d0d0" # Light gray for scrollbar
scroll_fg = "#333333" # Dark gray for scrollbar


def translate_to_console_style(text):
    """Translates the text to console-style log with Gemini."""
    try:
        prompt = f"""
            Translate the following text into a console-style log format that simulates git-like outputs for software project status updates. The output should maintain a tone of a command-line interface and should use similar words.
            
            Remove any triple backticks from the output. Remove any extra white space.

            Example Input:
              - Started working on the user authentication feature.
              - Implemented login functionality.
              - Testing the user login module.

            Example Output:
              [+] 2024-05-08 14:30:00: Started work on 'user authentication'.
              [+] 2024-05-08 14:45:00: Implemented login functionality.
              [*] 2024-05-08 15:15:00: Testing user login module.

            Input Text: {text}
            """
        
        response = model.generate_content(prompt)
        
        # Remove triple backticks and extra spaces, then return
        cleaned_text = re.sub(r'```\w*\n|```', '', response.text).strip()
        cleaned_text = ' '.join(cleaned_text.split())
        return cleaned_text
    except Exception as e:
        messagebox.showerror("Error", f"Error with Gemini API: {e}")
        return "Error in translation."


def save_log(log_text, file_path):
    try:
        with open(file_path, "a") as f:
            f.write(log_text + "\n")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error saving log: {e}")
        return False

def update_log():
    text = text_entry.get()
    if not text:
        messagebox.showerror("Error", "Please enter text to log.")
        return

    translated_text = translate_to_console_style(text)
    
    if translated_text == "Error in translation.":
        return

    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

    log_text = f"[{formatted_time}] {translated_text}"

    if not file_path:
          messagebox.showerror("Error", "Save a new file or select an existing file")
          return

    if save_log(log_text, file_path):
        log_display.insert(tk.END, log_text + '\n')
        text_entry.delete(0, tk.END)
    else:
         messagebox.showerror("Error", "Failed to update log file.")

def save_as_file():
    global file_path
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        update_file_label()

def change_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        update_file_label()

def update_file_label():
    file_label.config(text=f"Current File: {file_path}")

def on_button_enter(event):
    event.widget.config(bg=button_hover)

def on_button_leave(event):
    event.widget.config(bg=button_bg)

# --- GUI Setup ---
root = tk.Tk()
root.title("Gemini Workload Logger")
root.geometry("600x400")
root.configure(bg=bg_color, borderwidth=0)

# Variable to store the file path
file_path = None

# Input Frame
input_frame = tk.Frame(root, bg=frame_bg, borderwidth=0)
input_frame.pack(pady=10, padx=10, fill=tk.X)

tk.Label(input_frame, text="Enter Text to Update Workload:", bg=frame_bg, fg=text_color).pack(side=tk.LEFT)
text_entry = tk.Entry(input_frame, width=40, bg=entry_bg, fg=entry_fg, insertbackground=entry_fg, borderwidth=0)
text_entry.pack(side=tk.LEFT, padx=5)

update_button = tk.Button(input_frame, text="Update Log", bg=button_bg, fg=button_fg, borderwidth=0)
update_button.pack(side=tk.LEFT, padx=5)
update_button.bind("<Enter>", on_button_enter)
update_button.bind("<Leave>", on_button_leave)
update_button.config(command=update_log)

# File Frame
file_frame = tk.Frame(root, bg=frame_bg, borderwidth=0)
file_frame.pack(pady=10, padx=10, fill=tk.X)

file_label = tk.Label(file_frame, text="Current File: None", bg=frame_bg, fg=text_color)
file_label.pack(side=tk.LEFT, expand=True, fill=tk.X)

save_file_button = tk.Button(file_frame, text="Save as File", bg=button_bg, fg=button_fg, borderwidth=0)
save_file_button.pack(side=tk.LEFT, padx=5)
save_file_button.bind("<Enter>", on_button_enter)
save_file_button.bind("<Leave>", on_button_leave)
save_file_button.config(command=save_as_file)

change_file_button = tk.Button(file_frame, text="Change File", bg=button_bg, fg=button_fg, borderwidth=0)
change_file_button.pack(side=tk.LEFT, padx=5)
change_file_button.bind("<Enter>", on_button_enter)
change_file_button.bind("<Leave>", on_button_leave)
change_file_button.config(command=change_file)

# Log Display
log_frame = tk.Frame(root, bg=bg_color, borderwidth=0)
log_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

log_display = tk.Text(log_frame, height=15, wrap=tk.WORD, bg=bg_color, fg=text_color, borderwidth=0)
log_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(log_frame, command=log_display.yview, bg=scroll_bg, activebackground=scroll_fg)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_display.config(yscrollcommand=scrollbar.set)

root.mainloop()