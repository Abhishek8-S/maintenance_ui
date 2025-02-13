import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig
import json
import uuid
from second_frame import SecondFrame
from third_frame import ThirdFrame
from start_window import App

import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid

class CalibrationStatusFrame:
    def __init__(self, root, calibration_list, message_text, publisher_callback):
        self.root = root
        self.root.title("Calibration Status")
        self.calibration_list = calibration_list
        self.publisher_callback = publisher_callback
        self.current_test_index = 0
        

        self.container = ttk.Frame(root)
        self.container.grid(row=0, column=0, padx=10, pady=10)
        

        self.frame_left = ttk.Frame(self.container)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10)
        self.label = ttk.Label(self.frame_left, text="Calibration Test Status:")
        self.label.grid(row=0, column=0, padx=5, pady=5)
        

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

    def get_running_test(self):
        """Return the currently running test, if any"""
        for test, label in self.status_labels.items():
            if label.cget("text") == "In Progress":
                return test
        return None

    def remove_cancelled_tests(self, cancelled_tests):
        """Remove cancelled tests from the status display"""
        print(f"Starting to remove tests: {cancelled_tests}")
        print(f"Current calibration list: {self.calibration_list}")
        print(f"Current status labels: {list(self.status_labels.keys())}")
        
        # Store current statuses and colors before removing widgets
        current_statuses = {}
        for test, label in self.status_labels.items():
            current_statuses[test] = {
                'text': label.cget('text'),
                'background': label.cget('background')
            }
        
        # Remove all widgets from the status frame
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        
        # Update our tracking lists
        for test in cancelled_tests:
            if test in self.calibration_list:
                print(f"Removing test: {test}")
                self.calibration_list.remove(test)
                if test in self.status_labels:
                    del self.status_labels[test]
                if test in current_statuses:
                    del current_statuses[test]
        
        print(f"Remaining tests: {self.calibration_list}")
        
        # Rebuild the entire grid with preserved statuses
        for i, test in enumerate(self.calibration_list):
            print(f"Rebuilding grid for test {test} at row {i}")
            # Create new test name label
            test_label = ttk.Label(self.status_frame, text=test)
            test_label.grid(row=i, column=0, sticky='w', padx=5, pady=2)
            
            # Create new status label with preserved status
            if test in current_statuses:
                status = current_statuses[test]['text']
                bg_color = current_statuses[test]['background']
            else:
                status = "In Queue"
                bg_color = 'light gray'
                # If this is the first test and it's still in queue, mark it as In Progress
                if i == 0:
                    status = "In Progress"
                    bg_color = 'orange'
            
            status_label = ttk.Label(self.status_frame, text=status, 
                                   background=bg_color, width=10)
            status_label.grid(row=i, column=1, padx=5, pady=2)
            self.status_labels[test] = status_label
        
        # Update the frame
        self.status_frame.update()
        print(f"Final calibration list: {self.calibration_list}")
        print(f"Final status labels: {list(self.status_labels.keys())}")

    def show_cancel_dialog(self):
        """Show dialog with checkboxes for tests that can be cancelled"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cancel Tests")
        
        # Center the dialog on the parent window
        dialog.transient(self.root)
        
        # Wait for the dialog to be drawn
        dialog.update_idletasks()
        
        # Calculate position for the dialog
        x = self.root.winfo_rootx() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Make dialog modal after it's positioned and drawn
        dialog.focus_set()
        dialog.grab_set()
        
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
                # Get currently running test
                running_test = self.get_running_test()
                
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
                        "tests_to_cancel": selected_tests,
                        "running_test": running_test
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
async def run_simulation():
    nc = NATS()
    await nc.connect("nats://localhost:4222")

    js = nc.jetstream()

    async def create_stream(name, subjects):
        try:
            await js.add_stream(StreamConfig(name=name, subjects=subjects))
            print(f"Stream '{name}' created successfully.")
        except Exception as e:
            if "already in use" in str(e):
                print(f"Stream '{name}' already exists.")
            else:
                print(f"Error creating stream '{name}': {e}")

    await create_stream("data_stream", ["data.sv-maintenance.commands", "data.sv-maintenance.events"])
    await create_stream("control_stream", ["control.sv-maintenance.commands", "control.sv-maintenance.events"])

    loop = asyncio.get_running_loop()
    root = tk.Tk()
    
    current_frame = None
    last_message = None

    def switch_frames(frame_type, data=None, message=None):
        nonlocal current_frame, last_message
        if message:
            last_message = message

        for widget in root.winfo_children():
            widget.destroy()

        if frame_type == "second":
            current_frame = SecondFrame(root, data, last_message, 
                                     lambda msg_type, custom_msg=None: loop.create_task(publisher(msg_type, custom_msg)),
                                     switch_frames)
        elif frame_type == "third":
            current_frame = ThirdFrame(root, data, last_message,
                                    lambda msg_type, custom_msg=None: loop.create_task(publisher(msg_type, custom_msg)))
        elif frame_type == "calibration_status":
            current_frame = CalibrationStatusFrame(root, data, last_message,
                                                lambda msg_type, custom_msg=None: loop.create_task(publisher2(msg_type, custom_msg)))
        else:
            current_frame = App(root, 
                              lambda msg_type, custom_msg=None: loop.create_task(publisher(msg_type, custom_msg)),
                              switch_frames)

    current_frame = App(root, 
                       lambda msg_type, custom_msg=None: loop.create_task(publisher(msg_type, custom_msg)),
                       switch_frames)

    async def message_handler(msg):
        message = msg.data.decode()
        print(f"[Subscriber] Received on {msg.subject}: {message}")
        if current_frame:
            loop.call_soon_threadsafe(current_frame.display_message, msg.subject, message)
            
            try: 
                message_data = json.loads(message)
                if (message_data.get("type") == "calibration_started" and 
                    message_data.get("data", {}).get("status") == "success"):
                    calibration_list = message_data["data"].get("calibration_test_list", [])
                    loop.call_soon_threadsafe(switch_frames, "calibration_status", calibration_list, message)
            except json.JSONDecodeError:
                pass

    async def message_handler2(msg):
        message = msg.data.decode()
        print(f"[Subscriber2] Received on {msg.subject}: {message}")
        if current_frame:
            loop.call_soon_threadsafe(current_frame.display_message, msg.subject, message)
            
            try:
                message_data = json.loads(message)
                if (message_data.get("type") == "calibration_tests_cancelled"):
                    cancelled_tests = message_data.get("data", {}).get("cancelled_tests", [])
                    if isinstance(current_frame, CalibrationStatusFrame):
                        loop.call_soon_threadsafe(current_frame.remove_cancelled_tests, cancelled_tests)
            except json.JSONDecodeError:
                pass

    async def subscriber():
        print("Subscribing to data.sv-maintenance.events...")
        await nc.subscribe("data.sv-maintenance.events", cb=message_handler)

    async def subscriber2():
        print("Subscribing to control.sv-maintenance.events...")
        await nc.subscribe("control.sv-maintenance.events", cb=message_handler2)

    async def publisher(message_type, custom_msg=None):
        if custom_msg:
            msg = custom_msg
        else:
            msg = {
                "id": str(uuid.uuid4()),
                "type": message_type,
                "originator": "Simulator",
                "job_id": "job1",
                "metadata": {
                    "correlation_id": str(uuid.uuid4()),
                    "timestamp": "2024-11-30T15:53:24:12Z",
                    "trace_id": str(uuid.uuid4())
                },
                "data": {"slot_id": 1,"job_id": 234567,"species" : "feline"}
            }
        await js.publish("data.sv-maintenance.commands", json.dumps(msg).encode())
        print(f"[Publisher] Published to 'data.sv-maintenance.commands' with type: {message_type}")

    async def publisher2(message_type, custom_msg=None):
        if custom_msg:
            msg = custom_msg
        else:
            msg = {
                "id": str(uuid.uuid4()),
                "type": message_type,
                "originator": "Simulator",
                "job_id": "job1",
                "metadata": {
                    "correlation_id": str(uuid.uuid4()),
                    "timestamp": "2024-11-30T15:53:24:12Z",
                    "trace_id": str(uuid.uuid4())
                },
                "data": {"slot_id": 1}
            }
        await js.publish("control.sv-maintenance.commands", json.dumps(msg).encode())
        print(f"[Publisher] Published to 'control.sv-maintenance.commands' with type: {message_type}")

    async def tkinter_loop():
        while True:
            root.update()
            await asyncio.sleep(0.01)

    try:
        print("Starting subscribers and tkinter GUI...")
        await asyncio.gather(subscriber(), subscriber2(), tkinter_loop())
    except asyncio.CancelledError:
        print("Simulation stopped.")

    await nc.close()

if __name__ == "__main__":
    try:
        asyncio.run(run_simulation())
    except KeyboardInterrupt:
        print("Simulation interrupted by user.")
