"""
Image Loading and Preprocessing Module

Handles:
- Loading images from various formats
- Basic preprocessing (resize, normalize)
- Format conversions (RGB, Grayscale, etc.)
- Image validation
"""

import cv2
import numpy as np
from PIL import Image
import os


def load_image(image_path, color_mode='rgb'):
    """
    Load image from file path
    
    Parameters:
    -----------
    image_path : str
        Path to the image file
    color_mode : str
        'rgb', 'bgr', 'gray' - desired color mode
        
    Returns:
    --------
    image : numpy.ndarray
        Loaded image as numpy array
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Load image
    img = cv2.imread(image_path)
    
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    # Convert color mode
    if color_mode.lower() == 'rgb':
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    elif color_mode.lower() == 'gray':
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 'bgr' - keep as is
    
    return img


def preprocess_image(image, target_size=None, normalize=False):
    """
    Preprocess image for analysis
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image
    target_size : tuple, optional
        (width, height) to resize to
    normalize : bool
        Whether to normalize to [0, 1] range
        
    Returns:
    --------
    processed_image : numpy.ndarray
        Preprocessed image
    """
    processed = image.copy()
    
    # Resize if requested
    if target_size is not None:
        processed = cv2.resize(processed, target_size, interpolation=cv2.INTER_LINEAR)
    
    # Normalize if requested
    if normalize:
        processed = processed.astype(np.float32) / 255.0
    
    return processed


def save_image(image, output_path):
    """
    Save image to file
    
    Parameters:
    -----------
    image : numpy.ndarray
        Image to save
    output_path : str
        Path to save the image
    """
    # Create directory if doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert RGB to BGR for OpenCV saving
    if len(image.shape) == 3 and image.shape[2] == 3:
        image_to_save = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        image_to_save = image
    
    cv2.imwrite(output_path, image_to_save)
    print(f"✓ Image saved: {output_path}")


def validate_image(image):
    """
    Validate image format and properties
    
    Parameters:
    -----------
    image : numpy.ndarray
        Image to validate
        
    Returns:
    --------
    is_valid : bool
        Whether image is valid
    message : str
        Validation message
    """
    if not isinstance(image, np.ndarray):
        return False, "Image must be numpy array"
    
    if image.size == 0:
        return False, "Image is empty"
    
    if len(image.shape) not in [2, 3]:
        return False, "Image must be 2D (grayscale) or 3D (color)"
    
    if len(image.shape) == 3 and image.shape[2] not in [1, 3, 4]:
        return False, "Color image must have 1, 3, or 4 channels"
    
    return True, "Valid image"


def get_image_info(image):
    """
    Get detailed image information
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image
        
    Returns:
    --------
    info : dict
        Dictionary containing image properties
    """
    info = {
        'shape': image.shape,
        'height': image.shape[0],
        'width': image.shape[1],
        'channels': image.shape[2] if len(image.shape) == 3 else 1,
        'dtype': str(image.dtype),
        'min_value': np.min(image),
        'max_value': np.max(image),
        'mean_value': np.mean(image),
        'std_value': np.std(image)
    }
    
    return info
