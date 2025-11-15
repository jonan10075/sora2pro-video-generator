import os
import time
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='../frontend')
CORS(app)

API_URL = "https://api.cometapi.com/v1/videos"
API_KEY = os.getenv('COMET_API_KEY')

if not API_KEY:
    raise RuntimeError("COMET_API_KEY environment variable is required")

def poll_video_status(video_id):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    status_url = f"{API_URL}/{video_id}"
    while True:
        resp = requests.get(status_url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        status = data.get('status')
        if status == 'completed':
            return data.get('video_url')
        if status in ('failed', 'canceled'):
            raise RuntimeError(f"Video generation {status}")
        time.sleep(3)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form.get('prompt', '')
    duration = request.form.get('duration')
    if duration not in ('15', '25'):
        return jsonify(error='Duration must be 15 or 25 seconds'), 400

    file = request.files.get('image')
    if file is None:
        return jsonify(error='Image is required'), 400

    files = {
        'input_reference': (file.filename, file.stream, file.mimetype)
    }
    data = {
        'prompt': prompt,
        'seconds': int(duration),
        'model': 'sora-2-pro',
        'size': '1792x1024'
    }
    headers = {
        'Authorization': f"Bearer {API_KEY}"
    }

    try:
        response = requests.post(API_URL, headers=headers, data=data, files=files)
        response.raise_for_status()
        json_data = response.json()
    except Exception as e:
        return jsonify(error=str(e)), 500

    video_id = json_data.get('id') or json_data.get('video_id') or json_data.get('task_id')
    if not video_id:
        return jsonify(error='Failed to get video id'), 500

    try:
        video_url = poll_video_status(video_id)
    except Exception as e:
        return jsonify(error=str(e)), 500

    return jsonify(video_url=video_url)

if __name__ == '__main__':
    app.run(debug=True)
