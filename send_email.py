import json
import os
import smtplib
import sys
from email.message import EmailMessage


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


status = sys.argv[1] if len(sys.argv) > 1 else "SUCCESS"
old = load("reports/old_metrics.json")
new = load("reports/new_metrics.json")
student = "FA23-BDS-053"
build = os.environ.get("BUILD_NUMBER", "?")
user = os.environ["SMTP_USER"]
password = os.environ["SMTP_PASS"]

msg = EmailMessage()
msg["From"] = user
msg["To"] = "qasimalik@gmail.com"
msg["Subject"] = f"[{student}] ML retraining pipeline {status} - build #{build}"
msg.set_content("\n".join([
    f"New data received. Pipeline {status}.",
    f"Accuracy before: {old.get('accuracy', 'n/a')} | after: {new.get('accuracy', 'n/a')}",
    f"Rows before: {old.get('training_rows', 'n/a')} | after: {new.get('training_rows', 'n/a')}",
    f"Model version: {new.get('model_version', 'n/a')}",
    f"Git SHA: {new.get('git_sha', 'n/a')}",
    "Metrics: http://51.21.114.124:8000/metrics",
    f"Build: {os.environ.get('BUILD_URL', '')}",
]))

with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
    server.login(user, password)
    server.send_message(msg)
