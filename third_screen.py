import tkinter as tk
from tkinter import messagebox, ttk
import uuid
import json
from datetime import datetime

class ThirdScreen(tk.Frame):
    def __init__(self, master, selected_tests=None, **kwargs):
        super().__init__(master)
        self.master = master
        self.selected_tests = selected_tests or []
        self.current_test_index = 0
            ###
        # Reset flag to track if calibration has started
        self.calibration_started = False
        
        # Clear previous test data
        self.test_status = {}
        self.test_labels = {}
        self.test_state_labels = {}
        
        # Rest of the initialization...

        # Flag to track if calibration has started
        self.calibration_started = False
        
        # Store all calibration tests (selected and unselected)
        self.all_tests = {}
        
        # Title
        self.label = tk.Label(self, text="Calibration Tests Progress", font=("Arial", 16))
        self.label.pack(pady=10)
        
        # Main container with scrolling
        self.scroll_frame = tk.Frame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.canvas = tk.Canvas(self.scroll_frame)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        
        # Inner frame for content
        self.inner_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        # Selected tests section
        self.selected_frame = tk.Frame(self.inner_frame)
        self.selected_frame.pack(fill="x", pady=5)
        
        self.selected_label = tk.Label(self.selected_frame, text="Selected Tests", font=("Arial", 14, "bold"))
        self.selected_label.pack(anchor="w", pady=5)
        
        # Frame for the selected test list
        self.test_frame = tk.Frame(self.selected_frame)
        self.test_frame.pack(fill="x", pady=5)
        
        # Create test status display (placeholders until we get the real data)
        self.test_status = {}
        self.test_labels = {}
        self.test_state_labels = {}
        
        # Add a separator between selected and unselected tests
        self.separator = ttk.Separator(self.inner_frame, orient="horizontal")
        self.separator.pack(fill="x", pady=10)
        
        # Unselected tests section
        self.unselected_frame = tk.Frame(self.inner_frame)
        self.unselected_frame.pack(fill="x", pady=5)
        
        self.unselected_label = tk.Label(self.unselected_frame, text="Other Tests", font=("Arial", 14, "bold"))
        self.unselected_label.pack(anchor="w", pady=5)
        
        # Frame for the unselected test list
        self.unselected_test_frame = tk.Frame(self.unselected_frame)
        self.unselected_test_frame.pack(fill="x", pady=5)
        
        # Progress bar
        self.progress_frame = tk.Frame(self)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_label = tk.Label(self.progress_frame, text="Overall Progress: Waiting to start...", font=("Arial", 12))
        self.progress_label.pack(anchor="w", pady=5)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(fill="x", pady=5)
        
        # Buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill="x", padx=20, pady=20)
        
        self.cancel_button = tk.Button(
            self.button_frame, 
            text="Cancel", 
            command=self.on_cancel, 
            bg="#f44336", 
            fg="white", 
            height=2, 
            width=15
        )
        self.cancel_button.pack(side="left", padx=10)
        
        # Update canvas when frame size changes
        self.inner_frame.bind("<Configure>", self.on_frame_configure)
        
        # After initialization, send the start_calibration command
        self.send_start_calibration()
    
    def on_frame_configure(self, event):
        """Configure the canvas scroll region when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def send_start_calibration(self):
        """Send the start_calibration command with selected tests"""
        command = {
            "id": str(uuid.uuid4()),
            "type": "start_calibration",
            "originator": "device_maintenance",
            "data": {
                "calibration_list": self.selected_tests
            },
            "metadata": {
                "correlation_id": str(uuid.uuid4()),
                "timestamp": self.master.get_timestamp(),
                "trace_id": str(uuid.uuid4())
            }
        }
        
        full_command = self.master.send_command(
            command["type"],
            "data.sv-maintenance.commands",
            command.get("data", {})
        )
        
        if full_command:
            print(f"Sent start_calibration command: {json.dumps(full_command, indent=2)}")
            timestamp = self.master.get_timestamp()
            self.log_message(f"[{timestamp}] SENT: {json.dumps(full_command, indent=2)}")
            
            # Display waiting message
            self.progress_label.config(text="Waiting for calibration to start...")
        else:
            messagebox.showerror("Error", "Failed to send start_calibration command. NATS not connected.")

    def process_calibration_data(self, calibration_list):
        """Process the calibration list and update UI"""
        if not self.calibration_started:
            # First time processing - initialize UI
            self.calibration_started = True

            # Clear UI frames
            for widget in self.test_frame.winfo_children():
                widget.destroy()
            for widget in self.unselected_test_frame.winfo_children():
                widget.destroy()

            # Store all tests with calib_name as key
            self.all_tests = {item["calib_name"]: item for item in calibration_list}
            print("tehh###############################",self.all_tests)

            # Display selected tests
            for test_name in self.selected_tests:
                if test_name in self.all_tests:
                    self.create_test_row(test_name, self.test_frame, True)

            # Display unselected tests
            unselected_tests = [test["calib_name"] for test in calibration_list if test["calib_name"] not in self.selected_tests]
            for test_name in unselected_tests:
                self.create_test_row(test_name, self.unselected_test_frame, False)

        else:
            # Update existing test states in UI
            for test in calibration_list:
                test_name = test["calib_name"]
                new_state = test["calib_state"]

                # Update the stored test state
                if test_name in self.all_tests:
                    self.all_tests[test_name] = test

                # Update UI for the test
                if test_name in self.test_state_labels:
                    self.update_test_ui(test_name, new_state)

        # Update progress after processing
        self.update_progress()


    
    def create_test_row(self, test_name, parent_frame, is_selected):
        """Create a row for a test in the specified parent frame"""
        frame = tk.Frame(parent_frame, pady=5)
        frame.pack(fill="x", pady=2)
        
        # Test name
        test_label = tk.Label(frame, text=test_name, font=("Arial", 12), anchor="w", width=40)
        test_label.pack(side="left", padx=5)
        
        # Determine initial state
        test_data = self.all_tests[test_name]
        test_state = test_data["calib_state"]
        
        # For selected tests, set initial status
        if is_selected:
            if test_state == "uncalibrated":
                if self.selected_tests.index(test_name) == 0:
                    status = "In Progress"
                else:
                    status = "In Queue"
            else:
                status = self.format_state(test_state)
        else:
            status = self.format_state(test_state)
        
        # Status label
        status_color = self.get_status_color(status)
        status_label = tk.Label(
            frame, 
            text=status, 
            font=("Arial", 12), 
            fg=status_color
        )
        status_label.pack(side="right", padx=10)
        
        # Store the labels for future updates
        self.test_labels[test_name] = test_label
        self.test_state_labels[test_name] = status_label
        
        # Store the status
        self.test_status[test_name] = status
    
    def format_state(self, state):
        """Format a calibration state into display text"""
        if state == "uncalibrated":
            return "Uncalibrated"
        elif state == "calibrated":
            return "Calibrated"
        elif state == "in_progress":
            return "In Progress"
        elif state == "inqueue":  # Add handling for "inqueue" state
            return "In Queue" 
        elif state == "failed":
            return "Failed"
        else:
            return state.replace("_", " ").title()
    
    def get_status_color(self, status):
        """Get the display color for a status"""
        if status == "Calibrated":
            return "green"
        elif status == "In Progress":
            return "blue"
        elif status == "In Queue":
            return "orange"
        elif status == "Failed":
            return "red"
        elif status == "Uncalibrated":
            return "gray"
        else:
            return "black"
        
    def remove_test_from_ui(self, test_name):
        """Removes the test row from the UI."""
        if test_name in self.test_labels:
            self.test_labels[test_name].destroy()  # Remove test name label
            del self.test_labels[test_name]
        
        if test_name in self.test_state_labels:
            self.test_state_labels[test_name].destroy()  # Remove state label
            del self.test_state_labels[test_name]

        if test_name in self.test_status:
            del self.test_status[test_name]  # Remove from status tracking

    
    def update_test_ui(self, test_name, new_state):
        """Update the UI for a specific test"""
        if test_name in self.test_state_labels:
            # Determine the display status
            is_selected = test_name in self.selected_tests
            
            if is_selected:
                # For selected tests, we use our custom statuses
                if new_state == "in_progress":
                    status = "In Progress"
                elif new_state == "inqueue":  # Add handling for "inqueue" state
                    status = "In Queue"
                elif new_state == "calibrated":
                    status = "Calibrated"
                elif new_state == "failed":
                    status = "Failed"
                elif new_state == "uncalibrated":
                    # Only change if it's currently uncalibrated
                    current_status = self.test_status.get(test_name, "")
                    if current_status not in ["In Progress", "In Queue"]:
                        status = "Uncalibrated"
                    else:
                        # Keep the current status
                        status = current_status
                else:
                    status = self.format_state(new_state)
            else:
                # For unselected tests, we directly show the state
                status = self.format_state(new_state)
            
            # Update the label
            label = self.test_state_labels[test_name]
            label.config(text=status, fg=self.get_status_color(status))
            
            # Update our stored status
            self.test_status[test_name] = status

    
    def update_progress(self):
        """Update progress bar based on calibrated tests"""
        if not self.selected_tests:
            return
            
        # Count completed tests among selected tests
        completed = sum(1 for test_name in self.selected_tests 
                    if test_name in self.all_tests and 
                    self.all_tests[test_name]["calib_state"] == "calibrated")
        
        # Calculate progress percentage
        progress_value = (completed / len(self.selected_tests)) * 100
        self.progress_bar["value"] = progress_value
        
        # Update progress text
        progress_text = f"Overall Progress: {completed}/{len(self.selected_tests)} tests completed ({int(progress_value)}%)"
        self.progress_label.config(text=progress_text)
        
        # Check if all selected tests are completed
        all_completed = all(
            test_name in self.all_tests and 
            self.all_tests[test_name]["calib_state"] in ["calibrated", "failed"]
            for test_name in self.selected_tests
        )
        
        if all_completed:
            messagebox.showinfo("Complete", "All calibration tests have been completed!")

    
    def on_cancel(self):
        """Handle cancel button click - show a pop-up for selecting tests to cancel"""
        
        # Filter tests that are either "in_progress" or "queue"
        cancelable_tests = {
            test_name: test_data
            for test_name, test_data in self.all_tests.items()
            if test_data["calib_state"] in ["in_progress", "in_queue"]
        }

        if not cancelable_tests:
            messagebox.showinfo("Cancel Calibration", "No tests are currently in progress or in queue to cancel.")
            return
        
        # Create a pop-up window for selection
        popup = tk.Toplevel(self)
        popup.title("Select Tests to Cancel")
        popup.geometry("400x300")
        
        tk.Label(popup, text="Select tests to cancel:", font=("Arial", 12, "bold")).pack(pady=10)

        # Dictionary to store the checkbutton states
        selected_tests = {}

        # Create checkbuttons for each test
        for test_name, test_data in cancelable_tests.items():
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(popup, text=test_name, variable=var, font=("Arial", 10))
            chk.pack(anchor="w", padx=20)
            selected_tests[test_name] = var

        def submit_cancel():
            """Gather selected tests and send the cancel command"""
            tests_to_cancel = [
                {"calib_name": name, "calib_state": cancelable_tests[name]["calib_state"]}
                for name, var in selected_tests.items() if var.get()
            ]

            if not tests_to_cancel:
                messagebox.showwarning("Cancel Calibration", "No tests selected for cancellation.")
                popup.destroy()
                return

            # Prepare the cancel command
            command = {
                "id": str(uuid.uuid4()),
                "type": "cancel_calibration",
                "originator": "device_maintenance",
                "data": {
                    "calibration_list": tests_to_cancel
                },
                "metadata": {
                    "correlation_id": str(uuid.uuid4()),
                    "timestamp": self.master.get_timestamp(),
                    "trace_id": str(uuid.uuid4())
                }
            }

            full_command = self.master.send_command(
                command["type"],
                "control.sv-maintenance.commands",
                command.get("data", {})
            )

            if full_command:
                print(f"Sent cancel command: {json.dumps(full_command, indent=2)}")
                self.log_message(f"SENT: {json.dumps(full_command, indent=2)}")
                messagebox.showinfo("Cancel Calibration", "Cancellation request sent successfully.")
            else:
                messagebox.showerror("Error", "Failed to send cancel command.")

            popup.destroy()

        # Submit button
        tk.Button(popup, text="Cancel Selected Tests", command=submit_cancel, bg="#f44336", fg="white").pack(pady=10)

        popup.transient(self)
        popup.grab_set()
        self.wait_window(popup)

    def remove_test_from_ui(self, test_name):
        """Removes the test row from the UI."""
        if test_name in self.test_ui_elements:
            for widget in self.test_ui_elements[test_name]:
                widget.destroy()  # Remove all widgets related to this test
            del self.test_ui_elements[test_name]  # Remove from the dictionary


    
    def on_event_message(self, message):
        """Handle received event messages"""
        try:
            timestamp = self.master.get_timestamp()
            print(f"[{timestamp}] RECEIVED in ThirdScreen: {json.dumps(message, indent=2)}")
            
            message_type = message.get("type")
            data = message.get("data", {})
            
            if message_type == "calibration_started":
                # For initial setup
                calibration_list = data.get("calibration_list", [])
                
                if calibration_list:
                    self.process_calibration_data(calibration_list)
            
            elif message_type == "calibration_executed":
                # For updates to individual tests
                # The structure might be the same as calibration_started
                calibration_list = data.get("calibration_started", [])
                if not calibration_list:
                    # Try alternative field name if first one is empty
                    calibration_list = data.get("calibration_list", [])
                
                if calibration_list:
                    # Instead of reinitializing UI, just update existing test states
                    for test in calibration_list:
                        test_name = test.get("calib_name")
                        test_state = test.get("calib_state")
                        
                        if test_name and test_name in self.all_tests:
                            # Update stored test data
                            self.all_tests[test_name] = test
                            # Update UI
                            self.update_test_ui(test_name, test_state)
                    
                    # Update overall progress
                    self.update_progress()
            
            elif message_type == "calibration_completed":
                status = message.get("data", {}).get("status")
                if status == "success":
                    messagebox.showinfo("Success", "Calibration completed successfully!")
                    # Go back to first screen or wherever appropriate
                    self.master.after(2000, lambda: self.master.show_screen("FirstScreen"))
                else:
                    print("ok")
                    # error_msg = message.get("data", {}).get("message", "Unknown error")
                    # messagebox.showerror("Error", f"Calibration failed: {error_msg}")

            elif message_type == "calibration_canceled":
                canceled_tests = data.get("calibration_list", [])

                if canceled_tests:
                    for canceled_test in canceled_tests:
                        test_name = canceled_test.get("calib_name")
                        new_state = canceled_test.get("calib_state")

                        if test_name in self.all_tests:
                            # Keep only tests that are "In_queue" or "in_progress"
                            if self.all_tests[test_name]["calib_state"] not in ["In_queue", "in_progress"]:
                                self.remove_test_from_ui(test_name)
                                del self.all_tests[test_name]  # Remove from internal tracking

                    self.update_progress()
                    messagebox.showinfo("Calibration Update", "Only 'In_queue' and 'in_progress' tests remain.")


        
        except Exception as e:
            print(f"Error handling event in ThirdScreen: {e}")
    
    def log_message(self, message):
        """Log messages to console"""
        print(message)
