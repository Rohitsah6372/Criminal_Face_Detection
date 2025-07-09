@echo off
echo 🚀 Starting Criminal Face Recognition System...
echo.

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  Virtual environment not detected
    echo 💡 Please activate your virtual environment first:
    echo    venv\Scripts\activate
    echo.
    set /p continue="Continue anyway? (y/N): "
    if /i not "%continue%"=="y" exit /b 1
)

REM Check if dependencies are installed
echo 📦 Checking dependencies...
python -c "import flask, cv2, face_recognition" 2>nul
if errorlevel 1 (
    echo ❌ Missing dependencies detected
    echo 💡 Please install dependencies:
    echo    pip install -r requirements.txt
    echo.
    set /p continue="Continue anyway? (y/N): "
    if /i not "%continue%"=="y" exit /b 1
)

REM Create upload directory if it doesn't exist
if not exist "static\uploads" mkdir "static\uploads"

echo 🌐 Starting Flask application...
echo 📱 Access the application at: http://127.0.0.1:5000
echo 🛑 Press Ctrl+C to stop the server
echo.

REM Start the application
python app.py 