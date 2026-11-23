import json
import glob
import os
from datetime import datetime

from database import get_connection
from psycopg2.extras import Json
from recovery_logic import get_recovery_action


# --------------------------------------------------
# 1. Load latest incident report
# --------------------------------------------------

report_files = sorted(
    glob.glob("reports/incident_report_*.json")
)

if not report_files:
    print("No incident reports found. Run incident_report.py first.")
    exit()

latest_report = report_files[-1]

with open(latest_report) as file:
    incidents = json.load(file)


# --------------------------------------------------
# 2. Generate evidence-based recovery plans
# --------------------------------------------------

recovery_plan = []

for incident in incidents:

    correlation_status = incident.get(
        "CorrelationStatus", "UNMATCHED"
    )

    correlated_changes = incident.get(
        "CorrelatedChanges", []
    )

    cloudtrail_evidence = []

    for change in correlated_changes:
        evidence = change.get("CloudTrailEvidence")

        if evidence:
            cloudtrail_evidence.append(evidence)

    recommended_actions = get_recovery_action(incident)

    if correlation_status == "MATCHED":

        evidence_note = (
            "A matching infrastructure change was confirmed "
            "using snapshot comparison and CloudTrail evidence."
        )

        recommended_actions.insert(
            0,
            "Review the confirmed infrastructure change and verify whether it was authorized."
        )

        for change in correlated_changes:

            recommended_actions.append(
                "Review resource "
                + str(change.get("ResourceID"))
                + " attribute "
                + str(change.get("Attribute"))
                + ": "
                + str(change.get("OldValue"))
                + " -> "
                + str(change.get("NewValue"))
            )

    else:

        evidence_note = (
            "No matching infrastructure snapshot change was found. "
            "Treat this as an observed API event, not a confirmed "
            "infrastructure state change."
        )

        recommended_actions.insert(
            0,
            "Investigate the CloudTrail event and verify whether it was authorized."
        )

        recommended_actions.append(
            "Do not perform a rollback based only on this unmatched event. "
            "Collect additional evidence first."
        )

    recovery_plan.append({

        "EventId": incident.get("EventId"),

        "RiskLevel": incident.get("RiskLevel"),

        "Action": incident.get("Action"),

        "EventTime": incident.get("EventTime"),

        "Username": incident.get("Username"),

        "Service": incident.get("Service"),

        "CorrelationStatus": correlation_status,

        "RecoveryBasis": evidence_note,

        "MatchedInstances": [
            instance.get("InstanceId")
            for instance in incident.get("MatchedInstances", [])
        ],

        "CorrelatedChanges": correlated_changes,

        "CloudTrailEvidence": cloudtrail_evidence,

        "RecommendedRecoveryActions": recommended_actions,

        "AutomaticExecution": False
    })


# --------------------------------------------------
# 3. Save recovery plan as JSON
# --------------------------------------------------

os.makedirs("recovery_plans", exist_ok=True)

filename = datetime.now().strftime(
    "recovery_plan_%Y%m%d_%H%M%S.json"
)

filepath = os.path.join("recovery_plans", filename)

with open(filepath, "w") as file:
    json.dump(recovery_plan, file, indent=4)


# --------------------------------------------------
# 4. Display recovery plan
# --------------------------------------------------

print("\nINFRASTRUCTURE RECOVERY PLAN")
print("============================")

print("Incident report:", latest_report)
print("Incidents analyzed:", len(incidents))

for plan in recovery_plan:

    print("\nRisk:", plan["RiskLevel"])
    print("Action:", plan["Action"])
    print("Event ID:", plan["EventId"])
    print("Correlation:", plan["CorrelationStatus"])

    print("Affected instances:", plan["MatchedInstances"])

    print("Recovery basis:", plan["RecoveryBasis"])

    print("CloudTrail evidence:")

    for evidence in plan["CloudTrailEvidence"]:
        print("  Event ID:", evidence.get("EventId"))
        print("  API action:", evidence.get("APIAction"))
        print("  Actor:", evidence.get("Actor"))

    print("Correlated changes:")

    for change in plan["CorrelatedChanges"]:
        print("  Resource:", change.get("ResourceID"))
        print("  Attribute:", change.get("Attribute"))
        print("  Previous value:", change.get("OldValue"))
        print("  Current value:", change.get("NewValue"))

    print("Recommended actions:")

    for index, action in enumerate(
        plan["RecommendedRecoveryActions"], start=1
    ):
        print(str(index) + ".", action)

    print("Automatic execution:", plan["AutomaticExecution"])


print("\nRecovery plan saved:", filepath)


# --------------------------------------------------
# 5. Save recovery plan to PostgreSQL
# --------------------------------------------------

connection = None
cursor = None

try:

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM incident_reports
        WHERE report_file = %s
        ORDER BY id DESC
        LIMIT 1
    """, (latest_report,))

    result = cursor.fetchone()

    if not result:
        raise ValueError(
            f"No database incident report found for: {latest_report}"
        )

    incident_report_id = result[0]

    cursor.execute("""
        INSERT INTO recovery_plans
        (incident_report_id, plan_data, automatic_execution)
        VALUES (%s, %s, %s)
    """, (
        incident_report_id,
        Json(recovery_plan),
        False
    ))

    connection.commit()

    print("\nRecovery plan successfully saved to PostgreSQL!")
    print("Linked incident report ID:", incident_report_id)

except Exception as error:

    if connection:
        connection.rollback()

    print("Database save failed:", error)

finally:

    if cursor:
        cursor.close()

    if connection:
        connection.close()
