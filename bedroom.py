# app.py
from flask import Flask, Response, send_from_directory
import cv2
import schedule
import time
from datetime import datetime
import os
from threading import Thread

app = Flask(__name__)
RECORDING_DIR = "recordings"
os.makedirs(RECORDING_DIR, exist_ok=True)

def record_video(duration_seconds=240):  # 4 minutes
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Set up video writer
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{RECORDING_DIR}/recording_{timestamp}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(filename, fourcc, 20.0, (640,480))
    
    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
    
    cap.release()
    out.release()
    print(f"Recording saved: {filename}")

def schedule_recordings():
    schedule.every().day.at("13:49").do(record_video)
    schedule.every().day.at("08:59").do(record_video)
    schedule.every().day.at("15:59").do(record_video)
    schedule.every().day.at("22:59").do(record_video)
    
    while True:
        schedule.run_pending()
        time.sleep(30)

# Start scheduler in background thread
scheduler_thread = Thread(target=schedule_recordings, daemon=True)
scheduler_thread.start()

@app.route('/recordings/<path:filename>')
def serve_recording(filename):
    return send_from_directory(RECORDING_DIR, filename, mimetype='video/mp4')

@app.route('/recordings')
def list_recordings():
    files = os.listdir(RECORDING_DIR)
    files = [f for f in files if f.endswith('.mp4')]
    files.sort(reverse=True)
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Camera Recordings</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }
            
            body {
                background-color: #f5f5f5;
                color: #333;
                line-height: 1.6;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }
            
            h1 {
                color: #2c3e50;
                margin-bottom: 30px;
                text-align: center;
                font-size: 2.5em;
            }
            
            .recordings-list {
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .recording-link {
                display: block;
                padding: 15px 20px;
                color: #2c3e50;
                text-decoration: none;
                border-bottom: 1px solid #eee;
                transition: background-color 0.3s ease;
            }
            
            .recording-link:last-child {
                border-bottom: none;
            }
            
            .recording-link:hover {
                background-color: #f8f9fa;
            }
            
            .back-button {
                display: inline-block;
                background-color: #3cb371;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                text-decoration: none;
                margin-bottom: 20px;
                transition: background-color 0.3s ease;
            }
            
            .back-button:hover {
                background-color: #2980b9;
            }
            
            @media (max-width: 600px) {
                body {
                    padding: 15px;
                }
                
                h1 {
                    font-size: 2em;
                }
                
                .recording-link {
                    padding: 12px 15px;
                }
            }
        </style>
    </head>
    <body>
        <a href="/" class="back-button">← Back</a>
        <h1>Recordings</h1>
        <div class="recordings-list">
    '''
    
    for f in files:
        # Format the timestamp from filename (recording_YYYYMMDD_HHMMSS.mp4)
        try:
            timestamp = f.split('_')[1] + '_' + f.split('_')[2].split('.')[0]
            formatted_time = datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%B %d, %Y at %I:%M %p')
        except:
            formatted_time = f
            
        html += f'<a href="/recordings/{f}" class="recording-link">Recording from {formatted_time}</a>\\n'
    
    html += '''
        </div>
    </body>
    </html>
    '''
    
    return html

def gen_frames():
    cap = cv2.VideoCapture(1)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/live')
def live_stream():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Live Stream</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }
            
            body {
                background-color: #f5f5f5;
                color: #333;
                line-height: 1.6;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }
            
            h1 {
                color: #2c3e50;
                margin-bottom: 30px;
                text-align: center;
                font-size: 2.5em;
            }
            
            .stream-container {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            
            .stream-container img {
                width: 100%;
                height: auto;
                border-radius: 4px;
            }
            
            .back-button {
                display: inline-block;
                background-color: #3cb371;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                text-decoration: none;
                margin-bottom: 20px;
                transition: background-color 0.3s ease;
            }
            
            .back-button:hover {
                background-color: #2980b9;
            }
            
            @media (max-width: 600px) {
                body {
                    padding: 15px;
                }
                
                h1 {
                    font-size: 2em;
                }
                
                .stream-container {
                    padding: 15px;
                }
            }
        </style>
    </head>
    <body>
        <a href="/" class="back-button">← Back</a>
        <h1>Live Stream</h1>
        <div class="stream-container">
            <img src="/video_feed" alt="Live Stream">
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cat Cam
        </title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }
            
            body {
                background-color: #f5f5f5;
                color: #333;
                line-height: 1.6;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }
            
            h1 {
                color: #2c3e50;
                margin-bottom: 30px;
                text-align: center;
                font-size: 2.5em;
            }
            
            .button-container {
                display: grid;
                gap: 15px;
                margin-top: 20px;
            }
            
            .button {
                background-color: #3cb371;
                color: white;
                padding: 15px 25px;
                border-radius: 8px;
                text-decoration: none;
                text-align: center;
                transition: background-color 0.3s ease;
                font-size: 1.1em;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .button:hover {
                background-color: #2980b9;
            }
            
            @media (max-width: 600px) {
                body {
                    padding: 15px;
                }
                
                h1 {
                    font-size: 2em;
                }
                
                .button {
                    padding: 12px 20px;
                }
            }
        </style>
    </head>
    <body>
        <h1>Cat Cam Bedroom</h1>
        <div class="button-container">
            <a href="/recordings" class="button">View Recordings</a>
            <a href="/live" class="button">View Live Stream</a>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
