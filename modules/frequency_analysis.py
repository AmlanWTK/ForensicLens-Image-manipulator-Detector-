"""
Frequency Analysis Module

Technique:
- Analyze image in frequency domain using FFT
- Detect periodic patterns using notch filter

Image Processing Topics Covered:
✓ FFT (Fast Fourier Transform)
✓ Notch Filter
✓ Frequency Domain Analysis
"""

import cv2
import numpy as np


def analyze_frequency_domain(image):
    """
    Analyze image frequency domain for manipulation artifacts
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image
        
    Returns:
    --------
    results : dict
        - fft_magnitude: FFT magnitude spectrum
        - periodic_detected: bool
        - score: Suspicion score (0-100)
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    # Compute FFT
    fft = np.fft.fft2(gray)
    fft_shifted = np.fft.fftshift(fft)
    
    # Magnitude spectrum
    magnitude = np.abs(fft_shifted)
    magnitude_log = np.log(magnitude + 1)
    
    # Normalize for visualization
    magnitude_normalized = ((magnitude_log - np.min(magnitude_log)) / 
                           (np.max(magnitude_log) - np.min(magnitude_log)) * 255).astype(np.uint8)
    
    # Detect periodic patterns
    # Remove DC component (center)
    h, w = magnitude.shape
    center_y, center_x = h // 2, w // 2
    
    magnitude_copy = magnitude.copy()
    magnitude_copy[center_y-10:center_y+10, center_x-10:center_x+10] = 0
    
    # Find peaks in frequency domain
    threshold = np.percentile(magnitude_copy, 99.5)
    peaks = magnitude_copy > threshold
    
    num_peaks = np.sum(peaks)
    
    periodic_detected = num_peaks > 50
    score = min(100, num_peaks // 5)
    
    return {
        'fft_magnitude': magnitude_normalized,
        'periodic_detected': periodic_detected,
        'num_peaks': int(num_peaks),
        'score': score
    }


def apply_notch_filter(image, notch_center, notch_radius=10):
    """
    Apply notch filter to remove periodic noise
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image
    notch_center : tuple
        (y, x) coordinates of notch center
    notch_radius : int
        Radius of notch
        
    Returns:
    --------
    filtered : numpy.ndarray
        Filtered image
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    # FFT
    fft = np.fft.fft2(gray)
    fft_shifted = np.fft.fftshift(fft)
    
    # Create notch filter mask
    h, w = gray.shape
    mask = np.ones((h, w), dtype=np.float32)
    
    cy, cx = notch_center
    y, x = np.ogrid[:h, :w]
    
    # Create circular notch
    distance = np.sqrt((y - cy)**2 + (x - cx)**2)
    mask[distance <= notch_radius] = 0
    
    # Apply symmetrical notch (both sides of center)
    center_y, center_x = h // 2, w // 2
    offset_y = cy - center_y
    offset_x = cx - center_x
    
    sym_cy = center_y - offset_y
    sym_cx = center_x - offset_x
    
    distance_sym = np.sqrt((y - sym_cy)**2 + (x - sym_cx)**2)
    mask[distance_sym <= notch_radius] = 0
    
    # Apply filter
    fft_filtered = fft_shifted * mask
    
    # Inverse FFT
    fft_ishifted = np.fft.ifftshift(fft_filtered)
    filtered = np.fft.ifft2(fft_ishifted)
    filtered = np.abs(filtered).astype(np.uint8)
    
    return filtered
