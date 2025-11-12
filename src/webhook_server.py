"""
Webhook Server
Auto-generate reports on git push
"""

from flask import Flask, request, jsonify
import subprocess
import threading
import os
from config import Config

app = Flask(__name__)


@app.route('/webhook/analyze', methods=['POST'])
def analyze_on_push():
    """GitHub/GitLab webhook endpoint"""
    data = request.json

    repo_url = data.get('repository', {}).get('url', '')
    repo_name = data.get('repository', {}).get('name', 'unknown')

    print(f" Webhook received for: {repo_name}")

    # Run analysis in background
    thread = threading.Thread(
        target=run_analysis,
        args=(repo_name,)
    )
    thread.start()

    return jsonify({
        'status': 'analysis_started',
        'repository': repo_name
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


def run_analysis(repo_name: str):
    """Run DevFlow Chronicle analysis"""
    try:
        # Assume repos are in /repos directory
        repo_path = f"/repos/{repo_name}"

        if not os.path.exists(repo_path):
            print(f"  Repository not found: {repo_path}")
            return

        print(f" Starting analysis for {repo_name}...")

        result = subprocess.run([
            'python', 'src/main.py',
            repo_path,
            '-f', 'standup', 'technical'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print(f" Analysis complete for {repo_name}")
        else:
            print(f"X Analysis failed: {result.stderr}")

    except Exception as e:
        print(f"X Error running analysis: {e}")


if __name__ == '__main__':
    port = Config.WEBHOOK_PORT
    print(f" Starting webhook server on port {port}...")
    print(f" Endpoint: http://0.0.0.0:{port}/webhook/analyze")

    app.run(host='0.0.0.0', port=port, debug=False)
