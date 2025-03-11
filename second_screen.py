import tkinter as tk
from tkinter import messagebox
import uuid
import json

class SecondScreen(tk.Frame):
    def __init__(self, master, event_data=None, **kwargs):
        super().__init__(master)
        self.master = master
        self.event_data = event_data
        self.selected_tests = []

        # Title
        self.label = tk.Label(self, text="Select Calibration Tests", font=("Arial", 16))
        self.label.pack(pady=10)

        # Frame for scrolling
        self.scroll_frame = tk.Frame(self)
        self.scroll_frame.pack(fill="both", expand=True, pady=5)

        self.canvas = tk.Canvas(self.scroll_frame, height=300)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.inner_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.canvas.config(yscrollcommand=self.scrollbar.set)

        # Create checkboxes for calibration list
        self.checkbox_vars = {}
        if self.event_data and "data" in self.event_data:
            test_list = self.event_data["data"].get("calibration_test_list", [])
            for test in test_list:
                var = tk.BooleanVar()
                checkbox = tk.Checkbutton(
                    self.inner_frame, 
                    text=test, 
                    variable=var, 
                    anchor="w", 
                    justify="left"
                )
                checkbox.pack(fill="x", padx=10, pady=2)
                self.checkbox_vars[test] = var

        # Update canvas size dynamically
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.config(scrollregion=self.canvas.bbox("all")))

        # Next Button
        self.next_button = tk.Button(self, text="Next", command=self.on_next, bg="#4CAF50", fg="white", height=2, width=20)
        self.next_button.pack(pady=20)

    def on_next(self):
        """Handle next button click"""
        self.selected_tests = [test for test, var in self.checkbox_vars.items() if var.get()]
        if not self.selected_tests:
            messagebox.showwarning("Warning", "Please select at least one calibration test.")
            return
        
        # ✅ Send NATS Message
        command = {
            "id": str(uuid.uuid4()),
            "type": "position_tray_to_loading",
            "originator": "device_maintenance",
            "metadata": {
                "correlation_id": str(uuid.uuid4()),
                "timestamp": self.master.get_timestamp(),
                "trace_id": str(uuid.uuid4())
            },
            "data": {}
        }

        full_command = self.master.send_command(
            command["type"],
            "control.sv-maintenance.commands",
            command.get("data", {})
        )

        
        if full_command:
            print(f"Sent command: {json.dumps(full_command, indent=2)}")
            timestamp = self.master.get_timestamp()
            self.log_message(f"[{timestamp}] SENT: {json.dumps(full_command, indent=2)}")
        else:
            messagebox.showerror("Error", "Failed to send command. NATS not connected.")
            return

    def log_message(self, message):
        """Log messages to console or UI"""
        print(message)

    def handle_event_message(self, message):
        """Handle received event message"""
        try:
            # Log message for debugging
            timestamp = self.master.get_timestamp()
            print(f"[{timestamp}] RECEIVED: {json.dumps(message, indent=2)}")

            if message.get("type") == "tray_positioned_to_loading":
                status = message.get("data", {}).get("status", "")
                if status == "success":
                    print("Tray positioned successfully, showing popup...")
                    self.master.after(0, self.show_insert_slide_popup)

        except Exception as e:
            print(f"Error handling event in SecondScreen: {e}")

    def show_insert_slide_popup(self):
        """Show popup to insert slide"""
        popup = tk.Toplevel(self)
        popup.title("Insert Slide")
        popup.geometry("400x200")

        label = tk.Label(popup, text="Please insert the slide and press Next", font=("Arial", 14))
        label.pack(pady=20)

        next_button = tk.Button(popup, text="Next", command=lambda: self.on_insert_slide_next(popup), bg="#4CAF50", fg="white", height=2, width=15)
        next_button.pack(pady=10)

    def on_insert_slide_next(self, popup):
        """Handle next action after inserting slide"""
        popup.destroy()
        # ✅ Example: Proceed to the next screen or action
        # self.master.show_screen("ThirdScreen", selected_tests=self.selected_tests)
        messagebox.showinfo("Info", "Slide inserted successfully. Proceeding...")

