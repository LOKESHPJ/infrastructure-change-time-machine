import json
import glob
import os
from datetime import datetime
from database import get_connection
from psycopg2.extras import Json
from recovery_logic import get_recovery_action

report_files = sorted(glob.glob("reports/incident_report_*.json"))

if not report_files:
    print("No incident reports found. Run incident_report.py first.")
    exit()

latest_report = report_files[-1]

with open(latest_report) as file:
    incidents = json.load(file)

recovery_plan = []



for incident in incidents:
    recovery_plan.append({
        "RiskLevel": incident.get("RiskLevel"),
        "Action": incident.get("Action"),
        "EventTime": incident.get("EventTime"),
        "Username": incident.get("Username"),
        "MatchedInstances": [
            instance.get("InstanceId")
            for instance in incident.get("MatchedInstances", [])
        ],
        "RecommendedRecoveryActions": get_recovery_action(incident),
        "AutomaticExecution": False
    })


os.makedirs("recovery_plans", exist_ok=True)

filename = datetime.now().strftime("recovery_plan_%Y%m%d_%H%M%S.json")
filepath = os.path.join("recovery_plans", filename)

with open(filepath, "w") as file:
    json.dump(recovery_plan, file, indent=4)

print("\nINFRASTRUCTURE RECOVERY PLAN")
print("============================")
print("Incident report:", latest_report)
print("Incidents analyzed:", len(incidents))

for plan in recovery_plan:
    print("\nRisk:", plan["RiskLevel"])
    print("Action:", plan["Action"])
    print("Affected instances:", plan["MatchedInstances"])
    print("Recommended actions:")

    for index, action in enumerate(
        plan["RecommendedRecoveryActions"], start=1
    ):
        print(str(index) + ".", action)

    print("Automatic execution:", plan["AutomaticExecution"])

print("\nRecovery plan saved:", filepath)

# Save recovery plan to PostgreSQL
try:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM incident_reports
        ORDER BY generated_at DESC, id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    incident_report_id = result[0] if result else None

    cursor.execute("""
        INSERT INTO recovery_plans
        (incident_report_id, plan_data, automatic_execution)
        VALUES (%s, %s, %s)
    """, (incident_report_id, Json(recovery_plan), False))

    connection.commit()

    print("Recovery plan successfully saved to PostgreSQL!")
    print("Linked incident report ID:", incident_report_id)

except Exception as error:
    print("Database save failed:", error)

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()
