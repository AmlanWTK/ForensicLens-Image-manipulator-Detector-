"""
Forensic Analysis Modules

Each module implements a specific image forensics technique
"""

from .histogram_analysis import analyze_histogram_manipulation
from .error_level_analysis import perform_ela
from .noise_analysis import analyze_noise_inconsistency
from .bit_depth_analysis import analyze_bit_depth
from .clone_detection import detect_copy_move
from .frequency_analysis import analyze_frequency_domain
from .contrast_analysis import analyze_contrast_manipulation
from .blur_analysis import analyze_blur_inconsistency
from .bias_field_analysis import analyze_lighting_inconsistency

__all__ = [
    'analyze_histogram_manipulation',
    'perform_ela',
    'analyze_noise_inconsistency',
    'analyze_bit_depth',
    'detect_copy_move',
    'analyze_frequency_domain',
    'analyze_contrast_manipulation',
    'analyze_blur_inconsistency',
    'analyze_lighting_inconsistency'
]
