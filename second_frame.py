import tkinter as tk
from tkinter import ttk, messagebox
import json

class SecondFrame:
    def __init__(self, root, calibration_list, message_text, publisher_callback, switch_frame_callback):
        self.root = root
        self.root.title("Calibration List")
        self.publisher_callback = publisher_callback
        self.switch_frame_callback = switch_frame_callback
        self.selected_tests = []

        # Main container
        self.container = ttk.Frame(root)
        self.container.grid(row=0, column=0, padx=10, pady=10)

        # Left side: Calibration list with checkboxes
        self.frame_left = ttk.Frame(self.container)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10)

        self.label = ttk.Label(self.frame_left, text="Select Calibration Tests:")
        self.label.grid(row=0, column=0, padx=5, pady=5)

        # Frame for checkboxes
        self.checkbox_frame = ttk.Frame(self.frame_left)
        self.checkbox_frame.grid(row=1, column=0, padx=5, pady=5)

        self.var_dict = {}
        for i, test in enumerate(calibration_list):
            var = tk.BooleanVar()
            self.var_dict[test] = var
            cb = ttk.Checkbutton(self.checkbox_frame, text=test, variable=var)
            cb.grid(row=i, column=0, sticky='w')

        self.next_button = ttk.Button(self.frame_left, text="Next", command=self.on_next_click)
        self.next_button.grid(row=2, column=0, pady=10)

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

    def on_next_click(self):
        self.selected_tests = [test for test, var in self.var_dict.items() if var.get()]
        if self.selected_tests:
            self.publisher_callback("eject_tray")
        else:
            messagebox.showwarning("Warning", "Please select at least one test.")

    def display_message(self, subject, message):
        self.messages_text.configure(state="normal")
        self.messages_text.insert("end", f"Subject: {subject}\nMessage: {message}\n\n")
        self.messages_text.configure(state="disabled")
        self.messages_text.see("end")

        try:
            message_data = json.loads(message)
            if message_data.get("type") == "eject_tray":
                status = message_data.get("data", {}).get("status")
                if status == "success":
                    self.switch_frame_callback("third", self.selected_tests, message)
                else:
                    messagebox.showerror("Error", "Tray ejection failed. Please try again.")
        except json.JSONDecodeError:
            pass
