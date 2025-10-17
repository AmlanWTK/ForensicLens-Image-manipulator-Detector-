"""
Histogram Analysis Module

Techniques Implemented:
- Histogram Equalization Detection
- Histogram Clipping Detection
- Contrast Shift Detection
- Tone Mapping Detection

Image Processing Topics Covered:
✓ Histogram Equalization
✓ Histogram Clipping Transform
✓ Contrast Shift
"""

import cv2
import numpy as np
from scipy import stats, signal


def analyze_histogram_manipulation(image):
    """
    Detect histogram-based manipulations
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image (RGB or Grayscale)
        
    Returns:
    --------
    results : dict
        Dictionary containing:
        - manipulated: bool
        - type: str (type of manipulation detected)
        - score: float (0-100 confidence score)
        - histogram_data: dict (histogram information)
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    # Calculate histogram
    hist, bins = np.histogram(gray.flatten(), bins=256, range=[0, 256])
    hist_normalized = hist / np.sum(hist)
    
    results = {
        'manipulated': False,
        'type': 'None',
        'score': 0,
        'histogram_data': {
            'hist': hist,
            'bins': bins,
            'normalized': hist_normalized
        }
    }
    
    # Test 1: Histogram Equalization Detection
    equalization_score = detect_histogram_equalization(hist_normalized)
    
    # Test 2: Histogram Clipping Detection
    clipping_score = detect_histogram_clipping(hist, gray)
    
    # Test 3: Contrast Shift Detection
    contrast_score = detect_contrast_manipulation(hist_normalized)
    
    # Test 4: Posterization Detection
    posterization_score = detect_posterization(hist)
    
    # Determine overall result
    scores = {
        'Histogram Equalization': equalization_score,
        'Histogram Clipping': clipping_score,
        'Contrast Enhancement': contrast_score,
        'Posterization': posterization_score
    }
    
    max_score_type = max(scores, key=scores.get)
    max_score = scores[max_score_type]
    
    if max_score > 40:
        results['manipulated'] = True
        results['type'] = max_score_type
        results['score'] = int(max_score)
    
    # Store individual scores
    results['histogram_data']['individual_scores'] = scores
    
    return results


def detect_histogram_equalization(hist_normalized):
    """
    Detect if histogram equalization was applied
    
    Equalized histograms tend to be more uniform/flat
    
    Parameters:
    -----------
    hist_normalized : numpy.ndarray
        Normalized histogram
        
    Returns:
    --------
    score : float
        Detection confidence (0-100)
    """
    # Calculate histogram uniformity
    # Perfectly equalized histogram would be completely flat
    ideal_uniform = np.ones_like(hist_normalized) / len(hist_normalized)
    
    # Chi-square test for uniformity
    chi_square = np.sum((hist_normalized - ideal_uniform)**2 / (ideal_uniform + 1e-10))
    
    # Normalize chi-square to 0-100 scale
    # Lower chi-square = more uniform = likely equalized
    uniformity = 1 / (1 + chi_square / 100)
    
    # Also check standard deviation (lower = more uniform)
    std_score = 1 - np.std(hist_normalized) / np.mean(hist_normalized)
    
    # Combined score
    score = (uniformity * 0.6 + std_score * 0.4) * 100
    
    return score


def detect_histogram_clipping(hist, gray_image):
    """
    Detect histogram clipping (contrast stretching artifacts)
    
    Clipping manifests as:
    - Peaks at extremes (0 and 255)
    - Gaps in histogram
    
    Parameters:
    -----------
    hist : numpy.ndarray
        Histogram counts
    gray_image : numpy.ndarray
        Grayscale image
        
    Returns:
    --------
    score : float
        Detection confidence (0-100)
    """
    total_pixels = np.sum(hist)
    
    # Check for peaks at extremes
    black_peak = hist[0] / total_pixels
    white_peak = hist[255] / total_pixels
    
    extreme_peak_score = (black_peak + white_peak) * 100
    
    # Check for gaps in histogram (sign of clipping)
    # Ignore first and last 5 bins
    middle_hist = hist[5:250]
    zero_bins = np.sum(middle_hist == 0)
    gap_ratio = zero_bins / len(middle_hist)
    gap_score = gap_ratio * 100
    
    # Check dynamic range usage
    non_zero_bins = np.count_nonzero(hist)
    range_usage = non_zero_bins / 256
    
    # Low range usage with extreme peaks = likely clipped
    if range_usage < 0.7 and (black_peak > 0.02 or white_peak > 0.02):
        clipping_score = max(extreme_peak_score, gap_score) * 1.5
    else:
        clipping_score = (extreme_peak_score + gap_score) / 2
    
    return min(100, clipping_score)


def detect_contrast_manipulation(hist_normalized):
    """
    Detect contrast enhancement/reduction
    
    Manipulated contrast shows:
    - Bimodal distributions
    - Stretched histograms
    - Compressed histograms
    
    Parameters:
    -----------
    hist_normalized : numpy.ndarray
        Normalized histogram
        
    Returns:
    --------
    score : float
        Detection confidence (0-100)
    """
    # Calculate histogram spread (kurtosis and skewness)
    bins_centers = np.arange(256)
    
    # Calculate moments
    mean = np.sum(bins_centers * hist_normalized)
    variance = np.sum(((bins_centers - mean) ** 2) * hist_normalized)
    std = np.sqrt(variance)
    
    # Skewness (asymmetry)
    skewness = np.sum(((bins_centers - mean) ** 3) * hist_normalized) / (std ** 3 + 1e-10)
    
    # Kurtosis (tailedness)
    kurtosis = np.sum(((bins_centers - mean) ** 4) * hist_normalized) / (std ** 4 + 1e-10)
    
    # Normal distribution has kurtosis ~3
    # High kurtosis = heavy tails = possible contrast stretch
    # Low kurtosis = light tails = possible contrast compression
    kurtosis_deviation = abs(kurtosis - 3)
    
    # High skewness = asymmetric contrast adjustment
    skewness_score = abs(skewness) * 20
    
    # Detect bimodal distribution (sign of local contrast enhancement)
    smoothed_hist = signal.savgol_filter(hist_normalized, 21, 3)
    peaks = signal.find_peaks(smoothed_hist, height=np.max(smoothed_hist) * 0.1)[0]
    
    bimodal_score = 0
    if len(peaks) >= 2:
        bimodal_score = 50
    
    # Combined score
    score = min(100, skewness_score + kurtosis_deviation * 10 + bimodal_score)
    
    return score


def detect_posterization(hist):
    """
    Detect posterization (bit-depth reduction)
    
    Posterized images show regular peaks in histogram
    
    Parameters:
    -----------
    hist : numpy.ndarray
        Histogram counts
        
    Returns:
    --------
    score : float
        Detection confidence (0-100)
    """
    # Find peaks in histogram
    smoothed = signal.savgol_filter(hist.astype(float), 11, 2)
    peaks = signal.find_peaks(smoothed, height=np.max(smoothed) * 0.05)[0]
    
    if len(peaks) < 4:
        return 0
    
    # Check if peaks are regularly spaced
    peak_spacing = np.diff(peaks)
    
    if len(peak_spacing) < 2:
        return 0
    
    # Calculate regularity (low std = regular spacing)
    spacing_mean = np.mean(peak_spacing)
    spacing_std = np.std(peak_spacing)
    
    if spacing_mean == 0:
        return 0
    
    regularity = 1 - (spacing_std / spacing_mean)
    
    # High regularity + multiple peaks = likely posterized
    if regularity > 0.7 and len(peaks) >= 4:
        score = regularity * len(peaks) * 10
    else:
        score = regularity * 30
    
    return min(100, score)


def visualize_histogram_analysis(image, results):
    """
    Create visualization of histogram analysis
    
    Parameters:
    -----------
    image : numpy.ndarray
        Original image
    results : dict
        Analysis results
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Visualization figure
    """
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Original image
    if len(image.shape) == 3:
        axes[0, 0].imshow(image)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        axes[0, 0].imshow(image, cmap='gray')
        gray = image
    axes[0, 0].set_title('Original Image', fontweight='bold')
    axes[0, 0].axis('off')
    
    # Histogram
    hist_data = results['histogram_data']
    axes[0, 1].bar(hist_data['bins'][:-1], hist_data['hist'], 
                   width=1, color='steelblue', alpha=0.7)
    axes[0, 1].set_title('Intensity Histogram', fontweight='bold')
    axes[0, 1].set_xlabel('Pixel Intensity')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Cumulative histogram
    cumulative = np.cumsum(hist_data['hist'])
    axes[1, 0].plot(hist_data['bins'][:-1], cumulative, 
                    color='darkred', linewidth=2)
    axes[1, 0].set_title('Cumulative Histogram', fontweight='bold')
    axes[1, 0].set_xlabel('Pixel Intensity')
    axes[1, 0].set_ylabel('Cumulative Frequency')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Results summary
    axes[1, 1].axis('off')
    summary_text = f"""
    HISTOGRAM ANALYSIS RESULTS
    
    Manipulation Detected: {results['manipulated']}
    Type: {results['type']}
    Confidence Score: {results['score']}/100
    
    Individual Scores:
    """
    
    for test_name, score in hist_data['individual_scores'].items():
        summary_text += f"\n  • {test_name}: {score:.1f}/100"
    
    axes[1, 1].text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
                   verticalalignment='center',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    return fig
