import threading
import time

# Global stop event
stop_event = threading.Event()
stop_event2 = threading.Event()

class WorkerA:
    def __init__(self):
        self.thread = threading.Thread(target=self.run, name="WorkerA")

    def start(self):
        self.thread.start()

    def run(self):
        while not stop_event2.is_set():
            while not stop_event.is_set():
                print("WorkerA running...")
                time.sleep(1)
            time.sleep(0.5)
            print("WorkerA stopped with stop event 1 ---------------------------.")
        print("Worker A stopeed with stope event 2 ########################")
class WorkerB:
    def __init__(self):
        self.thread = threading.Thread(target=self.run, name="WorkerB")

    def start(self):
        self.thread.start()

    def run(self):
        while not stop_event2.is_set():
            print("WorkerB running...")
            time.sleep(3)
            stop_event.set()
            time.sleep(1)
            stop_event.clear()
        print("WorkerB stopped. with stop event 2 &&&&&&&&&&&&&&&&&&&&&&&&&")

# Create and start workers
worker_a = WorkerA()
worker_b = WorkerB()

worker_a.start()
worker_b.start()

# Let the workers run for 5 seconds
time.sleep(5)

# Stop all workers
print("Stopping all workers...")
stop_event2.set()

# Wait for workers to finish
worker_a.thread.join()
worker_b.thread.join()

print("All workers stopped.")
