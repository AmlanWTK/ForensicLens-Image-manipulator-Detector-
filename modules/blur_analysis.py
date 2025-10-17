"""
Blur Analysis Module

Technique:
- Detect inconsistent blur across image
- Find motion blur artifacts

Image Processing Topics Covered:
✓ Motion Blur Detection
✓ Edge Sharpness Analysis
"""

import cv2
import numpy as np


def analyze_blur_inconsistency(image, block_size=64):
    """
    Detect blur inconsistencies
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image
    block_size : int
        Block size for analysis
        
    Returns:
    --------
    results : dict
        - blur_map: Map of blur levels
        - inconsistent: bool
        - score: Suspicion score (0-100)
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    h, w = gray.shape
    h_blocks = h // block_size
    w_blocks = w // block_size
    
    # Calculate blur metric for each block
    blur_map = np.zeros((h_blocks, w_blocks))
    
    for i in range(h_blocks):
        for j in range(w_blocks):
            block = gray[i*block_size:(i+1)*block_size, 
                        j*block_size:(j+1)*block_size]
            
            # Laplacian variance (blur metric)
            blur_map[i, j] = cv2.Laplacian(block, cv2.CV_64F).var()
    
    # Resize
    blur_map_full = cv2.resize(blur_map, (w, h), interpolation=cv2.INTER_LINEAR)
    
    # Normalize (invert - high variance = sharp, low = blurry)
    blur_map_inverted = np.max(blur_map_full) - blur_map_full
    blur_normalized = ((blur_map_inverted - np.min(blur_map_inverted)) / 
                      (np.max(blur_map_inverted) - np.min(blur_map_inverted) + 1e-8) * 255).astype(np.uint8)
    
    # Check inconsistency
    blur_std = np.std(blur_map)
    blur_mean = np.mean(blur_map)
    
    cv_coefficient = blur_std / (blur_mean + 1e-8)
    
    inconsistent = cv_coefficient > 0.6
    score = min(100, int(cv_coefficient * 120))
    
    return {
        'blur_map': blur_normalized,
        'inconsistent': inconsistent,
        'score': score
    }
