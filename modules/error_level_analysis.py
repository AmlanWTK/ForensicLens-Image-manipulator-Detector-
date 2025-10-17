"""
Error Level Analysis (ELA) Module

Technique:
- Re-compress image at known JPEG quality
- Compare with original to find editing artifacts

Image Processing Topics Covered:
✓ JPEG Compression
✓ Bit-Depth Reduction
"""

import cv2
import numpy as np
from PIL import Image
import io


def perform_ela(image_path, quality=95):
    """
    Perform Error Level Analysis
    
    Parameters:
    -----------
    image_path : str
        Path to image file
    quality : int
        JPEG quality for re-compression (default 95)
        
    Returns:
    --------
    results : dict
        - ela_image: Error level result
        - ela_enhanced: Enhanced for visualization
        - score: Suspicion score (0-100)
    """
    # Load original
    original = Image.open(image_path).convert('RGB')
    
    # Re-compress at specified quality
    temp_buffer = io.BytesIO()
    original.save(temp_buffer, format='JPEG', quality=quality)
    temp_buffer.seek(0)
    compressed = Image.open(temp_buffer)
    
    # Convert to numpy
    original_array = np.array(original)
    compressed_array = np.array(compressed)
    
    # Calculate difference
    ela_array = np.abs(original_array.astype(int) - compressed_array.astype(int))
    
    # Normalize
    if np.max(ela_array) > 0:
        ela_normalized = (ela_array * 255.0 / np.max(ela_array)).astype(np.uint8)
    else:
        ela_normalized = ela_array.astype(np.uint8)
    
    # Enhanced version (amplify differences)
    ela_enhanced = np.clip(ela_array * 10, 0, 255).astype(np.uint8)
    
    # Calculate suspicion score
    # High variance in ELA = likely edited
    ela_variance = np.var(ela_array)
    score = min(100, ela_variance / 10)
    
    return {
        'ela_image': ela_normalized,
        'ela_enhanced': ela_enhanced,
        'score': int(score)
    }


def create_ela_heatmap(ela_image):
    """
    Create color heatmap from ELA result
    
    Parameters:
    -----------
    ela_image : numpy.ndarray
        ELA result
        
    Returns:
    --------
    heatmap : numpy.ndarray
        Color heatmap
    """
    # Convert to grayscale if needed
    if len(ela_image.shape) == 3:
        ela_gray = cv2.cvtColor(ela_image, cv2.COLOR_RGB2GRAY)
    else:
        ela_gray = ela_image
    
    # Apply colormap
    heatmap = cv2.applyColorMap(ela_gray, cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    
    return heatmap
