"""
TASK 4: DOCKERIZED FLASK API
----------------------------
Description: Containerization of a Flask-based inference service. 
Demonstrates environment isolation and portable AI deployment.

Features: RESTful /predict endpoint, Dockerfile configuration, 
and container lifecycle management (build/run).

Stack: Python, Flask, Docker.
"""

import subprocess
import time
import sys

def create_file():
    """Step 1: Create Flask app file, requirements.txt and Dockerfile programmatically."""
    print("===== Creating Application Files =====")

    app_code = r'''from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is alive! Use POST /predict with JSON {\"feature\": [1,2,3]}"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    input_feature = data.get('feature', [])
    
    prediction = sum(input_feature) * 2
    
    return jsonify({
        'status': 'success',
        'input': input_feature,
        'prediction': prediction
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
'''

    docker_code = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
"""

    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write("flask\n")

    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_code)

    with open("Dockerfile", "w", encoding="utf-8") as f:
        f.write(docker_code)

    print("Created files successfully:")
    print("  • requirements.txt")
    print("  • app.py")
    print("  • Dockerfile")


def build_image():
    """Step 2: Build the Docker image."""
    print("\n===== Building Docker Image =====")
    subprocess.run(
        ["docker", "build", "-t", "simple_flask_predict", "."],
        check=True
    )
    print("Image built successfully: simple_flask_predict")


def run_container():
    """Step 3: Run the Docker container."""
    print("\n===== Starting Container =====")
    
    # Remove old container if exists (ignore failure)
    subprocess.run(["docker", "rm", "-f", "flask-container"],
                   capture_output=True, text=True)

    result = subprocess.run(
        ["docker", "run", "-d", "--name", "flask-container",
         "-p", "5000:5000", "simple_flask_predict"],
        check=True, capture_output=True, text=True
    )
    print("Container started:", result.stdout.strip()[:12], "...")
    print("Waiting 6 seconds for Flask to initialize...")
    time.sleep(6)


def test_api():
    """Step 4: Test the /predict endpoint."""
    print("\n===== Testing API =====")
    
    curl_cmd = [
        "curl", "-s", "--fail-with-body",
        "-X", "POST", "http://localhost:5000/predict",
        "-H", "Content-Type: application/json",
        "-d", '{"feature": [1, 2, 3, 4, 5]}'
    ]

    result = subprocess.run(
        curl_cmd,
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode == 0:
        print("API Response (200 OK):")
        print(result.stdout.strip())
    else:
        print("API test failed!")
        print("Exit code:", result.returncode)
        print("Response / error:")
        print(result.stdout.strip() or result.stderr.strip())


def show_logs():
    """Show last lines of container logs"""
    print("\n===== Last 15 lines of container logs =====")
    subprocess.run(["docker", "logs", "--tail", "15", "flask-container"])


def cleanup():
    """Step 5: Stop and remove the container."""
    print("\n===== Cleaning Up =====")
    subprocess.run(["docker", "stop", "flask-container"], 
                   capture_output=True, check=False)
    subprocess.run(["docker", "rm", "flask-container"], 
                   capture_output=True, check=False)
    print("Container stopped and removed.")