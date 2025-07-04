from flask import Flask, request, redirect, url_for, flash, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import face_recognition
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import cv2
import time
from datetime import datetime

app = Flask(__name__)

# Configurations
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

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

class DetectionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    criminal_name = db.Column(db.String(100), nullable=False)
    detection_type = db.Column(db.String(20), nullable=False)  # 'video' or 'live'

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

    # Load all criminal encodings
    criminals = Criminal.query.all()
    known_encodings = [c.face_encoding for c in criminals]
    known_names = [c.name for c in criminals]
    detected = set()

    # Process video
    video = cv2.VideoCapture(filepath)
    while True:
        ret, frame = video.read()
        if not ret:
            break
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            name = None
            for idx, match in enumerate(matches):
                if match:
                    name = known_names[idx]
                    detected.add(name)
                    break
    video.release()
    # Log detections
    for name in detected:
        log = DetectionLog(criminal_name=name, detection_type='video')
        db.session.add(log)
    db.session.commit()
    return jsonify({'status': 'success', 'detected_criminals': list(detected)})

def gen_frames():
    with app.app_context():
        # Load all criminal encodings
        criminals = Criminal.query.all()
        known_encodings = [c.face_encoding for c in criminals]
        known_names = [c.name for c in criminals]
    camera = cv2.VideoCapture(0)
    detected_live = set()
    while True:
        success, frame = camera.read()
        if not success:
            break
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"
            for idx, match in enumerate(matches):
                if match:
                    name = known_names[idx]
                    if name not in detected_live:
                        detected_live.add(name)
                        with app.app_context():
                            log = DetectionLog(criminal_name=name, detection_type='live')
                            db.session.add(log)
                            db.session.commit()
                    break
            # Draw bounding box and label
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    camera.release()

@app.route('/live_detection')
def live_detection():
    return app.response_class(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

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
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'criminal_name': log.criminal_name,
            'detection_type': log.detection_type
        } for log in logs
    ])

@app.route('/detection_logs_page', methods=['GET'])
def detection_logs_page():
    return render_template('detection_logs.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 