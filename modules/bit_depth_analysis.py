"""
Bit-Depth Analysis Module

Technique:
- Detect posterization and bit-depth reduction
- Find color quantization artifacts

Image Processing Topics Covered:
✓ Bit-Depth Reduction
✓ Histogram Analysis
"""

import cv2
import numpy as np
from scipy import signal


def analyze_bit_depth(image):
    """
    Detect bit-depth reduction and posterization
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image
        
    Returns:
    --------
    results : dict
        - posterized: bool
        - estimated_bits: int (estimated bit depth)
        - score: Suspicion score (0-100)
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    # Calculate histogram
    hist, bins = np.histogram(gray.flatten(), bins=256, range=[0, 256])
    
    # Detect regular peaks (sign of posterization)
    peaks = signal.find_peaks(hist, height=np.max(hist) * 0.05)[0]
    
    posterized = False
    estimated_bits = 8
    score = 0
    
    if len(peaks) >= 4:
        # Check peak spacing regularity
        peak_spacing = np.diff(peaks)
        
        if len(peak_spacing) >= 2:
            spacing_mean = np.mean(peak_spacing)
            spacing_std = np.std(peak_spacing)
            
            if spacing_mean > 0:
                regularity = 1 - (spacing_std / spacing_mean)
                
                if regularity > 0.7:
                    posterized = True
                    
                    # Estimate bit depth from peak spacing
                    avg_spacing = spacing_mean
                    estimated_levels = 256 / avg_spacing
                    estimated_bits = int(np.log2(estimated_levels))
                    
                    score = int(regularity * 100)
    
    # Also check unique value count
    unique_values = len(np.unique(gray))
    
    if unique_values < 128:
        posterized = True
        score = max(score, int((1 - unique_values/256) * 100))
    
    return {
        'posterized': posterized,
        'estimated_bits': estimated_bits,
        'unique_colors': unique_values,
        'score': score
    }
