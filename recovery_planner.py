import json
import glob
import os
from datetime import datetime
from database import get_connection
from psycopg2.extras import Json

report_files = sorted(glob.glob("reports/incident_report_*.json"))

if not report_files:
    print("No incident reports found. Run incident_report.py first.")
    exit()

latest_report = report_files[-1]

with open(latest_report) as file:
    incidents = json.load(file)

recovery_plan = []

def get_recovery_action(incident):
    action = incident.get("Action", "Unknown")
    risk = incident.get("RiskLevel", "OTHER")

    if action == "TerminateInstances":
        return [
            "Check whether the instance termination was authorized.",
            "Identify the affected instance and its dependencies.",
            "Check available backups, AMIs, and recovery options.",
            "Restore the workload using an approved recovery procedure."
        ]

    elif action == "StopInstances":
        return [
            "Verify whether stopping the instance was intentional.",
            "Check application availability and dependent services.",
            "Confirm whether the instance should be restarted.",
            "If approved, start the instance and verify application health."
        ]

    elif action in [
        "AuthorizeSecurityGroupIngress",
        "AuthorizeSecurityGroupEgress",
        "ModifySecurityGroupRules"
    ]:
        return [
            "Inspect the security group rule changes.",
            "Verify whether the new network access is authorized.",
            "Check for unintended public or excessive access.",
            "If unauthorized, prepare a controlled rule rollback."
        ]

    elif action in [
        "DeleteSecurityGroup",
        "DeleteVpc",
        "DeleteSubnet",
        "DeleteNetworkAcl",
        "DeleteRouteTable"
    ]:
        return [
            "Identify the deleted networking resource and dependencies.",
            "Check service connectivity and application impact.",
            "Review available infrastructure backups and Terraform state.",
            "Prepare an infrastructure restoration plan."
        ]

    elif action == "ModifyInstanceAttribute":
        return [
            "Review the changed EC2 instance attributes.",
            "Compare the current configuration with the previous snapshot.",
            "Determine whether the modification affected service availability.",
            "Prepare a rollback using the approved configuration."
        ]

    elif action == "SendSSHPublicKey":
        return [
            "Verify whether the EC2 Instance Connect access was authorized.",
            "Review the identity and source details in the full CloudTrail event.",
            "Check for unexpected administrative activity.",
            "No infrastructure rollback is required if the access was legitimate."
        ]

    elif risk == "HIGH":
        return [
            "Investigate the high-risk infrastructure event immediately.",
            "Identify affected resources and service dependencies.",
            "Review CloudTrail details and infrastructure snapshots.",
            "Prepare an approved recovery or rollback procedure."
        ]

    elif risk == "MEDIUM":
        return [
            "Review the infrastructure configuration change.",
            "Determine whether any service was affected.",
            "Compare the configuration with the previous known state.",
            "Prepare a rollback if the change was unauthorized."
        ]

    else:
        return [
            "Review the event and verify whether it was authorized.",
            "Check the affected infrastructure resource.",
            "Monitor for unexpected changes or service impact."
        ]


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
