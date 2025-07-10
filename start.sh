#!/bin/bash

# Employee Attendance System Startup Script
# This script handles common issues in WSL environments

echo "🚀 Starting Employee Attendance System..."

# Check if we're in WSL
if grep -qi microsoft /proc/version; then
    echo "📋 WSL detected - checking camera access..."
    
    # Check if camera devices exist
    if [ ! -e /dev/video0 ]; then
        echo "⚠️  Warning: No camera device found at /dev/video0"
        echo "💡 This is normal in WSL. You can still use:"
        echo "   - Video upload functionality"
        echo "   - External camera feeds (IP cameras, RTSP streams)"
        echo "   - Add camera feeds through the web interface"
        echo ""
    else
        echo "✅ Camera device found at /dev/video0"
    fi
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not detected"
    echo "💡 Please activate your virtual environment first:"
    echo "   source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
python -c "import flask, cv2, face_recognition" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies detected"
    echo "💡 Please install dependencies:"
    echo "   pip install -r requirements.txt"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create upload directory if it doesn't exist
mkdir -p static/uploads

echo "🌐 Starting Flask application..."
echo "📱 Access the application at: http://127.0.0.1:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the application
python app.py 