# Employee Face Recognition System

A comprehensive Flask-based web application for real-time employee face detection and recognition using computer vision and machine learning. This system supports multiple camera feeds, video analysis, and provides a complete surveillance solution for security applications.

## 🚀 Features

- **Real-time Face Detection**: Live camera feed analysis for instant employee identification
- **CCTV/Camera Feed Integration**: Connect to external cameras, IP cameras, RTSP streams, and CCTV systems
- **Video Upload & Analysis**: Process uploaded video files for face detection
- **Employee Database Management**: Add, edit, and delete employee records with facial data
- **Detection Logging**: Track and view all detection events with timestamps and confidence scores
- **Web-based Interface**: User-friendly web interface for all operations
- **Face Encoding Storage**: Secure storage of facial encodings in SQLite database
- **Multi-Camera Support**: Monitor multiple camera feeds simultaneously
- **Real-time Notifications**: Instant alerts when employees are detected
- **Confidence Scoring**: Advanced face recognition with confidence metrics
- **Production Ready**: WSGI server support for deployment

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Computer Vision**: OpenCV, face_recognition library
- **Image Processing**: PIL (Python Imaging Library)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **File Handling**: Werkzeug for secure file uploads
<!-- - **Production Server**: Gunicorn WSGI server -->

## 📋 Prerequisites

Before running this application, make sure you have:

- Python 3.7 or higher
- pip (Python package installer)
- Webcam (for live detection) - optional in WSL
- Sufficient disk space for image/video uploads
- Network access (for IP cameras and RTSP streams)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd employee-face-recognition
```

### 2. Create Virtual Environment
```bash
# On Windows
python -m venv venv

# On Linux/macOS
python3 -m venv venv
```

### 3. Activate Virtual Environment

**On Windows:**
```cmd
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Install Additional System Dependencies (if needed)

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-dev cmake build-essential
sudo apt-get install libopencv-dev python3-opencv
```

**On macOS:**
```bash
brew install cmake
brew install opencv
```

## 🏃‍♂️ Running the Application

### Quick Start (Recommended)
Use the provided startup script for automatic checks and setup:

**On Windows:**
```cmd
start.bat
```

**On Linux/macOS:**
```bash
./start.sh
```

### Manual Start
1. **Start the Flask application**:
   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **The application will redirect you to the live detection page** by default.

### Production Deployment
For production use, install production dependencies and use a WSGI server:

```bash
pip install -r requirements-prod.txt
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## 📖 Usage Guide

### 1. Adding Employees
- Navigate to the "Add Employee" page
- Fill in the required information:
  - Name
  - Employee ID
  - Description (optional)
  - Upload a clear face image
- The system will automatically encode the face and store it in the database

### 2. Live Detection
- Access the live detection page
- Allow camera permissions when prompted
- The system will analyze the video feed in real-time
- Detected employees will be highlighted with bounding boxes and names
- Detection events are automatically logged

### 3. CCTV/Camera Feed Detection
- Navigate to "Camera Feeds" in the navigation menu
- Add new camera feeds with different types:
  - **Local Device**: Built-in or USB cameras (device index: 0, 1, 2...)
  - **RTSP Stream**: Real-time streaming protocol cameras
  - **IP Camera**: Network cameras accessible via HTTP/HTTPS
  - **CCTV System**: Professional surveillance system cameras
- Test camera connections before starting detection
- Start detection on any camera feed to monitor for employees
- Real-time notifications and detection logs with confidence scores

### 4. Video Upload & Analysis
- Upload a video file through the web interface
- The system will process the video frame by frame
- Detection results will be displayed in real-time

### 5. Managing Employee Database
- View all registered employees in the database
- Edit employee information and images
- Delete employee records when needed

### 6. Viewing Detection Logs
- Access the detection logs page to view all detection events
- Logs include timestamps, employee names, detection types, camera feed information, and confidence scores

## 🗂️ Project Structure

```
employee-face-recognition/
├── app.py                 # Main Flask application
├── wsgi.py               # Production WSGI entry point
├── config.py             # Configuration settings
├── requirements.txt      # Development dependencies
├── requirements-prod.txt # Production dependencies
├── start.bat            # Windows startup script
├── start.sh             # Linux/macOS startup script
├── README.md            # This file
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── add_employee.html # Add employee form
│   ├── employees.html   # Employee management page
│   ├── live_detection.html # Live detection interface
│   ├── upload_video.html # Video upload page
│   ├── detection_logs.html # Detection logs page
│   ├── add_camera_feed.html # Add camera feed form
│   ├── camera_feeds.html # Camera feeds management page
│   └── cctv_detection.html # CCTV detection interface
├── static/              # Static files
│   └── uploads/         # Uploaded images and videos
├── instance/            # Database files (auto-generated)
└── venv/                # Virtual environment
```

## 🔧 Configuration

The application uses the following default configurations:

- **Database**: SQLite database stored in `instance/database.db`
- **Upload Folder**: `static/uploads/`
- **Secret Key**: Change `'your_secret_key_here'` in `app.py` for production
- **Face Recognition Tolerance**: 0.5 (adjustable in the code)

### Camera Feed Configuration

The system supports various camera types:

- **Local Device**: Use device indices (0, 1, 2...) for built-in or USB cameras
- **RTSP Stream**: Format: `rtsp://username:password@ip:port/stream`
- **IP Camera**: Format: `http://ip:port/video` or `https://ip:port/video`
- **CCTV System**: Format: `rtsp://admin:password@192.168.1.100:554/stream1`

Common RTSP URLs for popular camera brands:
- **Hikvision**: `rtsp://admin:password@ip:554/Streaming/Channels/101`
- **Dahua**: `rtsp://admin:password@ip:554/cam/realmonitor?channel=1&subtype=0`
- **Axis**: `rtsp://username:password@ip:554/axis-media/media.amp`

### Environment Variables

For production deployment, set these environment variables:

```bash
export SECRET_KEY="your-secure-secret-key"
export DATABASE_URL="sqlite:///path/to/database.db"
export FLASK_ENV="production"
```

## 🛡️ Security Considerations

- **File Upload Security**: Only image files (PNG, JPG, JPEG) are allowed
- **Secure Filenames**: Uploaded files are sanitized using `secure_filename()`
- **Database Security**: Face encodings are stored as binary data
- **Input Validation**: All user inputs are validated before processing
- **Production Security**: Use environment variables for sensitive data
- **HTTPS**: Always use HTTPS in production environments

## 🐛 Troubleshooting

### Common Issues:

1. **"Command not found: python"**
   - Use `python3` instead of `python`
   - Ensure virtual environment is activated

2. **Camera not working (WSL/Development)**
   - **WSL Users**: Camera access is limited in WSL. Use video upload or external camera feeds instead
   - **Development**: Check camera permissions in your browser
   - **Production**: Ensure camera drivers are properly installed
   - The system will show an error frame if no camera is available

3. **Face detection not working**
   - Ensure uploaded images contain clear, front-facing faces
   - Check lighting conditions for live detection
   - Verify face_recognition library is properly installed

4. **Camera feed connection issues**
   - Verify camera URL/credentials are correct
   - Test camera connection using the "Test Connection" button
   - Ensure camera is accessible from the network (for IP cameras)
   - Check firewall settings for RTSP streams

5. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Activate virtual environment before running
   - Update setuptools: `pip install --upgrade setuptools`

6. **Development server warning**
   - This is normal for development. Use `gunicorn` for production
   - Install production requirements: `pip install -r requirements-prod.txt`

### Performance Tips:

- Use high-quality images for better face encoding
- Ensure good lighting for live detection
- Close unnecessary applications to free up system resources
- Use SSD storage for better database performance
- Monitor system resources during multi-camera operations

### WSL-Specific Issues:

- Camera access is limited in WSL environments
- Use video upload functionality instead of live camera
- External camera feeds (IP cameras, RTSP) work normally
- Consider using Windows native Python for camera access

## �� API Endpoints

### Employee Management
- `POST /add_employee` - Add new employee record
- `GET /employees` - List all employees
- `POST /edit_employee/<id>` - Edit employee record
- `POST /delete_employee/<id>` - Delete employee record

### Camera Feed Management
- `POST /add_camera_feed` - Add new camera feed
- `GET /camera_feeds` - List all camera feeds
- `POST /edit_camera_feed/<id>` - Edit camera feed
- `POST /delete_camera_feed/<id>` - Delete camera feed
- `GET /test_camera_feed/<id>` - Test camera connection

### Detection
- `GET /live_detection` - Live detection stream
- `POST /upload_video` - Upload video for analysis
- `GET /detection_logs` - Get detection logs

### Pages
- `GET /add_employee_form` - Add employee form page
- `GET /employees_page` - Employee management page
- `GET /live_detection_page` - Live detection page
- `GET /upload_video_page` - Video upload page
- `GET /detection_logs_page` - Detection logs page
- `GET /camera_feeds_page` - Camera feeds management page
- `GET /cctv_detection_page` - CCTV detection page

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add proper error handling
- Include docstrings for functions
- Test thoroughly before submitting
- Update documentation for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application is for educational and demonstration purposes. Always ensure compliance with local laws and regulations regarding surveillance and data privacy when using face recognition technology. Users are responsible for:

- Obtaining proper consent for surveillance
- Complying with privacy laws (GDPR, CCPA, etc.)
- Following local regulations for CCTV usage
- Protecting personal data and privacy rights

## 📞 Support

For issues and questions:

- **Check the troubleshooting section** above
- **Review the code comments** for implementation details
- **Create an issue** in the repository
- **Check the logs** for detailed error information

### Getting Help

1. **Check the logs**: Look for error messages in the console output
2. **Test camera connections**: Use the test button in the camera feeds page
3. **Verify dependencies**: Ensure all packages are properly installed
4. **Check permissions**: Verify camera and file access permissions

## 🔮 Future Enhancements

Planned features for future releases:

- **Mobile App**: iOS and Android applications
- **Cloud Integration**: AWS/Azure cloud deployment
- **Advanced Analytics**: Detection statistics and reports
- **Multi-language Support**: Internationalization
- **API Documentation**: Swagger/OpenAPI documentation
- **Real-time Alerts**: Email/SMS notifications
- **Face Recognition Models**: Custom model training
- **Video Recording**: Automatic recording of detections

## 📊 System Requirements

### Minimum Requirements
- **CPU**: Dual-core 2.0 GHz
- **RAM**: 4 GB
- **Storage**: 10 GB free space
- **OS**: Windows 10, macOS 10.14+, Ubuntu 18.04+

### Recommended Requirements
- **CPU**: Quad-core 3.0 GHz or higher
- **RAM**: 8 GB or more
- **Storage**: SSD with 50 GB free space
- **GPU**: NVIDIA GPU with CUDA support (optional)
- **Network**: Stable internet connection for IP cameras

---

**Note**: This application requires a webcam for live detection functionality. Make sure your device has a working camera and that you grant camera permissions when prompted by your browser. In WSL environments, use video upload or external camera feeds for best results. 