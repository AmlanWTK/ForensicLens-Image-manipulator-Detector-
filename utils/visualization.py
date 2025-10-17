"""
Visualization Module

Handles:
- Creating heatmaps from analysis results
- Side-by-side image comparisons
- Color mapping for forensics visualization
- Plot generation for reports
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.patches as mpatches


def create_heatmap(data, colormap='jet', normalize=True):
    """
    Create heatmap from data array
    
    Parameters:
    -----------
    data : numpy.ndarray
        2D array of values
    colormap : str
        OpenCV colormap name ('jet', 'hot', 'turbo', etc.)
    normalize : bool
        Whether to normalize data to [0, 255]
        
    Returns:
    --------
    heatmap : numpy.ndarray
        RGB heatmap image
    """
    # Ensure 2D array
    if len(data.shape) == 3:
        data = cv2.cvtColor(data, cv2.COLOR_RGB2GRAY)
    
    # Normalize to 0-255
    if normalize:
        data_normalized = ((data - np.min(data)) / 
                          (np.max(data) - np.min(data) + 1e-8) * 255).astype(np.uint8)
    else:
        data_normalized = data.astype(np.uint8)
    
    # Apply colormap
    colormap_dict = {
        'jet': cv2.COLORMAP_JET,
        'hot': cv2.COLORMAP_HOT,
        'turbo': cv2.COLORMAP_TURBO,
        'rainbow': cv2.COLORMAP_RAINBOW,
        'viridis': cv2.COLORMAP_VIRIDIS,
        'plasma': cv2.COLORMAP_PLASMA,
        'magma': cv2.COLORMAP_MAGMA
    }
    
    cmap = colormap_dict.get(colormap.lower(), cv2.COLORMAP_JET)
    heatmap = cv2.applyColorMap(data_normalized, cmap)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    
    return heatmap


def apply_colormap(image, colormap='jet'):
    """
    Apply colormap to grayscale image
    
    Parameters:
    -----------
    image : numpy.ndarray
        Grayscale image
    colormap : str
        Colormap name
        
    Returns:
    --------
    colored : numpy.ndarray
        Color-mapped image
    """
    return create_heatmap(image, colormap=colormap, normalize=True)


def display_side_by_side(images, titles=None, figsize=(15, 5), save_path=None):
    """
    Display multiple images side by side
    
    Parameters:
    -----------
    images : list
        List of numpy arrays (images)
    titles : list, optional
        List of titles for each image
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save the figure
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Generated figure
    """
    n_images = len(images)
    
    if titles is None:
        titles = [f'Image {i+1}' for i in range(n_images)]
    
    fig, axes = plt.subplots(1, n_images, figsize=figsize)
    
    # Handle single image case
    if n_images == 1:
        axes = [axes]
    
    for idx, (img, title) in enumerate(zip(images, titles)):
        # Convert to RGB if grayscale
        if len(img.shape) == 2:
            axes[idx].imshow(img, cmap='gray')
        else:
            axes[idx].imshow(img)
        
        axes[idx].set_title(title, fontsize=12, fontweight='bold')
        axes[idx].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Figure saved: {save_path}")
    
    return fig


def create_comparison_plot(original, result, analysis_name, save_path=None):
    """
    Create before/after comparison plot
    
    Parameters:
    -----------
    original : numpy.ndarray
        Original image
    result : numpy.ndarray
        Analysis result image
    analysis_name : str
        Name of the analysis
    save_path : str, optional
        Path to save the figure
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Generated figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Original
    if len(original.shape) == 2:
        axes[0].imshow(original, cmap='gray')
    else:
        axes[0].imshow(original)
    axes[0].set_title('Original Image', fontsize=14, fontweight='bold')
    axes[0].axis('off')
    
    # Result
    if len(result.shape) == 2:
        axes[1].imshow(result, cmap='gray')
    else:
        axes[1].imshow(result)
    axes[1].set_title(f'{analysis_name} Result', fontsize=14, fontweight='bold')
    axes[1].axis('off')
    
    plt.suptitle(f'Forensic Analysis: {analysis_name}', 
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Comparison saved: {save_path}")
    
    return fig


def create_overlay(original, mask, alpha=0.5, color=(255, 0, 0)):
    """
    Create overlay of mask on original image
    
    Parameters:
    -----------
    original : numpy.ndarray
        Original image
    mask : numpy.ndarray
        Binary or grayscale mask
    alpha : float
        Transparency (0-1)
    color : tuple
        RGB color for mask overlay
        
    Returns:
    --------
    overlay : numpy.ndarray
        Image with mask overlay
    """
    overlay = original.copy()
    
    # Ensure mask is 2D
    if len(mask.shape) == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
    
    # Normalize mask to 0-1
    mask_normalized = mask.astype(float) / 255.0
    
    # Create colored mask
    colored_mask = np.zeros_like(original)
    colored_mask[:, :] = color
    
    # Apply mask with alpha blending
    for c in range(3):
        overlay[:, :, c] = (
            original[:, :, c] * (1 - alpha * mask_normalized) +
            colored_mask[:, :, c] * (alpha * mask_normalized)
        ).astype(np.uint8)
    
    return overlay


def create_detection_visualization(image, suspicious_regions, title="Detection Results"):
    """
    Visualize detected suspicious regions
    
    Parameters:
    -----------
    image : numpy.ndarray
        Original image
    suspicious_regions : list of dict
        Each dict contains 'bbox' or 'mask' for suspicious region
    title : str
        Plot title
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figure with detections highlighted
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    ax.imshow(image)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')
    
    # Draw bounding boxes
    for region in suspicious_regions:
        if 'bbox' in region:
            x, y, w, h = region['bbox']
            rect = mpatches.Rectangle(
                (x, y), w, h,
                linewidth=2, edgecolor='red', facecolor='none'
            )
            ax.add_patch(rect)
            
            # Add label
            if 'label' in region:
                ax.text(x, y-5, region['label'], 
                       color='red', fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    plt.tight_layout()
    return fig
