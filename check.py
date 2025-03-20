import pickle
import cv2
import numpy as np
import os

# Function to load and display the image
def load_and_show_pkl_image(pkl_path):
    with open(pkl_path, 'rb') as file:
        data = pickle.load(file)  # Load the pickle file

    if isinstance(data, np.ndarray):  
        image = data  # Directly use if it's an image array
    elif isinstance(data, dict):  
        # If stored in a dict, try common keys like 'image' or 'img'
        image = data.get('image') or data.get('img')
    else:
        raise ValueError("Unsupported data format in the pickle file.")

    if image is None:
        raise ValueError("No valid image found in the pickle file.")

    cv2.imshow("Image from Pickle", image)
    cv2.waitKey(0)  # Wait for key press
    cv2.destroyAllWindows()

# Example usage
pkl_path = "/imgarc/sigvet/tempfs/000.pkl"  # Change to your file path
load_and_show_pkl_image(pkl_path)
