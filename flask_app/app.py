from flask import Flask, render_template, request, jsonify
import os
import threading
import time
import asyncio
from pathlib import Path
from datetime import datetime

import sys

# Add project root to sys.path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from workflows.workflow import CampaignWorkflow  # 👈 direct use
from core.utils.campaign_recs import CampaignReportSaver  # if needed

app = Flask(__name__)
# LOG_DIR = "/app/logs"
from logs.logging_config import find_project_root
LOG_DIR = os.path.join(find_project_root(), "logs")
campaign_workflow = CampaignWorkflow()

# Shared buffer for log lines
log_buffer = []

# Absolute path to log file
log_file_path = os.path.abspath("logs/app.log")

# Ensure logs dir exists
Path("logs").mkdir(exist_ok=True)

# Log tailing thread
def stream_logs():
    if not os.path.exists(log_file_path):
        open(log_file_path, "a").close()
    with open(log_file_path, "r") as f:
        f.seek(0, os.SEEK_END)  # Go to end of file
        while True:
            line = f.readline()
            if line:
                log_buffer.append(line)
                if len(log_buffer) > 100:
                    log_buffer.pop(0)
            time.sleep(0.2)

# Start thread once
threading.Thread(target=stream_logs, daemon=True).start()

@app.route("/", methods=["GET", "POST"])
def index():
    output = None
    docx_link = None  # <--- Initialize the link

    if request.method == "POST":
        user_id = request.form.get("user_id")
        query = request.form.get("query")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        campaign_workflow = CampaignWorkflow()
        state = asyncio.run(campaign_workflow.run(user_id=user_id, query=query))

        # Save the report
        CampaignReportSaver.save(state, user_id=user_id, query=query, timestamp=timestamp)

        # Prepare download link (same logic used in .docx saving)
        # timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        docx_filename = f"{user_id}_{timestamp}.docx"
        docx_link = f"/download/{docx_filename}"

        # Build report preview for UI
        report = f"""📊 CAMPAIGN REPORT
───────────────────────
User ID: {user_id}
Timestamp: {timestamp}
Campaign Query: {query}

User Segment: {state.user_segment or 'N/A'}
Campaign Objective: {state.campaign_objective or 'N/A'}
Recommendation: {state.campaign_recommendation or 'N/A'}
Generated Ad Copy: {state.generated_ad or 'N/A'}
Human Feedback: {state.ad_feedback or 'No feedback yet'}

Recommendation:
{state.campaign_recommendation or 'N/A'}

Generated Ad Copy:
{state.generated_ad or 'N/A'}

Human Feedback:
{state.ad_feedback or 'No feedback yet'}
"""
        output = report

    return render_template("index.html", output=output, docx_link=docx_link)

# @app.route("/", methods=["GET", "POST"])
# def index():
#     output = None
#     if request.method == "POST":
#         user_id = request.form.get("user_id")
#         query = request.form.get("query")
#         campaign_workflow = CampaignWorkflow()

#         state = asyncio.run(campaign_workflow.run(user_id=user_id, query=query))

#         # Save the report
#         CampaignReportSaver.save(state, user_id=user_id, query=query)

#         # Create the same report string (repeating CampaignReportSaver logic)
#         from datetime import datetime
#         timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#         report = f"""📊 CAMPAIGN REPORT
# ───────────────────────
# User ID: {user_id}
# Timestamp: {timestamp}
# Campaign Query: {query}

# User Segment: {state.user_segment or 'N/A'}
# Campaign Objective: {state.campaign_objective or 'N/A'}
# Recommendation: {state.campaign_recommendation or 'N/A'}
# Generated Ad Copy: {state.generated_ad or 'N/A'}
# Human Feedback: {state.ad_feedback or 'No feedback yet'}

# Recommendation:
# {state.campaign_recommendation or 'N/A'}

# Generated Ad Copy:
# {state.generated_ad or 'N/A'}

# Human Feedback:
# {state.ad_feedback or 'No feedback yet'}
# """
#         output = report

#     return render_template("index.html", output=output)


@app.route("/logs")
def get_logs():
    # return jsonify(logs=log_buffer[-50:])  # return last 50 lines
    try:
        today = datetime.now().strftime("%Y%m%d")
        log_file_path = os.path.join(LOG_DIR, f"{today}.txt")
        if not os.path.exists(log_file_path):
            return jsonify({"logs": ["Log file not found."]})
        
        with open(log_file_path, "r") as f:
            lines = f.readlines()
        return jsonify({"logs": lines[-100:]})  # adjust as needed
    except Exception as e:
        return jsonify({"logs": [f"Error: {e}"]})
    

from flask import send_from_directory

@app.route('/download/<filename>')
def download_file(filename):
    output_dir = os.path.abspath("campaign_outputs")
    file_path = os.path.join(output_dir, filename)

    if not os.path.exists(file_path):
        return "File not found", 404

    return send_from_directory(output_dir, filename, as_attachment=True)


# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

