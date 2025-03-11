import tkinter as tk
from tkinter import messagebox
import json

class FirstScreen(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.master = master

        # Main title
        self.label = tk.Label(self, text="Maintenance UI", font=("Arial", 16))
        self.label.pack(pady=20)

        # Create buttons
        self.calibration_button = tk.Button(self, text="Open Calibration", command=self.open_calibration)
        self.calibration_button.pack(pady=10)
        
        # Add message log area
        self.log_label = tk.Label(self, text="Message Log:", anchor="w")
        self.log_label.pack(fill=tk.X, padx=10, pady=(20, 5))
        
        # Create text widget with scrollbar for log
        self.log_frame = tk.Frame(self)
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.message_log = tk.Text(self.log_frame, height=10, width=60, wrap=tk.WORD)
        self.message_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = tk.Scrollbar(self.log_frame, command=self.message_log.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_log.config(yscrollcommand=self.scrollbar.set)
        
        # Make text widget read-only
        self.message_log.config(state=tk.DISABLED)

    def open_calibration(self):
        """Open calibration screen and send appropriate NATS message"""
        full_command = self.master.send_command(
            "open_calibration", 
            "data.sv-maintenance.commands"
        )
        
        if full_command:
            timestamp = self.master.get_timestamp() if hasattr(self.master, 'get_timestamp') else "N/A"
            self.log_message(f"[{timestamp}] SENT: {json.dumps(full_command, indent=2)}")
        else:
            messagebox.showerror("Error", "Failed to send calibration command. NATS not connected.")
            self.log_message("[ERROR] Failed to send command - NATS not connected")
    
    def log_message(self, message):
        """Add a message to the log box"""
        self.message_log.config(state=tk.NORMAL)
        if self.message_log.get("1.0", tk.END) != "\n":
            self.message_log.insert(tk.END, "\n")
        self.message_log.insert(tk.END, message)
        self.message_log.see(tk.END)
        self.message_log.config(state=tk.DISABLED)

    def on_event_message(self, message):
        """Handle incoming event message"""
        try:
            timestamp = self.master.get_timestamp()
            self.log_message(f"[{timestamp}] RECEIVED: {json.dumps(message, indent=2)}")

            if message.get("type") == "get_calibration_list":
                # messagebox.showinfo("Info", "Calibration completed successfully!")
                # ✅ Switch to SecondScreen
                self.master.show_screen("SecondScreen", event_data=message)
        except Exception as e:
            print(f"Error handling event in FirstScreen: {e}")
