import torch
import argparse
import requests
import matplotlib.pyplot as plt
from PIL import Image
from transformers import pipeline, AutoImageProcessor, AutoModelForDepthEstimation
import cv2

def capture_image():
    """Capture an image from the camera."""
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Error: Could not capture image.")
        return None
    
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image)

def infer_depth_pipeline(image, model_name="depth-anything/Depth-Anything-V2-base-hf"):
    """Perform monocular depth estimation using the pipeline API."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = pipeline("depth-estimation", model=model_name, device=0 if device == "cuda" else -1)
    
    predictions = pipe(image)
    
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(image)
    plt.axis("off")
    plt.title("Original Image")
    
    plt.subplot(1, 2, 2)
    plt.imshow(predictions["depth"], cmap="magma")
    plt.axis("off")
    plt.title("Depth Map")
    
    plt.show()

def infer_depth_manual(image, model_name="Intel/zoedepth-nyu-kitti"):
    """Perform monocular depth estimation manually using ZoeDepth."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    image_processor = AutoImageProcessor.from_pretrained(model_name)
    model = AutoModelForDepthEstimation.from_pretrained(model_name).to(device)
    
    pixel_values = image_processor(image, return_tensors="pt").pixel_values.to(device)
    
    with torch.no_grad():
        outputs = model(pixel_values)
    
    post_processed_output = image_processor.post_process_depth_estimation(outputs, source_sizes=[(image.height, image.width)])
    predicted_depth = post_processed_output[0]["predicted_depth"]
    
    depth = (predicted_depth - predicted_depth.min()) / (predicted_depth.max() - predicted_depth.min())
    depth = depth.detach().cpu().numpy() * 255
    depth = Image.fromarray(depth.astype("uint8"))
    
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(image)
    plt.axis("off")
    plt.title("Original Image")
    
    plt.subplot(1, 2, 2)
    plt.imshow(depth, cmap="magma")
    plt.axis("off")
    plt.title("Depth Map")
    
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Monocular Depth Estimation")
    parser.add_argument("--model", type=str, choices=["depth-anything", "zoedepth"], default="depth-anything", help="Choose the depth estimation model")
    
    args = parser.parse_args()
    
    image = capture_image()
    if image is None:
        return
    
    if args.model == "depth-anything":
        infer_depth_pipeline(image)
    else:
        infer_depth_manual(image)

if __name__ == "__main__":
    main()