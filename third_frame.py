
import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid

class ThirdFrame:
    def __init__(self, root, selected_tests, message_text, publisher_callback):
        self.root = root
        self.root.title("Start Calibration")
        self.selected_tests = selected_tests
        self.publisher_callback = publisher_callback

        # Main container
        self.container = ttk.Frame(root)
        self.container.grid(row=0, column=0, padx=10, pady=10)

        # Left side: Instructions and start button
        self.frame_left = ttk.Frame(self.container)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10)

        self.label = ttk.Label(self.frame_left, text="Please insert the slide and press Start")
        self.label.grid(row=0, column=0, padx=5, pady=5)

        self.start_button = ttk.Button(self.frame_left, text="Start", command=self.on_start_click)
        self.start_button.grid(row=1, column=0, pady=10)

        # Right side: Message display
        self.frame_right = ttk.Frame(self.container)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10)

        self.messages_label = ttk.Label(self.frame_right, text="Received Messages:")
        self.messages_label.grid(row=0, column=0, padx=5, pady=5)

        self.messages_text = tk.Text(self.frame_right, width=50, height=20, state="disabled", wrap="word")
        self.messages_text.grid(row=1, column=0, padx=5, pady=5)
        self.messages_text.configure(state="normal")
        self.messages_text.insert("end", message_text)
        self.messages_text.configure(state="disabled")

    def on_start_click(self):
        message = {
            "id": str(uuid.uuid4()),
            "type": "start_calibration",
            "originator": "Device_store",
            "data": {
                "calibration_test_list": self.selected_tests,
                "job_id": str(uuid.uuid4())
            },
            "metadata": {
                "correlation_id": str(uuid.uuid4()),
                "timestamp": "2024-11-30T15:53:24:12Z",
                "trace_id": str(uuid.uuid4())
            }
        }
        self.publisher_callback("start_calibration", message)

    def display_message(self, subject, message):
        self.messages_text.configure(state="normal")
        self.messages_text.insert("end", f"Subject: {subject}\nMessage: {message}\n\n")
        self.messages_text.configure(state="disabled")
        self.messages_text.see("end")
