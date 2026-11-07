FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY aws_collector.py .
COPY change_detector.py .
COPY cloudtrail_collector.py .
COPY database.py .
COPY event_analyzer.py .
COPY incident_correlator.py .
COPY incident_report.py .
COPY recovery_planner.py .
COPY terraform_reader.py .
COPY database_schema.sql .
COPY terraform ./terraform

CMD ["python", "aws_collector.py"]
