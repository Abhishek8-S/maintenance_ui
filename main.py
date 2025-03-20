import asyncio
import tkinter as tk
import threading
import uuid
import json
from datetime import datetime
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig

# Import your screens
from first_screen import FirstScreen
from second_screen import SecondScreen
from third_screen import ThirdScreen

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dummy UI")
        self.geometry("1000x800")
        
        # Initialize NATS components
        self.nc = None
        self.js = None
        self.loop = None
        
        # App information
        self.originator = "dummy-ui"
        
        # Current active screen
        self.current_screen = None
        
        # Store available screens
        self.screens = {
            "FirstScreen": FirstScreen,
            "SecondScreen": SecondScreen,
            "ThirdScreen": ThirdScreen,
        }
        
        # Start asyncio loop in a separate thread
        self.asyncio_thread = threading.Thread(target=self.run_asyncio_loop, daemon=True)
        self.asyncio_thread.start()
        
        # Initialize first screen (after a short delay to let NATS connect)
        self.after(100, lambda: self.show_screen("FirstScreen"))

    def get_timestamp(self):
        """Get a formatted timestamp for logging"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    def run_asyncio_loop(self):
        """Run the asyncio event loop in a separate thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.setup_nats())
        self.loop.run_forever()

    async def setup_nats(self):
        """Set up NATS and JetStream"""
        try:
            self.nc = NATS()
            await self.nc.connect("nats://localhost:4222")
            self.js = self.nc.jetstream()

            # Create standard streams
            await self.create_stream("data_stream", ["data.sv-maintenance.commands", "data.sv-maintenance.events"])
            await self.create_stream("control_stream", ["control.sv-maintenance.commands", "control.sv-maintenance.events"])

            # Subscribe to data events
            await self.nc.subscribe("data.sv-maintenance.events", cb=self.handle_event_message)
            
            print("NATS setup completed successfully")
        except Exception as e:
            print(f"NATS setup error: {e}")

    async def create_stream(self, name, subjects):
        """Create a JetStream stream if it doesn't exist"""
        try:
            await self.js.add_stream(StreamConfig(name=name, subjects=subjects))
            print(f"Stream '{name}' created successfully.")
        except Exception as e:
            if "already in use" in str(e):
                print(f"Stream '{name}' already exists.")
            else:
                print(f"Error creating stream '{name}': {e}")
    

    async def handle_event_message(self, msg):
        """Handle incoming event messages from NATS"""
        try:
            data = json.loads(msg.data.decode())
            print(f"Received event: {json.dumps(data, indent=2)}")

            # If the current screen has an on_event_message method, call it
            if self.current_screen and hasattr(self.current_screen, 'on_event_message'):
                self.current_screen.on_event_message(data)

            # Example: Switch to SecondScreen if the event type is 'calibration_complete'
            if data.get("type") == "calibration_complete":
                self.show_screen("SecondScreen", event_data=data)

        except Exception as e:
            print(f"Error handling event: {e}")

    
    def send_command(self, command_type, subject, data=None):
        """Send a command to a NATS subject with proper formatting"""
        if data is None:
            data = {}
        
        command = {
            "id": str(uuid.uuid4()),
            "type": command_type,
            "originator": self.originator,
            "metadata": {
                "correlation_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "trace_id": str(uuid.uuid4())
            },
            "data": data
        }
        
        json_command = json.dumps(command)
        
        if self.loop and self.js:
            asyncio.run_coroutine_threadsafe(
                self.js.publish(subject, json_command.encode()), 
                self.loop
            )
            print(f"Command sent: {command_type} to {subject}")
            return command  
        else:
            print("NATS not ready yet")
            return None
    def reset_screen(self):
        """Reset the screen state for reuse"""
        self.calibration_started = False
        self.all_tests = {}
        
        # Clear UI elements
        for widget in self.test_frame.winfo_children():
            widget.destroy()
        for widget in self.unselected_test_frame.winfo_children():
            widget.destroy()
        
        # Reset test tracking
        self.test_status = {}
        self.test_labels = {}
        self.test_state_labels = {}
        
        # Reset progress
        self.progress_bar["value"] = 0
        self.progress_label.config(text="Overall Progress: Waiting to start...")

    def show_screen(self, screen_name, **kwargs):
        """
        Switch to a specific screen by name
        """
        if screen_name not in self.screens:
            print(f"Screen '{screen_name}' not found")
            return False
            
        if self.current_screen:
            # Remove event handlers for the current screen if it's ThirdScreen
            if hasattr(self.current_screen, 'on_event_message'):
                # Unregister any event handlers if necessary
                pass
            
            self.current_screen.pack_forget()
            
        screen_class = self.screens[screen_name]
        self.current_screen = screen_class(self, **kwargs)
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
        # If the new screen is ThirdScreen, make sure it's properly initialized
        if screen_name == "ThirdScreen":
            # Allow the screen to be fully rendered before sending commands
            self.after(100, lambda: self.ensure_third_screen_initialized())
        
        print(f"Switched to {screen_name}")
        return True

    def ensure_third_screen_initialized(self):
        """
        Ensure the ThirdScreen is properly initialized
        """
        if hasattr(self.current_screen, 'calibration_started') and not self.current_screen.calibration_started:
            # Force the ThirdScreen to check for messages if it hasn't started yet
            print("Ensuring ThirdScreen is initialized...")
            
            # If you have any pending messages that should be processed, handle them here
            # For example, you might want to re-subscribe to event channels
            
            # You might also want to force a message check if there's a mechanism for that
            # self.check_for_messages()

        
    def register_screen(self, screen_name, screen_class):
        """Register a new screen type"""
        self.screens[screen_name] = screen_class
        print(f"Registered screen '{screen_name}'")

if __name__ == "__main__":
    app = App()
    app.mainloop()
