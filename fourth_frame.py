import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid
import asyncio
import json
class CalibrationStatusFrame:
    def __init__(self, root, calibration_list, message_text, publisher_callback):
        self.root = root
        self.root.title("Calibration Status")
        self.calibration_list = calibration_list
        self.publisher_callback = publisher_callback
        self.current_test_index = 0
        
        # Main container
        self.container = ttk.Frame(root)
        self.container.grid(row=0, column=0, padx=10, pady=10)
        
        # Left side: Status boxes
        self.frame_left = ttk.Frame(self.container)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10)
        self.label = ttk.Label(self.frame_left, text="Calibration Test Status:")
        self.label.grid(row=0, column=0, padx=5, pady=5)
        
        # Frame for status boxes
        self.status_frame = ttk.Frame(self.frame_left)
        self.status_frame.grid(row=1, column=0, padx=5, pady=5)
        
        self.status_labels = {}
        for i, test in enumerate(calibration_list):
            # Test name label
            test_label = ttk.Label(self.status_frame, text=test)
            test_label.grid(row=i, column=0, sticky='w', padx=5, pady=2)
            
            # Status label - initially all tests are "In Queue"
            status_label = ttk.Label(self.status_frame, text="In Queue", 
                                   background='light gray', width=10)
            status_label.grid(row=i, column=1, padx=5, pady=2)
            self.status_labels[test] = status_label
        
        # Add Cancel button
        self.cancel_button = ttk.Button(self.frame_left, text="Cancel Tests", 
                                      command=self.show_cancel_dialog)
        self.cancel_button.grid(row=2, column=0, pady=10)
        
        # Set first test as "In Progress"
        if calibration_list:
            self.status_labels[calibration_list[0]].configure(
                text="In Progress", background='orange')
        
        # Right side: Message display
        self.frame_right = ttk.Frame(self.container)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10)
        self.messages_label = ttk.Label(self.frame_right, text="Received Messages:")
        self.messages_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.messages_text = tk.Text(self.frame_right, width=50, height=20, 
                                   state="disabled", wrap="word")
        self.messages_text.grid(row=1, column=0, padx=5, pady=5)
        self.messages_text.configure(state="normal")
        self.messages_text.insert("end", message_text)
        self.messages_text.configure(state="disabled")

    def show_cancel_dialog(self):
        """Show dialog with checkboxes for tests that can be cancelled"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cancel Tests")
        dialog.grab_set()  # Make dialog modal
        
        # Add instruction label
        instruction_label = ttk.Label(dialog, 
                                    text="Select tests to cancel:")
        instruction_label.grid(row=0, column=0, padx=10, pady=5)
        
        # Create frame for checkboxes
        checkbox_frame = ttk.Frame(dialog)
        checkbox_frame.grid(row=1, column=0, padx=10, pady=5)
        
        # Dictionary to store checkbox variables
        checkbox_vars = {}
        
        # Add checkboxes for in-progress and queued tests
        current_row = 0
        for test in self.calibration_list:
            status = self.status_labels[test].cget("text")
            if status in ["In Progress", "In Queue"]:
                var = tk.BooleanVar()
                checkbox_vars[test] = var
                cb = ttk.Checkbutton(checkbox_frame, text=test, variable=var)
                cb.grid(row=current_row, column=0, sticky='w', pady=2)
                current_row += 1
        
        def send_cancel_request():
            # Get selected tests
            selected_tests = [test for test, var in checkbox_vars.items() 
                            if var.get()]
            
            if selected_tests:
                # Prepare cancel message
                cancel_msg = {
                    "id": str(uuid.uuid4()),
                    "type": "cancel_calibration",
                    "originator": "Simulator",
                    "job_id": "job1",
                    "metadata": {
                        "correlation_id": str(uuid.uuid4()),
                        "timestamp": "2024-11-30T15:53:24:12Z",
                        "trace_id": str(uuid.uuid4())
                    },
                    "data": {
                        "tests_to_cancel": selected_tests
                    }
                }
                
                # Use the publisher_callback with the correct subject
                try:
                    self.publisher_callback("cancel_calibration", cancel_msg)
                    print("[Publisher] Published cancel request to 'control.sv-maintenance.commands'")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to send cancel request: {str(e)}")
            else:
                messagebox.showwarning("No Selection", 
                                     "Please select at least one test to cancel.")
        
        # Add Cancel button
        cancel_button = ttk.Button(dialog, text="Cancel Selected Tests", 
                                 command=send_cancel_request)
        cancel_button.grid(row=2, column=0, pady=10)

    def update_test_status(self, test_name, status):
        """Update the status label for a specific test and manage the sequence"""
        if test_name in self.status_labels:
            label = self.status_labels[test_name]
            if status == "success":
                label.configure(text="Completed", background='green')
                
                # Move to next test if available
                current_index = self.calibration_list.index(test_name)
                if current_index + 1 < len(self.calibration_list):
                    next_test = self.calibration_list[current_index + 1]
                    self.status_labels[next_test].configure(
                        text="In Progress", background='orange')
            else:
                label.configure(text="Failed", background='red')

    def display_message(self, subject, message):
        """Display messages and handle test status updates"""
        self.messages_text.configure(state="normal")
        self.messages_text.insert("end", f"Subject: {subject}\nMessage: {message}\n\n")
        self.messages_text.configure(state="disabled")
        self.messages_text.see("end")
        
        try:
            message_data = json.loads(message)
            if message_data.get("type") == "record_calibration_test_executed":
                test_data = message_data.get("data", {})
                test_name = test_data.get("test", "")
                status = test_data.get("status", "")
                
                if test_name and status:
                    self.update_test_status(test_name, status)
                
                # Check if all tests are completed
                all_completed = all(
                    label.cget("text") == "Completed" 
                    for label in self.status_labels.values()
                )
                
                if all_completed:
                    messagebox.showinfo("Calibration Complete", 
                                      "All calibration tests have been completed!")
        except json.JSONDecodeError:
            pass