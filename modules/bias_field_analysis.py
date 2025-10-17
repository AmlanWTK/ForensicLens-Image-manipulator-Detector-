"""
Bias Field Analysis Module

Technique:
- Detect lighting inconsistencies
- Find unnatural illumination patterns

Image Processing Topics Covered:
✓ Bias Field Simulation
✓ Lighting Analysis
"""

import cv2
import numpy as np
from scipy import ndimage


def analyze_lighting_inconsistency(image):
    """
    Detect lighting inconsistencies
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image
        
    Returns:
    --------
    results : dict
        - lighting_map: Estimated lighting field
        - inconsistent: bool
        - score: Suspicion score (0-100)
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    # Estimate lighting field (smooth version of image)
    lighting_field = cv2.GaussianBlur(gray, (51, 51), 0)
    
    # Calculate lighting gradient
    gradient_x = cv2.Sobel(lighting_field, cv2.CV_64F, 1, 0, ksize=5)
    gradient_y = cv2.Sobel(lighting_field, cv2.CV_64F, 0, 1, ksize=5)
    
    gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
    
    # Normalize
    lighting_normalized = ((lighting_field - np.min(lighting_field)) / 
                          (np.max(lighting_field) - np.min(lighting_field) + 1e-8) * 255).astype(np.uint8)
    
    # Check for abrupt changes (inconsistent lighting)
    gradient_threshold = np.percentile(gradient_magnitude, 90)
    abrupt_changes = np.sum(gradient_magnitude > gradient_threshold)
    
    total_pixels = gradient_magnitude.size
    change_ratio = abrupt_changes / total_pixels
    
    inconsistent = change_ratio > 0.05
    score = min(100, int(change_ratio * 1000))
    
    return {
        'lighting_map': lighting_normalized,
        'gradient_magnitude': gradient_magnitude,
        'inconsistent': inconsistent,
        'score': score
    }
