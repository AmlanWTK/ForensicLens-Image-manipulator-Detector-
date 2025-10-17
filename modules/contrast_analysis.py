"""
Contrast Analysis Module

Technique:
- Detect localized contrast adjustments
- Find unnatural contrast patterns

Image Processing Topics Covered:
✓ Contrast Shift
✓ Local vs Global Contrast
"""

import cv2
import numpy as np


def analyze_contrast_manipulation(image, block_size=64):
    """
    Detect contrast manipulation
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image
    block_size : int
        Block size for local analysis
        
    Returns:
    --------
    results : dict
        - contrast_map: Map of contrast levels
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
    
    # Calculate local contrast for each block
    contrast_map = np.zeros((h_blocks, w_blocks))
    
    for i in range(h_blocks):
        for j in range(w_blocks):
            block = gray[i*block_size:(i+1)*block_size, 
                        j*block_size:(j+1)*block_size]
            
            # Calculate contrast (standard deviation)
            contrast_map[i, j] = np.std(block)
    
    # Resize to full size
    contrast_map_full = cv2.resize(contrast_map, (w, h), interpolation=cv2.INTER_LINEAR)
    
    # Normalize
    contrast_normalized = ((contrast_map_full - np.min(contrast_map_full)) / 
                          (np.max(contrast_map_full) - np.min(contrast_map_full) + 1e-8) * 255).astype(np.uint8)
    
    # Check for inconsistency
    contrast_std = np.std(contrast_map)
    contrast_mean = np.mean(contrast_map)
    
    cv_coefficient = contrast_std / (contrast_mean + 1e-8)
    
    inconsistent = cv_coefficient > 0.5
    score = min(100, int(cv_coefficient * 150))
    
    return {
        'contrast_map': contrast_normalized,
        'inconsistent': inconsistent,
        'score': score
    }
