import numpy as np

def otsu_threshold(image: np.ndarray) -> np.ndarray:
    pixel_counts = np.bincount(image.ravel(), minlength=256)
    total_pixels = image.size

    sum_total = np.sum(np.arange(256) * pixel_counts)
    sum_background = 0
    weight_background = 0
    max_variance = 0
    threshold = 0

    for t in range(256):
        weight_background += pixel_counts[t]
        if weight_background == 0:
            continue

        weight_foreground = total_pixels - weight_background
        if weight_foreground == 0:
            break

        sum_background += t * pixel_counts[t]

        mean_background = sum_background / weight_background
        mean_foreground = (sum_total - sum_background) / weight_foreground

        between_class_variance = (
            weight_background * weight_foreground * (mean_background - mean_foreground) ** 2
        )

        if between_class_variance > max_variance:
            max_variance = between_class_variance
            threshold = t

    binarized = (image >= threshold).astype(np.uint8) * 255
    return binarized
