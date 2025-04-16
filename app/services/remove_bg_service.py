import cv2
import numpy as np
import torch
from torchvision import transforms
from app.models.u2net import U2NET
from PIL import Image
import io
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level to /app
APP_DIR = os.path.dirname(BASE_DIR)
# Navigate to /app/model/weight
WEIGHT_DIR = os.path.join(APP_DIR, "models", "weight")

# Load U^2-Net model
model_path = os.path.join(WEIGHT_DIR, "u2net.pth")

net = U2NET(3, 1)
net.load_state_dict(torch.load(model_path, map_location='cpu'))
net.eval()

# Transform for model input
transform = transforms.Compose([
    transforms.Resize((320, 320)),
    transforms.ToTensor()
])

def resize_image_for_sd(image: Image, max_size: int = 500):
    """
    Resize image for SD version (max dimension size)
    """
    width, height = image.size
    if width > height:
        new_width = max_size
        new_height = int((max_size / width) * height)
    else:
        new_height = max_size
        new_width = int((max_size / height) * width)
    return image.resize((new_width, new_height))

def remove_background(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    original_size = image.size

    # Create SD version of image (only resize if it exceeds max size)
    if original_size[0] > 500 or original_size[1] > 500:
        sd_image = resize_image_for_sd(image, max_size=500)
    else:
        sd_image = image
    sd_size = sd_image.size

    # Preprocess SD image for model
    img_tensor = transform(sd_image).unsqueeze(0)

    with torch.no_grad():
        d1, *_ = net(img_tensor)
        mask = d1[0][0].numpy()
        mask = (mask * 255).astype(np.uint8)

        # Resize mask for SD image
        sd_mask = cv2.resize(mask, (sd_size[0], sd_size[1]))  # width, height
        _, sd_mask = cv2.threshold(sd_mask, 100, 255, cv2.THRESH_BINARY)

        # Convert SD image to RGBA
        sd_np = np.array(sd_image)
        sd_np = cv2.cvtColor(sd_np, cv2.COLOR_RGB2BGR)
        b, g, r = cv2.split(sd_np)
        sd_rgba = cv2.merge((b, g, r, sd_mask))

        # Resize mask for HD image (original image size)
        hd_mask = cv2.resize(mask, (original_size[0], original_size[1]))  # width, height
        _, hd_mask = cv2.threshold(hd_mask, 100, 255, cv2.THRESH_BINARY)

        hd_np = np.array(image)
        hd_np = cv2.cvtColor(hd_np, cv2.COLOR_RGB2BGR)
        b, g, r = cv2.split(hd_np)
        hd_rgba = cv2.merge((b, g, r, hd_mask))

        # Encode both images to PNG
        _, sd_encoded = cv2.imencode(".png", sd_rgba)
        _, hd_encoded = cv2.imencode(".png", hd_rgba)

        return (
            sd_encoded.tobytes(),  # SD image bytes
            sd_rgba.shape[:2],     # SD size (height, width)
            hd_encoded.tobytes(),  # HD image bytes
            hd_rgba.shape[:2]      # HD size (height, width)
        )
