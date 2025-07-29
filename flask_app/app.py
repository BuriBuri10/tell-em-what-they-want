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
    if request.method == "POST":
        user_id = request.form.get("user_id")
        query = request.form.get("query")
        campaign_workflow = CampaignWorkflow()

        state = asyncio.run(campaign_workflow.run(user_id=user_id, query=query))
        # result = asyncio.run(workflow.run(query=query, user_id=user_id))

        # Save the report
        CampaignReportSaver.save(state, user_id=user_id, query=query)

        # Create the same report string (repeating CampaignReportSaver logic)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

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

    return render_template("index.html", output=output)


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
    

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    feedback = request.form.get("feedback")
    revision = request.form.get("revision") == "true"

    # Call the router’s method (ensure you're referencing the correct instance)
    campaign_workflow.human_review_router.receive_feedback(feedback, revision)
    return "Feedback submitted", 200


if __name__ == "__main__":
    app.run(debug=True)





# from flask import Flask, render_template, request
# import requests
# import threading
# import time
# import os

# app = Flask(__name__)

# # Shared log buffer
# log_buffer = []

# # API endpoint (adjust if running on a different host/port)
# API_URL = "http://localhost:8000/run-campaign"


# @app.route("/", methods=["GET", "POST"])
# def index():
#     output = None

#     if request.method == "POST":
#         user_id = request.form["user_id"]
#         query = request.form["query"]

#         # Clear old logs
#         log_buffer.clear()

#         def stream_logs():
#             log_file_path = os.path.abspath("logs/app.log")
#             if os.path.exists(log_file_path):
#                 with open(log_file_path, "r") as f:
#                     f.seek(0, 2)  # Go to end
#                     while True:
#                         line = f.readline()
#                         if line:
#                             log_buffer.append(line)
#                         time.sleep(0.2)

#         threading.Thread(target=stream_logs, daemon=True).start()

#         try:
#             response = requests.post(API_URL, json={"user_id": user_id, "query": query})
#             if response.status_code == 200:
#                 output = response.json()
#             else:
#                 output = {"error": response.text}
#         except Exception as e:
#             output = {"error": str(e)}

#     return render_template("index.html", logs=log_buffer, output=output)


# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
