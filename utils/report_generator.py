"""
Report Generation Module

Handles:
- Generating comprehensive forensics reports
- Formatting analysis results
- Creating text and HTML reports
"""

import os
from datetime import datetime


def generate_report(image_path, analysis_results, output_format='text'):
    """
    Generate comprehensive forensics report
    
    Parameters:
    -----------
    image_path : str
        Path to analyzed image
    analysis_results : dict
        Dictionary containing all analysis results
    output_format : str
        'text' or 'html'
        
    Returns:
    --------
    report : str
        Formatted report
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = []
    report.append("="*70)
    report.append("FORENSICLENS - IMAGE MANIPULATION DETECTION REPORT")
    report.append("="*70)
    report.append(f"\nAnalysis Date: {timestamp}")
    report.append(f"Image: {os.path.basename(image_path)}")
    report.append(f"Full Path: {image_path}\n")
    report.append("="*70)
    
    # Summary scores
    report.append("\n📊 ANALYSIS SUMMARY")
    report.append("-"*70)
    
    scores = []
    
    # ELA
    if 'ela' in analysis_results:
        ela_score = analysis_results['ela'].get('score', 0)
        scores.append(ela_score)
        report.append(f"\n1. Error Level Analysis (ELA)")
        report.append(f"   Suspicion Score: {ela_score}/100")
        report.append(f"   Status: {get_status_label(ela_score)}")
    
    # JPEG
    if 'jpeg' in analysis_results:
        jpeg_score = analysis_results['jpeg'].get('score', 0)
        scores.append(jpeg_score)
        double = analysis_results['jpeg'].get('double_compressed', False)
        report.append(f"\n2. JPEG Compression Analysis")
        report.append(f"   Double Compression: {'YES ⚠️' if double else 'NO ✓'}")
        report.append(f"   Suspicion Score: {jpeg_score}/100")
        report.append(f"   Status: {get_status_label(jpeg_score)}")
    
    # Noise
    if 'noise' in analysis_results:
        noise_score = analysis_results['noise'].get('score', 0)
        scores.append(noise_score)
        report.append(f"\n3. Noise Inconsistency Analysis")
        report.append(f"   Suspicion Score: {noise_score}/100")
        report.append(f"   Status: {get_status_label(noise_score)}")
    
    # Histogram
    if 'histogram' in analysis_results:
        hist_score = analysis_results['histogram'].get('score', 0)
        scores.append(hist_score)
        manipulated = analysis_results['histogram'].get('manipulated', False)
        manip_type = analysis_results['histogram'].get('type', 'None')
        report.append(f"\n4. Histogram Manipulation Analysis")
        report.append(f"   Manipulation Detected: {'YES ⚠️' if manipulated else 'NO ✓'}")
        report.append(f"   Type: {manip_type}")
        report.append(f"   Confidence: {hist_score}/100")
    
    # Bit-depth
    if 'bitdepth' in analysis_results:
        bd_score = analysis_results['bitdepth'].get('score', 0)
        scores.append(bd_score)
        posterized = analysis_results['bitdepth'].get('posterized', False)
        report.append(f"\n5. Bit-Depth Analysis")
        report.append(f"   Posterization Detected: {'YES ⚠️' if posterized else 'NO ✓'}")
        report.append(f"   Suspicion Score: {bd_score}/100")
    
    # Clone detection
    if 'clone' in analysis_results:
        clone_score = analysis_results['clone'].get('score', 0)
        scores.append(clone_score)
        clones_found = analysis_results['clone'].get('regions_found', 0)
        report.append(f"\n6. Clone/Copy-Move Detection")
        report.append(f"   Cloned Regions Found: {clones_found}")
        report.append(f"   Suspicion Score: {clone_score}/100")

    # 6. Frequency Analysis
    if 'frequency' in analysis_results:
        freq_score = analysis_results['frequency'].get('score', 0)
        scores.append(freq_score)
        periodic = analysis_results['frequency'].get('periodic_detected', False)
        num_peaks = analysis_results['frequency'].get('num_peaks', 0)
        report.append(f"\n6. Frequency Domain Analysis")
        report.append(f"   Periodic Patterns: {'YES ⚠️' if periodic else 'NO ✓'}")
        report.append(f"   Frequency Peaks: {num_peaks}")
        report.append(f"   Suspicion Score: {freq_score}/100")
    
    # 7. Contrast Analysis
    if 'contrast' in analysis_results:
        contrast_score = analysis_results['contrast'].get('score', 0)
        scores.append(contrast_score)
        inconsistent = analysis_results['contrast'].get('inconsistent', False)
        report.append(f"\n7. Contrast Manipulation Analysis")
        report.append(f"   Inconsistent Contrast: {'YES ⚠️' if inconsistent else 'NO ✓'}")
        report.append(f"   Suspicion Score: {contrast_score}/100")
        report.append(f"   Status: {get_status_label(contrast_score)}")

    # 8. Blur Analysis
    if 'blur' in analysis_results:
        blur_score = analysis_results['blur'].get('score', 0)
        scores.append(blur_score)
        inconsistent = analysis_results['blur'].get('inconsistent', False)
        report.append(f"\n8. Blur Inconsistency Analysis")
        report.append(f"   Inconsistent Blur: {'YES ⚠️' if inconsistent else 'NO ✓'}")
        report.append(f"   Suspicion Score: {blur_score}/100")
        report.append(f"   Status: {get_status_label(blur_score)}")
    
    # 9. Bias Field (Lighting)
    if 'bias_field' in analysis_results:
        lighting_score = analysis_results['bias_field'].get('score', 0)
        scores.append(lighting_score)
        inconsistent = analysis_results['bias_field'].get('inconsistent', False)
        report.append(f"\n9. Lighting Inconsistency Analysis")
        report.append(f"   Inconsistent Lighting: {'YES ⚠️' if inconsistent else 'NO ✓'}")
        report.append(f"   Suspicion Score: {lighting_score}/100")
        report.append(f"   Status: {get_status_label(lighting_score)}")        
    
    # Overall verdict
    report.append("\n" + "="*70)
    report.append("🔍 OVERALL VERDICT")
    report.append("="*70)
    
    if scores:
        avg_score = sum(scores) / len(scores)
        report.append(f"\nAverage Suspicion Score: {avg_score:.1f}/100\n")
        
        if avg_score > 70:
            report.append("🚨 HIGH PROBABILITY OF MANIPULATION")
            report.append("   Recommendation: Image is likely manipulated")
            report.append("   Multiple forensic indicators detected")
        elif avg_score > 40:
            report.append("⚠️  MODERATE SUSPICION")
            report.append("   Recommendation: Further investigation recommended")
            report.append("   Some forensic indicators present")
        else:
            report.append("✅ LOW PROBABILITY OF MANIPULATION")
            report.append("   Recommendation: Image appears authentic")
            report.append("   Few forensic indicators detected")
    
    report.append("\n" + "="*70)
    report.append("End of Report")
    report.append("="*70)
    
    return "\n".join(report)


def get_status_label(score):
    """
    Get status label based on score
    
    Parameters:
    -----------
    score : float
        Suspicion score (0-100)
        
    Returns:
    --------
    label : str
        Status label
    """
    if score > 70:
        return "🚨 HIGH SUSPICION"
    elif score > 40:
        return "⚠️  MODERATE"
    else:
        return "✓ NORMAL"


def save_report(report_text, output_path):
    """
    Save report to file
    
    Parameters:
    -----------
    report_text : str
        Report content
    output_path : str
        Path to save report
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"✓ Report saved: {output_path}")
