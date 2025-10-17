import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt
import cv2
import numpy as np

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 + OpenCV Test")
        self.setGeometry(100, 100, 600, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Add labels
        title_label = QLabel("Old Document Restoration - Setup Test")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title_label)
        
        # Test PyQt6
        pyqt_label = QLabel("✓ PyQt6 is working!")
        pyqt_label.setStyleSheet("color: green; font-size: 14px; margin: 10px;")
        layout.addWidget(pyqt_label)
        
        # Test OpenCV
        try:
            cv_version = cv2.__version__
            cv_label = QLabel(f"✓ OpenCV {cv_version} is working!")
            cv_label.setStyleSheet("color: green; font-size: 14px; margin: 10px;")
        except:
            cv_label = QLabel("✗ OpenCV not working")
            cv_label.setStyleSheet("color: red; font-size: 14px; margin: 10px;")
        layout.addWidget(cv_label)
        
        # Test NumPy
        try:
            np_version = np.__version__
            np_label = QLabel(f"✓ NumPy {np_version} is working!")
            np_label.setStyleSheet("color: green; font-size: 14px; margin: 10px;")
        except:
            np_label = QLabel("✗ NumPy not working")
            np_label.setStyleSheet("color: red; font-size: 14px; margin: 10px;")
        layout.addWidget(np_label)
        
        # Test button
        test_button = QPushButton("Test Image Processing")
        test_button.clicked.connect(self.test_image_processing)
        test_button.setStyleSheet("padding: 10px; font-size: 14px; margin: 20px;")
        layout.addWidget(test_button)
        
        # Result label
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_label)
        
    def test_image_processing(self):
        """Test basic image processing functionality"""
        try:
            # Create a test image
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            test_image[:50, :50] = [255, 0, 0]  # Red square
            test_image[50:, 50:] = [0, 255, 0]  # Green square
            
            # Apply Gaussian blur (basic processing)
            blurred = cv2.GaussianBlur(test_image, (15, 15), 0)
            
            # If we get here, basic processing works
            self.result_label.setText("✓ Image processing test successful!\nReady for document restoration!")
            self.result_label.setStyleSheet("color: green; font-size: 14px; margin: 10px; font-weight: bold;")
            
        except Exception as e:
            self.result_label.setText(f"✗ Image processing test failed: {str(e)}")
            self.result_label.setStyleSheet("color: red; font-size: 14px; margin: 10px;")

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()