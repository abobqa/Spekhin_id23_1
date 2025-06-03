import cv2
import numpy as np
import base64
from typing import Literal
from app.services.otsu import otsu_threshold
from app.services.niblack import niblack_threshold
from app.services.sauvola import sauvola_threshold
from io import BytesIO
from PIL import Image

SUPPORTED_ALGORITHMS = ["otsu", "niblack", "sauvola"]

def decode_base64_image(base64_str: str) -> np.ndarray:
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data)).convert("L")
    return np.array(image)

def encode_base64_image(image_array: np.ndarray) -> str:
    pil_img = Image.fromarray(image_array)
    buffered = BytesIO()
    pil_img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def binarize_image(image: np.ndarray, algorithm: Literal["otsu", "niblack", "sauvola"]) -> np.ndarray:
    if algorithm == "otsu":
        return otsu_threshold(image)
    elif algorithm == "niblack":
        return niblack_threshold(image)
    elif algorithm == "sauvola":
        return sauvola_threshold(image)
    else:
        raise ValueError(f"Unsupported algorithm '{algorithm}'. Supported: {SUPPORTED_ALGORITHMS}")
