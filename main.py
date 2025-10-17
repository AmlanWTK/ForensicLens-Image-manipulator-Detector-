"""
ForensicLens - Main Application

Simple GUI for image forensics analysis
"""

import sys
import os
import cv2
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Import our modules
from utils.image_loader import load_image
from utils.visualization import create_heatmap, display_side_by_side
from utils.report_generator import generate_report, save_report

from modules.histogram_analysis import analyze_histogram_manipulation
from modules.error_level_analysis import perform_ela
from modules.noise_analysis import analyze_noise_inconsistency
from modules.bit_depth_analysis import analyze_bit_depth
from modules.clone_detection import detect_copy_move
from modules.frequency_analysis import analyze_frequency_domain
from modules.contrast_analysis import analyze_contrast_manipulation
from modules.blur_analysis import analyze_blur_inconsistency
from modules.bias_field_analysis import analyze_lighting_inconsistency



class AnalysisWorker(QThread):
    """Worker thread for analysis"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int, str)
    
    def __init__(self, image_path, image):
        super().__init__()
        self.image_path = image_path
        self.image = image
    
    def run(self):
        results = {}
        
        # 1. Histogram Analysis
        self.progress.emit(10, "Analyzing histogram...")
        results['histogram'] = analyze_histogram_manipulation(self.image)
        
        # 2. ELA
        self.progress.emit(25, "Running ELA...")
        results['ela'] = perform_ela(self.image_path)
        
        # 3. Noise Analysis
        self.progress.emit(40, "Analyzing noise...")
        results['noise'] = analyze_noise_inconsistency(self.image)
        
        # 4. Bit-Depth
        self.progress.emit(55, "Checking bit-depth...")
        results['bitdepth'] = analyze_bit_depth(self.image)
        
        # 5. Clone Detection
        # self.progress.emit(70, "Detecting clones...")
        #results['clone'] = detect_copy_move(self.image)
        
        # 6. Frequency Analysis
        self.progress.emit(85, "Frequency analysis...")
        results['frequency'] = analyze_frequency_domain(self.image)

         # 7. Contrast Analysis
        self.progress.emit(64, "Analyzing contrast...")
        results['contrast'] = analyze_contrast_manipulation(self.image)
    
        # 8. Blur Analysis
        self.progress.emit(76, "Checking blur...")
        results['blur'] = analyze_blur_inconsistency(self.image)
    
       # 9. Bias Field Analysis
        self.progress.emit(88, "Analyzing lighting...")
        results['bias_field'] = analyze_lighting_inconsistency(self.image)
        
        self.progress.emit(100, "Complete!")
        self.finished.emit(results)


class ForensicLensApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_path = None
        self.image = None
        self.results = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('ForensicLens - Image Manipulation Detector')
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel('🔍 ForensicLens - Image Manipulation Detector')
        title.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        load_btn = QPushButton('📁 Load Image')
        load_btn.clicked.connect(self.load_image)
        load_btn.setMinimumHeight(40)
        
        self.analyze_btn = QPushButton('🔬 Analyze')
        self.analyze_btn.clicked.connect(self.analyze)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setMinimumHeight(40)
        
        self.save_btn = QPushButton('💾 Save Report')
        self.save_btn.clicked.connect(self.save_results)
        self.save_btn.setEnabled(False)
        self.save_btn.setMinimumHeight(40)
        
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(self.analyze_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)
        
        # Progress
        self.progress_label = QLabel('Ready')
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(800, 500)
        self.image_label.setStyleSheet("border: 2px solid gray;")
        layout.addWidget(self.image_label)
        
        # Results
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        layout.addWidget(self.results_text)
        
        self.show()
    
    def load_image(self):
        """Load image"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", 
            "Images (*.jpg *.jpeg *.png *.bmp)"
        )
        
        if path:
            self.image_path = path
            self.image = load_image(path, color_mode='rgb')
            
            # Display
            self.display_image(self.image)
            
            self.analyze_btn.setEnabled(True)
            self.progress_label.setText(f'Loaded: {os.path.basename(path)}')
    
    def display_image(self, img):
        """Display image in label"""
        h, w = img.shape[:2]
        scale = min(800/w, 500/h, 1.0)
        new_w, new_h = int(w*scale), int(h*scale)
        
        img_resized = cv2.resize(img, (new_w, new_h))
        
        qimg = QImage(img_resized.data, new_w, new_h, new_w*3, 
                      QImage.Format.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg))
    
    def analyze(self):
        """Run analysis"""
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # Start worker
        self.worker = AnalysisWorker(self.image_path, self.image)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.analysis_done)
        self.worker.start()
    
    def update_progress(self, value, msg):
        """Update progress"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(msg)
    
    def analysis_done(self, results):
        """Handle results"""
        self.results = results
        self.analyze_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        
        # Generate and display report
        report = generate_report(self.image_path, results)
        self.results_text.setText(report)
        
        # Save visualizations
        output_dir = 'samples/output'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save heatmaps
        if 'ela' in results:
            ela_heatmap = create_heatmap(results['ela']['ela_enhanced'])
            cv2.imwrite(f'{output_dir}/ela_heatmap.png', 
                       cv2.cvtColor(ela_heatmap, cv2.COLOR_RGB2BGR))
        
        if 'noise' in results:
            noise_heatmap = create_heatmap(results['noise']['noise_map'])
            cv2.imwrite(f'{output_dir}/noise_heatmap.png', 
                       cv2.cvtColor(noise_heatmap, cv2.COLOR_RGB2BGR))
        
        self.progress_label.setText('✓ Analysis complete! Results saved to samples/output/')
    
    def save_results(self):
        """Save report"""
        if self.results is None:
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "forensics_report.txt", 
            "Text Files (*.txt)"
        )
        
        if path:
            report = generate_report(self.image_path, self.results)
            save_report(report, path)
            self.progress_label.setText(f'✓ Report saved: {path}')


def main():
    app = QApplication(sys.argv)
    window = ForensicLensApp()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
