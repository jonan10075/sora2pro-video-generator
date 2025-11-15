import os
import time
import base64
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Create Flask app and enable CORS
app = Flask(__name__, static_folder='../frontend')
CORS(app)

# APIMart API endpoints and credentials
API_URL = "https://api.apimart.ai/v1/videos/generations"
TASK_URL = "https://api.apimart.ai/v1/tasks"
API_KEY = os.getenv('APIMART_API_KEY')

if not API_KEY:
    raise RuntimeError("APIMART_API_KEY environment variable is required")


def poll_task_status(task_id):
    """
    Polls the APIMart task status endpoint until the video generation
    is complete. Returns the first video URL when available.
    """
    headers = {"Authorization": f"Bearer {API_KEY}"}
    status_url = f"{TASK_URL}/{task_id}"
    while True:
        resp = requests.get(status_url, headers=headers)
        resp.raise_for_status()
        body = resp.json()
        # APIMart wraps result data under a `data` key
        data = body.get('data', {}) if isinstance(body, dict) else {}
        status = data.get('status')
        if status == 'completed':
            result = data.get('result', {})
            videos = result.get('videos', [])
            if videos:
                url_list = videos[0].get('url')
                if isinstance(url_list, list) and url_list:
                    return url_list[0]
            raise RuntimeError('Completed but no video URL found')
        if status in ('failed', 'canceled'):
            raise RuntimeError(f"Video generation {status}")
        time.sleep(3)


@app.route('/')
def serve_index():
    """Serve the front-end HTML file."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """Handles video generation requests from the front-end."""
    prompt = request.form.get('prompt', '').strip()
    duration = request.form.get('duration')
    if duration not in ('15', '25'):
        return jsonify(error='Duration must be 15 or 25 seconds'), 400

    image_file = request.files.get('image')
    if image_file is None:
        return jsonify(error='Image is required'), 400

    # Convert uploaded image to a base64 data URI
    try:
        file_bytes = image_file.read()
        encoded = base64.b64encode(file_bytes).decode('utf-8')
        mime_type = image_file.mimetype or 'image/png'
        data_uri = f"data:{mime_type};base64,{encoded}"
    except Exception:
        return jsonify(error='Failed to read image file'), 400

    # Build the payload for APIMart
    payload = {
        'model': 'sora-2-pro',
        'prompt': prompt,
        'duration': int(duration),
        'aspect_ratio': '16:9',
        'image_urls': [data_uri],
        'watermark': False,
        'private': False
    }

    headers = {
        'Authorization': f"Bearer {API_KEY}",
        'Content-Type': 'application/json'
    }

    try:
        api_resp = requests.post(API_URL, headers=headers, json=payload)
        api_resp.raise_for_status()
        resp_json = api_resp.json()
    except Exception as e:
        return jsonify(error=str(e)), 500

    data = resp_json.get('data') if isinstance(resp_json, dict) else None
    task_id = None
    if isinstance(data, dict):
        task_id = data.get('task_id') or data.get('id')
    elif isinstance(data, list) and data:
        task_id = data[0].get('task_id') or data[0].get('id')

    if not task_id:
        return jsonify(error='Failed to obtain task ID'), 500

    try:
        video_url = poll_task_status(task_id)
    except Exception as e:
        return jsonify(error=str(e)), 500

    return jsonify(video_url=video_url)


if __name__ == '__main__':
    app.run(debug=True)
