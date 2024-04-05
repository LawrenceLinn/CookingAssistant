import ultralytics
from ultralytics import YOLO
from PIL import Image
import numpy as np
from IPython.display import display
import pathlib

def detect_food_ingredients(model_path, image_path):
    # Load the YOLO model
    
    model = YOLO(model_path)

    # Perform detection
    results = model(image_path)
    result = results[0]

    # Access class labels for each detection
    class_ids = result.boxes.cls.cpu().numpy()  # Convert to numpy array if not already
    detected_labels = [result.names[int(class_id)] for class_id in class_ids]

    # Convert the list of labels to a set to remove duplicates, then back to a list
    unique_labels = list(set(detected_labels))

    return unique_labels

def get_detected_image(model_path, image_path, conf=0.25, iou=0.7):
    
    model = YOLO(model_path)

    # Perform detection
    results = model.predict(
        source=image_path,
        conf=conf,
        iou=iou)

    first_image_results = results[0]

    detected_image = Image.fromarray(first_image_results.plot()[:,:,::-1])

    return detected_image

def YOLO_model(image_path):

    path = pathlib.Path(__file__).parent.resolve()
    # model_path = 

    return {'ingredients': detect_food_ingredients(f'{path}/best_weight_100.pt', image_path), 'image':get_detected_image(f'{path}/best_weight_100.pt', image_path)}