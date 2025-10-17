"""
Noise Analysis Module

Technique:
- Analyze noise patterns across image regions
- Detect inconsistent noise (sign of splicing)

Image Processing Topics Covered:
✓ Gaussian Noise Detection
✓ Poisson Noise Detection
✓ Region Descriptors
"""

import cv2
import numpy as np


def analyze_noise_inconsistency(image, block_size=64):
    """
    Detect noise inconsistencies across image
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image
    block_size : int
        Size of blocks for analysis
        
    Returns:
    --------
    results : dict
        - noise_map: Noise level map
        - inconsistency_mask: Binary mask of suspicious regions
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
    
    # Calculate noise for each block
    noise_map = np.zeros((h_blocks, w_blocks))
    
    for i in range(h_blocks):
        for j in range(w_blocks):
            block = gray[i*block_size:(i+1)*block_size, 
                        j*block_size:(j+1)*block_size]
            noise_map[i, j] = estimate_noise(block)
    
    # Resize to full image size
    noise_map_full = cv2.resize(noise_map, (w, h), interpolation=cv2.INTER_LINEAR)
    
    # Normalize
    noise_map_normalized = ((noise_map_full - np.min(noise_map_full)) / 
                           (np.max(noise_map_full) - np.min(noise_map_full) + 1e-8) * 255).astype(np.uint8)
    
    # Find inconsistent regions
    noise_mean = np.mean(noise_map)
    noise_std = np.std(noise_map)
    threshold = noise_mean + 1.5 * noise_std
    
    inconsistency_mask = (noise_map_full > threshold).astype(np.uint8) * 255
    
    # Calculate score
    cv_coefficient = noise_std / (noise_mean + 1e-8)
    score = min(100, int(cv_coefficient * 200))
    
    return {
        'noise_map': noise_map_normalized,
        'inconsistency_mask': inconsistency_mask,
        'score': score
    }


def estimate_noise(image_block):
    """
    Estimate noise level in image block
    
    Uses Laplacian method (detects high-frequency noise)
    
    Parameters:
    -----------
    image_block : numpy.ndarray
        Image block
        
    Returns:
    --------
    noise_std : float
        Estimated noise standard deviation
    """
    # Apply Laplacian to get high-frequency components
    laplacian = cv2.Laplacian(image_block.astype(float), cv2.CV_64F)
    
    # Median Absolute Deviation (robust noise estimator)
    mad = np.median(np.abs(laplacian - np.median(laplacian)))
    
    # Convert to standard deviation
    noise_std = 1.4826 * mad
    
    return noise_std
