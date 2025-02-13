import tkinter as tk
from tkinter import ttk, messagebox
import json

class App:
    def __init__(self, root, publisher_callback, switch_frame_callback):
        self.root = root
        self.root.title("MAINTENANCE DUMMY UI")
        self.publisher_callback = publisher_callback
        self.switch_frame_callback = switch_frame_callback

        # Left side: Button to show calibration list
        self.frame_left = ttk.Frame(root)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10)

        self.show_calibration_button = ttk.Button(self.frame_left, text="Show Calibration List", 
                                                command=self.show_calibration_list)
        self.show_calibration_button.grid(row=0, column=0, columnspan=2, pady=5)

        # Right side: Message display
        self.frame_right = ttk.Frame(root)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.messages_label = ttk.Label(self.frame_right, text="Received Messages:")
        self.messages_label.grid(row=0, column=0, padx=5, pady=5)

        self.messages_text = tk.Text(self.frame_right, width=50, height=20, state="disabled", wrap="word")
        self.messages_text.grid(row=1, column=0, padx=5, pady=5)

        self.scrollbar = ttk.Scrollbar(self.frame_right, command=self.messages_text.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        self.messages_text.configure(yscrollcommand=self.scrollbar.set)

    def show_calibration_list(self):
        self.publisher_callback("get_calibration_list")

    def display_message(self, subject, message):
        self.messages_text.configure(state="normal")
        self.messages_text.insert("end", f"Subject: {subject}\nMessage: {message}\n\n")
        self.messages_text.configure(state="disabled")
        self.messages_text.see("end")

        try:
            message_data = json.loads(message)
            if message_data.get("type") == "get_calibration_list":
                calibration_list = message_data["data"].get("calibration_test_list", [])
                self.switch_frame_callback("second", calibration_list, message)
        except json.JSONDecodeError:
            pass