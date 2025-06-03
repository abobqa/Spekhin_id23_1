import numpy as np
import cv2

def niblack_threshold(image: np.ndarray, window_size: int = 25, k: float = 0.5) -> np.ndarray:
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image = image.astype(np.float32)
    h, w = image.shape
    output = np.zeros((h, w), dtype=np.uint8)

    half_win = window_size // 2

    for y in range(h):
        for x in range(w):
            y0 = max(0, y - half_win)
            y1 = min(h, y + half_win + 1)
            x0 = max(0, x - half_win)
            x1 = min(w, x + half_win + 1)

            window = image[y0:y1, x0:x1]
            mean = np.mean(window)
            std = np.std(window)

            threshold = mean + k * std
            output[y, x] = 255 if image[y, x] > threshold else 0

    return output
