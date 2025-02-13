import pickle

def read_pickle_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
            print("Contents of the pickle file:")
            print(data)
    except Exception as e:
        print(f"Error reading pickle file: {e}")

# Example usage
file_path = "/home/sigtuple/Desktop/device_logic_layer/src/calibration_data/calib.pkl"  # Change this to your pickle file path
read_pickle_file(file_path)
