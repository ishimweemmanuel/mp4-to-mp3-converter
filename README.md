# MP4 to MP3 Converter

A modern, user-friendly desktop application for converting MP4 videos to MP3 audio files. Built with Python and PyQt5, this application provides an efficient way to extract and convert audio from video files.

![MP4 to MP3 Converter]

## Features

- **Modern User Interface**: Clean, intuitive design with a side-by-side layout
- **Drag and Drop Support**: Easily add files by dragging them into the application
- **Batch Processing**: Convert multiple files simultaneously
- **Parallel Processing**: Convert up to 3 files at the same time for faster completion
- **Progress Tracking**: Individual progress bars for each file
- **Quality Settings**:
  - Adjustable bitrate (128k, 192k, 256k, 320k)
  - Configurable frequency (44.1kHz, 48kHz, 96kHz)
- **File Information**: Display file sizes and total batch size
- **Offline Processing**: All conversions happen locally on your machine

## Installation

1. Clone this repository or download the source code:
```bash
git clone https://github.com/yourusername/mp4-to-mp3-converter.git
cd mp4-to-mp3-converter
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python mp4_to_mp3_converter.py
```

2. Add MP4 files using one of these methods:
   - Drag and drop files into the application window
   - Click the "Add Files" button to browse
   - Click the drop zone to select files

3. Configure conversion settings (optional):
   - Select desired bitrate for output quality
   - Choose appropriate frequency

4. Click "Convert All" to start the conversion process

5. Converted MP3 files will be saved in:
```
C:\Users\ISHIMWEEmmanuel\Music\converted
```

## Requirements

- Python 3.6 or higher
- PyQt5
- moviepy
- See requirements.txt for complete list

## Technical Details

- Built with PyQt5 for the GUI
- Uses moviepy for audio extraction and conversion
- Implements multithreading for parallel processing
- Supports drag and drop file operations
- Real-time progress tracking

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PyQt5 for the GUI framework
- moviepy for video/audio processing
- All contributors and users of this application
