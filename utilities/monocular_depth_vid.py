import torch
import argparse
import requests
import matplotlib.pyplot as plt
import time
from PIL import Image
from transformers import pipeline, AutoImageProcessor, AutoModelForDepthEstimation
import cv2
import numpy as np

def capture_frame(cap):
    """Capture a frame from the video feed."""
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not capture frame.")
        return None
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image), frame

def infer_depth_pipeline(pipe, image):
    """Perform monocular depth estimation using the pipeline API."""
    start_time = time.time()
    predictions = pipe(image)
    processing_time = time.time() - start_time
    
    depth_map = predictions["depth"]
    return depth_map, processing_time

def infer_depth_manual(model, image_processor, image):
    """Perform monocular depth estimation manually using ZoeDepth."""
    start_time = time.time()
    pixel_values = image_processor(image, return_tensors="pt").pixel_values.to("cuda" if torch.cuda.is_available() else "cpu")
    with torch.no_grad():
        outputs = model(pixel_values)
    post_processed_output = image_processor.post_process_depth_estimation(outputs, source_sizes=[(image.height, image.width)])
    predicted_depth = post_processed_output[0]["predicted_depth"]
    depth = (predicted_depth - predicted_depth.min()) / (predicted_depth.max() - predicted_depth.min())
    depth = depth.detach().cpu().numpy() * 255
    depth_map = Image.fromarray(depth.astype("uint8"))
    processing_time = time.time() - start_time
    return depth_map, processing_time

def main():
    parser = argparse.ArgumentParser(description="Monocular Depth Estimation")
    parser.add_argument("--model", type=str, choices=["depth-anything", "zoedepth"], default="depth-anything", help="Choose the depth estimation model")
    args = parser.parse_args()
    
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    if args.model == "depth-anything":
        pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-base-hf", device=0 if device == "cuda" else -1)
        model_obj = pipe
    else:
        image_processor = AutoImageProcessor.from_pretrained("Intel/zoedepth-nyu-kitti")
        model = AutoModelForDepthEstimation.from_pretrained("Intel/zoedepth-nyu-kitti").to(device)
        model_obj = (model, image_processor)
    
    while True:
        image, frame = capture_frame(cap)
        if image is None:
            continue
        
        if args.model == "depth-anything":
            depth_map, processing_time = infer_depth_pipeline(model_obj, image)
        else:
            depth_map, processing_time = infer_depth_manual(*model_obj, image)
        
        print(f"Processing Time: {processing_time:.2f} seconds")
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        depth_map = np.array(depth_map)  # Convert PIL image to NumPy array
        depth_map = cv2.cvtColor(depth_map, cv2.COLOR_GRAY2BGR)  # Convert grayscale to BGR
        depth_map = cv2.cvtColor(depth_map, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        
        combined = cv2.hconcat([frame, depth_map])
        cv2.imshow("Depth Estimation", cv2.cvtColor(combined, cv2.COLOR_RGB2BGR))
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
