"""
Clone/Copy-Move Detection Module

Technique:
- Find duplicated regions in image
- Detect copy-paste forgery

Image Processing Topics Covered:
✓ Region Descriptors
✓ Feature Matching
"""

import cv2
import numpy as np


def detect_copy_move(image, block_size=16, threshold=0.9):
    """
    Detect copy-move forgery
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image
    block_size : int
        Size of blocks to compare
    threshold : float
        Similarity threshold (0-1)
        
    Returns:
    --------
    results : dict
        - clone_mask: Mask showing cloned regions
        - regions_found: Number of cloned regions
        - score: Suspicion score (0-100)
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    h, w = gray.shape
    
    # Simple block-matching approach
    clone_mask = np.zeros((h, w), dtype=np.uint8)
    matches = []
    
    # Divide into overlapping blocks
    step = block_size // 2
    
    blocks = []
    positions = []
    
    for i in range(0, h - block_size, step):
        for j in range(0, w - block_size, step):
            block = gray[i:i+block_size, j:j+block_size]
            blocks.append(block)
            positions.append((i, j))
    
    # Compare blocks (simplified - full implementation would use DCT or features)
    for idx1 in range(len(blocks)):
        for idx2 in range(idx1 + 1, len(blocks)):
            # Skip nearby blocks
            pos1 = positions[idx1]
            pos2 = positions[idx2]
            
            distance = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
            
            if distance < block_size * 2:
                continue
            
            # Calculate similarity
            block1 = blocks[idx1].astype(float)
            block2 = blocks[idx2].astype(float)
            
            correlation = np.corrcoef(block1.flatten(), block2.flatten())[0, 1]
            
            if correlation > threshold:
                matches.append((pos1, pos2, correlation))
                
                # Mark regions
                i1, j1 = pos1
                i2, j2 = pos2
                clone_mask[i1:i1+block_size, j1:j1+block_size] = 255
                clone_mask[i2:i2+block_size, j2:j2+block_size] = 255
    
    regions_found = len(matches)
    score = min(100, regions_found * 20)
    
    return {
        'clone_mask': clone_mask,
        'regions_found': regions_found,
        'matches': matches[:10],  # Store first 10 matches
        'score': score
    }
