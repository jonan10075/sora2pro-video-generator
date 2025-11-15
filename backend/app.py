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
    attempt = 0
    start_time = time.time()
    timeout_seconds = 300  # 5 minutes maximum wait

    while True:
        attempt += 1
        resp = requests.get(status_url, headers=headers)
        resp.raise_for_status()
        body = resp.json()
        data = body.get('data', {}) if isinstance(body, dict) else {}
        status = data.get('status')

        elapsed = int(time.time() - start_time)
        print(
            f"[poll] task {task_id} attempt={attempt} status={status} elapsed={elapsed}s",
            flush=True,
        )

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
        if elapsed > timeout_seconds:
            raise RuntimeError(
                f"Video generation timed out after {timeout_seconds} seconds"
            )
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

    # Call APIMart
    api_resp = requests.post(API_URL, headers=headers, json=payload)
    # If APIMart returns error (401, 4xx, 5xx...), show full body
    if not api_resp.ok:
        # Log to console (CMD)
        print("APIMart error status:", api_resp.status_code, flush=True)
        print("APIMart error body:", api_resp.text, flush=True)
        # Try to parse JSON; if not, plain text
        try:
            details = api_resp.json()
        except ValueError:
            details = api_resp.text
        return jsonify(
            error="APIMart API error",
            status_code=api_resp.status_code,
            details=details,
        ), api_resp.status_code

    # Parse normal response
    resp_json = api_resp.json()
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
    # Enable threading so the Flask server can handle multiple requests concurrently
    app.run(debug=True, threaded=True)
