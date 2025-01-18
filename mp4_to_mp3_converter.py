import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QProgressBar, QComboBox, QStyle, QListWidget,
                            QListWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPalette, QColor
from moviepy.editor import VideoFileClip
import threading
from concurrent.futures import ThreadPoolExecutor

class AudioConverter(QThread):
    progress = pyqtSignal(str, int)  # file_path, progress value
    finished = pyqtSignal(str)
    error = pyqtSignal(str, str)  # file_path, error message

    def __init__(self, video_path, output_path, bitrate, frequency):
        super().__init__()
        self.video_path = video_path
        self.output_path = output_path
        self.bitrate = bitrate
        self.frequency = frequency

    def run(self):
        try:
            video = VideoFileClip(self.video_path)
            audio = video.audio
            
            filename = os.path.splitext(os.path.basename(self.video_path))[0]
            output_file = os.path.join(self.output_path, f"{filename}.mp3")
            
            # Convert and export with progress updates
            audio.write_audiofile(output_file, 
                                bitrate=self.bitrate,
                                fps=self.frequency,
                                logger=None)
            
            video.close()
            audio.close()
            
            self.finished.emit(self.video_path)
        except Exception as e:
            self.error.emit(self.video_path, str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP4 to MP3 Converter")
        self.setMinimumSize(800, 600)
        
        # Initialize variables
        self.files_to_convert = []
        self.output_directory = r"C:\Users\ISHIMWEEmmanuel\Music\converted"
        os.makedirs(self.output_directory, exist_ok=True)
        
        self.converters = {}  # Store converter threads
        self.progress_bars = {}  # Store progress bars for each file
        
        self.init_ui()
        
        # Accept drops
        self.setAcceptDrops(True)
        
        # Thread pool for parallel conversion
        self.thread_pool = ThreadPoolExecutor(max_workers=3)  # Convert up to 3 files simultaneously

    def init_ui(self):
        # Set the application style
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton {
                background-color: #333;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton:pressed {
                background-color: #222;
            }
            QPushButton:disabled {
                background-color: #999;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #666;
                padding: 4px;
                border-radius: 4px;
            }
            QComboBox:hover {
                border-color: #888;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: rgba(128, 128, 128, 0.1);
                height: 16px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #444;
                border-radius: 4px;
            }
            QListWidget {
                border: 1px solid #666;
                border-radius: 4px;
                padding: 5px;
                background: white;
                min-width: 300px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background: rgba(128, 128, 128, 0.1);
                color: black;
            }
            QLabel#FileCountLabel {
                color: #666;
                font-size: 12px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)  # Changed to horizontal layout
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Left side - File List Section
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)

        # Files section title
        files_header = QWidget()
        files_header_layout = QHBoxLayout(files_header)
        files_header_layout.setContentsMargins(0, 0, 0, 0)
        
        files_title = QLabel("Files to Convert")
        files_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        files_header_layout.addWidget(files_title)
        
        self.file_count_label = QLabel("0 files")
        self.file_count_label.setObjectName("FileCountLabel")
        self.file_count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        files_header_layout.addWidget(self.file_count_label)
        
        left_layout.addWidget(files_header)

        # File list
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(400)
        left_layout.addWidget(self.file_list)

        # Add files button
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.select_files)
        add_files_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                padding: 10px;
                font-size: 14px;
            }
        """)
        left_layout.addWidget(add_files_btn)

        main_layout.addWidget(left_widget)

        # Right side - Controls Section
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        # App title
        title_label = QLabel("MP4 to MP3 Converter")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(title_label)

        # Drop area
        self.drop_label = QLabel("Drag and drop MP4 files here\nor click to select files")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #666;
                border-radius: 12px;
                padding: 30px;
                background: rgba(128, 128, 128, 0.1);
                font-size: 16px;
                margin: 20px 0;
            }
            QLabel:hover {
                background: rgba(128, 128, 128, 0.15);
                border-color: #888;
            }
        """)
        self.drop_label.mousePressEvent = self.select_files
        right_layout.addWidget(self.drop_label)

        # Settings group
        settings_group = QWidget()
        settings_group.setStyleSheet("""
            QWidget {
                background: rgba(128, 128, 128, 0.1);
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                font-weight: bold;
                margin-bottom: 5px;
            }
        """)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(15)
        
        # Bitrate selection
        bitrate_label = QLabel("Bitrate:")
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(['128k', '192k', '256k', '320k'])
        self.bitrate_combo.setCurrentText('192k')
        settings_layout.addWidget(bitrate_label)
        settings_layout.addWidget(self.bitrate_combo)
        
        # Frequency selection
        freq_label = QLabel("Frequency:")
        self.freq_combo = QComboBox()
        self.freq_combo.addItems(['44100', '48000', '96000'])
        self.freq_combo.setCurrentText('44100')
        settings_layout.addWidget(freq_label)
        settings_layout.addWidget(self.freq_combo)
        
        right_layout.addWidget(settings_group)

        # Output directory info
        output_label = QLabel(f"Output Directory:\n{self.output_directory}")
        output_label.setStyleSheet("color: #666; padding: 10px;")
        output_label.setWordWrap(True)
        right_layout.addWidget(output_label)

        # Convert button
        self.convert_btn = QPushButton("Convert All")
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                padding: 15px;
                font-size: 16px;
                margin-top: 10px;
            }
        """)
        self.convert_btn.clicked.connect(self.start_conversion)
        right_layout.addWidget(self.convert_btn)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 10px;
                color: #666;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.status_label)

        # Add stretch to push everything up
        right_layout.addStretch()
        
        main_layout.addWidget(right_widget)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()
                if url.toLocalFile().lower().endswith('.mp4')]
        if files:
            self.add_files(files)

    def add_files(self, files):
        for file_path in files:
            if file_path not in self.files_to_convert:
                self.files_to_convert.append(file_path)
                
                # Create list item with progress bar
                item_widget = QWidget()
                item_layout = QVBoxLayout(item_widget)
                item_layout.setSpacing(5)
                
                # File info layout
                file_info_layout = QHBoxLayout()
                
                # File name label
                file_name = os.path.basename(file_path)
                file_label = QLabel(file_name)
                file_label.setStyleSheet("font-weight: bold;")
                file_info_layout.addWidget(file_label)
                
                # File size
                size_bytes = os.path.getsize(file_path)
                size_mb = size_bytes / (1024 * 1024)
                size_label = QLabel(f"{size_mb:.1f} MB")
                size_label.setStyleSheet("color: #666;")
                file_info_layout.addWidget(size_label)
                
                item_layout.addLayout(file_info_layout)
                
                # Progress bar
                progress_bar = QProgressBar()
                progress_bar.setVisible(False)
                self.progress_bars[file_path] = progress_bar
                item_layout.addWidget(progress_bar)
                
                # Add to list
                item = QListWidgetItem()
                item.setSizeHint(item_widget.sizeHint())
                self.file_list.addItem(item)
                self.file_list.setItemWidget(item, item_widget)

        self.update_ui_state()

    def select_files(self, event):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select MP4 Files", "",
            "MP4 Files (*.mp4);;All Files (*.*)")
        if files:
            self.add_files(files)

    def update_ui_state(self):
        file_count = len(self.files_to_convert)
        self.convert_btn.setEnabled(file_count > 0)
        self.file_count_label.setText(f"{file_count} file{'s' if file_count != 1 else ''}")
        
        if file_count > 0:
            total_size = sum(os.path.getsize(f) for f in self.files_to_convert)
            total_size_mb = total_size / (1024 * 1024)
            self.status_label.setText(f"Total size: {total_size_mb:.1f} MB")
        else:
            self.status_label.setText("")

    def start_conversion(self):
        if not self.files_to_convert:
            self.status_label.setText("Please select MP4 files first!")
            return

        self.convert_btn.setEnabled(False)
        self.status_label.setText("Converting files...")

        # Start conversion for all files
        for file_path in self.files_to_convert[:]:
            self.convert_file(file_path)

    def convert_file(self, file_path):
        # Show progress bar for this file
        if file_path in self.progress_bars:
            self.progress_bars[file_path].setVisible(True)
            self.progress_bars[file_path].setValue(0)

        converter = AudioConverter(
            file_path,
            self.output_directory,
            self.bitrate_combo.currentText(),
            int(self.freq_combo.currentText())
        )
        
        converter.progress.connect(lambda f, v: self.update_progress(f, v))
        converter.finished.connect(lambda f: self.file_converted(f))
        converter.error.connect(lambda f, e: self.conversion_error(f, e))
        
        self.converters[file_path] = converter
        converter.start()

    def update_progress(self, file_path, value):
        if file_path in self.progress_bars:
            self.progress_bars[file_path].setValue(value)

    def file_converted(self, file_path):
        # Remove from list and clean up
        if file_path in self.files_to_convert:
            self.files_to_convert.remove(file_path)
            
        if file_path in self.converters:
            del self.converters[file_path]

        # Remove the item from the list widget
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            widget = self.file_list.itemWidget(item)
            if widget.findChild(QLabel).text() == os.path.basename(file_path):
                self.file_list.takeItem(i)
                break

        if not self.files_to_convert:
            self.conversion_complete()

    def conversion_error(self, file_path, error):
        self.status_label.setText(f"Error converting {os.path.basename(file_path)}: {error}")
        self.file_converted(file_path)  # Remove the file from the list

    def conversion_complete(self):
        self.status_label.setText("All conversions completed!")
        self.convert_btn.setEnabled(True)
        self.update_ui_state()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
