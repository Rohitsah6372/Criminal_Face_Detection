from flask import Flask, request, redirect, url_for, flash, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import face_recognition
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import cv2
import time
from datetime import datetime, timedelta
import threading
import queue

app = Flask(__name__)

# Configurations
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['DETECTION_COOLDOWN_SECONDS'] = 30  # Time window to prevent duplicate detections

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class Criminal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    criminal_id = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(200), nullable=False)
    face_encoding = db.Column(db.PickleType, nullable=False)  # Store numpy array as binary

    def __repr__(self):
        return f'<Criminal {self.name}>'

class CameraFeed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    camera_url = db.Column(db.String(500), nullable=False)  # RTSP URL, IP camera URL, or device index
    camera_type = db.Column(db.String(50), nullable=False)  # 'rtsp', 'ip', 'device', 'cctv'
    location = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CameraFeed {self.name}>'

class DetectionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    criminal_name = db.Column(db.String(100), nullable=False)
    detection_type = db.Column(db.String(20), nullable=False)  # 'video', 'live', 'cctv'
    camera_feed_id = db.Column(db.Integer, db.ForeignKey('camera_feed.id'), nullable=True)
    camera_feed_name = db.Column(db.String(100), nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<DetectionLog {self.criminal_name} at {self.timestamp}>'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect('/live_detection_page')

@app.route('/add_criminal', methods=['POST'])
def add_criminal():
    name = request.form.get('name')
    criminal_id = request.form.get('criminal_id')
    description = request.form.get('description')
    file = request.files.get('image')

    if not name or not criminal_id or file is None or not hasattr(file, 'filename') or not file.filename or not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'Missing or invalid data'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Load image and encode face
    image = face_recognition.load_image_file(filepath)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        os.remove(filepath)
        return jsonify({'status': 'error', 'message': 'No face detected in image'}), 400
    face_encoding = encodings[0]

    # Store in DB
    try:
        criminal = Criminal(
            name=name,
            criminal_id=criminal_id,
            description=description,
            image_filename=filename,
            face_encoding=face_encoding
        )
        db.session.add(criminal)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Criminal added successfully'})
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/criminals', methods=['GET'])
def list_criminals():
    criminals = Criminal.query.all()
    result = []
    for c in criminals:
        result.append({
            'id': c.id,
            'name': c.name,
            'criminal_id': c.criminal_id,
            'description': c.description,
            'image_url': url_for('static', filename=f'uploads/{c.image_filename}', _external=True)
        })
    return jsonify(result)

@app.route('/edit_criminal/<int:criminal_id>', methods=['POST'])
def edit_criminal(criminal_id):
    criminal = Criminal.query.get_or_404(criminal_id)
    name = request.form.get('name')
    new_criminal_id = request.form.get('criminal_id')
    description = request.form.get('description')
    file = request.files.get('image')

    if name:
        criminal.name = name
    if new_criminal_id:
        criminal.criminal_id = new_criminal_id
    if description is not None:
        criminal.description = description

    if file and hasattr(file, 'filename') and file.filename and allowed_file(file.filename):
        # Remove old image
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], criminal.image_filename)
        if os.path.exists(old_path):
            os.remove(old_path)
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Re-encode face
        image = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            os.remove(filepath)
            return jsonify({'status': 'error', 'message': 'No face detected in new image'}), 400
        criminal.face_encoding = encodings[0]
        criminal.image_filename = filename

    try:
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Criminal updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/delete_criminal/<int:criminal_id>', methods=['POST'])
def delete_criminal(criminal_id):
    criminal = Criminal.query.get_or_404(criminal_id)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], criminal.image_filename)
    try:
        db.session.delete(criminal)
        db.session.commit()
        if os.path.exists(image_path):
            os.remove(image_path)
        return jsonify({'status': 'success', 'message': 'Criminal deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/upload_video', methods=['POST'])
def upload_video():
    file = request.files.get('video')
    if file is None or not hasattr(file, 'filename') or not file.filename:
        return jsonify({'status': 'error', 'message': 'No video file provided'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    # Do not process video here, just return filename for live detection
    return jsonify({'status': 'success', 'video_filename': filename})

def gen_frames(video_filename=None, camera_feed_id=None):
    ctx = app.app_context()
    ctx.push()
    camera = None
    try:
        # Load all criminal encodings
        criminals = Criminal.query.all()
        known_encodings = [c.face_encoding for c in criminals]
        known_names = [c.name for c in criminals]

        if camera_feed_id:
            # Get camera feed details
            camera_feed = CameraFeed.query.get(camera_feed_id)
            if not camera_feed or not camera_feed.is_active:
                return
            # Handle different camera types
            if camera_feed.camera_type == 'device':
                try:
                    camera = cv2.VideoCapture(int(camera_feed.camera_url))
                except ValueError:
                    camera = cv2.VideoCapture(0)
            else:
                # For RTSP, IP cameras, or other URLs
                camera = cv2.VideoCapture(camera_feed.camera_url)
        elif video_filename:
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
            camera = cv2.VideoCapture(video_path)
        else:
            # Try to find an available camera
            camera = find_available_camera()

        if camera is None or not camera.isOpened():
            # Generate error frame
            error_frame = generate_error_frame("Camera not available")
            ret, buffer = cv2.imencode('.jpg', error_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            return

        detected_live = set()
        while True:
            success, frame = camera.read()
            if not success or frame is None:
                break
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
                name = "Unknown"
                confidence = 0.0

                for idx, match in enumerate(matches):
                    if match:
                        name = known_names[idx]
                        # Calculate confidence score
                        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                        confidence = 1 - face_distances[idx]

                        # Check if this person was already detected recently (within configurable time window)
                        cooldown_seconds = app.config.get('DETECTION_COOLDOWN_SECONDS', 30)
                        recent_detection = DetectionLog.query.filter(
                            DetectionLog.criminal_name == name,
                            DetectionLog.timestamp >= datetime.utcnow() - timedelta(seconds=cooldown_seconds)
                        ).first()

                        if not recent_detection:
                            log = DetectionLog(
                                criminal_name=name, 
                                detection_type='cctv' if camera_feed_id else 'live',
                                camera_feed_id=camera_feed_id,
                                camera_feed_name=camera_feed.name if camera_feed_id else None,
                                confidence_score=confidence
                            )
                            db.session.add(log)
                            db.session.commit()
                            detected_live.add(name)
                        break

                # Draw bounding box and label
                color = (0, 0, 255) if name != "Unknown" else (0, 255, 0)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                label = f"{name} ({confidence:.2f})" if name != "Unknown" else name
                cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    except Exception as e:
        print(f"Error in gen_frames: {e}")
        # Generate error frame
        error_frame = generate_error_frame(f"Error: {str(e)}")
        ret, buffer = cv2.imencode('.jpg', error_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        if camera is not None:
            camera.release()
        ctx.pop()

def find_available_camera():
    """Find an available camera by trying different device indices"""
    for i in range(4):  # Try cameras 0-3
        try:
            camera = cv2.VideoCapture(i)
            if camera.isOpened():
                # Test if we can actually read a frame
                ret, frame = camera.read()
                if ret and frame is not None:
                    return camera
                else:
                    camera.release()
            else:
                camera.release()
        except Exception as e:
            print(f"Error trying camera {i}: {e}")
            continue
    return None

def generate_error_frame(message):
    """Generate an error frame with a message"""
    # Create a black frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add error text
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2
    color = (255, 255, 255)
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(message, font, font_scale, thickness)
    
    # Calculate position to center the text
    x = (frame.shape[1] - text_width) // 2
    y = (frame.shape[0] + text_height) // 2
    
    # Add text
    cv2.putText(frame, message, (x, y), font, font_scale, color, thickness)
    
    # Add additional help text
    help_text = "Check camera connection or try video upload"
    (help_width, help_height), _ = cv2.getTextSize(help_text, font, 0.7, 1)
    help_x = (frame.shape[1] - help_width) // 2
    help_y = y + 50
    cv2.putText(frame, help_text, (help_x, help_y), font, 0.7, (200, 200, 200), 1)
    
    return frame

@app.route('/live_detection')
def live_detection():
    video_filename = request.args.get('video')
    camera_feed_id = request.args.get('camera_feed_id')
    if camera_feed_id:
        camera_feed_id = int(camera_feed_id)
    return app.response_class(gen_frames(video_filename, camera_feed_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/add_criminal_form', methods=['GET'])
def add_criminal_form():
    return render_template('add_criminal.html')

@app.route('/criminals_page', methods=['GET'])
def criminals_page():
    return render_template('criminals.html')

@app.route('/live_detection_page', methods=['GET'])
def live_detection_page():
    return render_template('live_detection.html')

@app.route('/upload_video_page', methods=['GET'])
def upload_video_page():
    return render_template('upload_video.html')

@app.route('/detection_logs', methods=['GET'])
def detection_logs():
    logs = DetectionLog.query.order_by(DetectionLog.timestamp.desc()).all()
    return jsonify([
        {
            'id': log.id,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'criminal_name': log.criminal_name,
            'detection_type': log.detection_type
        } for log in logs
    ])

@app.route('/delete_detection_log/<int:log_id>', methods=['DELETE'])
def delete_detection_log(log_id):
    try:
        log = DetectionLog.query.get_or_404(log_id)
        db.session.delete(log)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Detection log deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/delete_all_detection_logs', methods=['DELETE'])
def delete_all_detection_logs():
    try:
        DetectionLog.query.delete()
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'All detection logs deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/detection_logs_page', methods=['GET'])
def detection_logs_page():
    return render_template('detection_logs.html')

# Camera Feed Management Routes
@app.route('/add_camera_feed', methods=['POST'])
def add_camera_feed():
    name = request.form.get('name')
    camera_url = request.form.get('camera_url')
    camera_type = request.form.get('camera_type')
    location = request.form.get('location')
    description = request.form.get('description')
    
    if not name or not camera_url or not camera_type:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    try:
        camera_feed = CameraFeed(
            name=name,
            camera_url=camera_url,
            camera_type=camera_type,
            location=location,
            description=description
        )
        db.session.add(camera_feed)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Camera feed added successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/camera_feeds', methods=['GET'])
def list_camera_feeds():
    camera_feeds = CameraFeed.query.all()
    result = []
    for cf in camera_feeds:
        result.append({
            'id': cf.id,
            'name': cf.name,
            'camera_url': cf.camera_url,
            'camera_type': cf.camera_type,
            'location': cf.location,
            'description': cf.description,
            'is_active': cf.is_active,
            'created_at': cf.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result)

@app.route('/edit_camera_feed/<int:camera_feed_id>', methods=['POST'])
def edit_camera_feed(camera_feed_id):
    camera_feed = CameraFeed.query.get_or_404(camera_feed_id)
    name = request.form.get('name')
    camera_url = request.form.get('camera_url')
    camera_type = request.form.get('camera_type')
    location = request.form.get('location')
    description = request.form.get('description')
    is_active = request.form.get('is_active')
    
    if name:
        camera_feed.name = name
    if camera_url:
        camera_feed.camera_url = camera_url
    if camera_type:
        camera_feed.camera_type = camera_type
    if location is not None:
        camera_feed.location = location
    if description is not None:
        camera_feed.description = description
    if is_active is not None:
        camera_feed.is_active = is_active.lower() == 'true'
    
    try:
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Camera feed updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/delete_camera_feed/<int:camera_feed_id>', methods=['POST'])
def delete_camera_feed(camera_feed_id):
    camera_feed = CameraFeed.query.get_or_404(camera_feed_id)
    try:
        db.session.delete(camera_feed)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Camera feed deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/test_camera_feed/<int:camera_feed_id>', methods=['GET'])
def test_camera_feed(camera_feed_id):
    camera_feed = CameraFeed.query.get_or_404(camera_feed_id)
    camera = None
    try:
        if camera_feed.camera_type == 'device':
            try:
                camera = cv2.VideoCapture(int(camera_feed.camera_url))
            except ValueError:
                # Try to find an available camera
                camera = find_available_camera()
                if camera is None:
                    return jsonify({'status': 'error', 'message': 'No camera devices available'}), 400
        else:
            camera = cv2.VideoCapture(camera_feed.camera_url)
        
        if camera is None or not camera.isOpened():
            return jsonify({'status': 'error', 'message': 'Cannot connect to camera feed'}), 400
        
        ret, frame = camera.read()
        if ret and frame is not None:
            return jsonify({'status': 'success', 'message': 'Camera feed is working'})
        else:
            return jsonify({'status': 'error', 'message': 'Camera feed is not working - no video signal'}), 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error testing camera: {str(e)}'}), 500
    finally:
        if camera is not None:
            camera.release()

@app.route('/add_camera_feed_form', methods=['GET'])
def add_camera_feed_form():
    return render_template('add_camera_feed.html')

@app.route('/camera_feeds_page', methods=['GET'])
def camera_feeds_page():
    return render_template('camera_feeds.html')

@app.route('/cctv_detection_page', methods=['GET'])
def cctv_detection_page():
    return render_template('cctv_detection.html')

@app.route('/detection_config', methods=['GET'])
def get_detection_config():
    return jsonify({
        'cooldown_seconds': app.config.get('DETECTION_COOLDOWN_SECONDS', 30)
    })

@app.route('/criminal_status_page', methods=['GET'])
def criminal_status_page():
    return render_template('criminal_status.html')

@app.route('/criminal_status_data', methods=['GET'])
def get_criminal_status_data():
    """Get real-time criminal status data"""
    try:
        # Get all criminals
        criminals = Criminal.query.all()
        criminal_data = []
        
        # Get recent detection logs
        cooldown_seconds = app.config.get('DETECTION_COOLDOWN_SECONDS', 30)
        recent_time = datetime.utcnow() - timedelta(seconds=cooldown_seconds)
        
        recent_detections = DetectionLog.query.filter(
            DetectionLog.timestamp >= recent_time
        ).all()
        
        # Create a map of recent detections
        recent_detection_map = {}
        for detection in recent_detections:
            if detection.criminal_name not in recent_detection_map:
                recent_detection_map[detection.criminal_name] = []
            recent_detection_map[detection.criminal_name].append({
                'timestamp': detection.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'detection_type': detection.detection_type,
                'camera_feed_name': detection.camera_feed_name
            })
        
        # Build status data for each criminal
        for criminal in criminals:
            recent_detections_for_criminal = recent_detection_map.get(criminal.name, [])
            is_present = len(recent_detections_for_criminal) > 0
            
            criminal_data.append({
                'id': criminal.id,
                'name': criminal.name,
                'criminal_id': criminal.criminal_id,
                'image_url': url_for('static', filename=f'uploads/{criminal.image_filename}', _external=True),
                'status': 'present' if is_present else 'absent',
                'detection_count': len(recent_detections_for_criminal),
                'last_detected': recent_detections_for_criminal[-1]['timestamp'] if recent_detections_for_criminal else None,
                'recent_detections': recent_detections_for_criminal
            })
        
        return jsonify({
            'criminals': criminal_data,
            'summary': {
                'total': len(criminals),
                'present': len([c for c in criminal_data if c['status'] == 'present']),
                'absent': len([c for c in criminal_data if c['status'] == 'absent']),
                'detection_rate': round((len([c for c in criminal_data if c['status'] == 'present']) / len(criminals)) * 100) if criminals else 0,
                'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 