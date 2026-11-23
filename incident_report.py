
import json
import glob
import os
from datetime import datetime

from database import get_connection
from psycopg2.extras import Json


# --------------------------------------------------
# 1. Locate the latest infrastructure and CloudTrail data
# --------------------------------------------------

snapshot_files = sorted(glob.glob("snapshots/snapshot_*.json"))
cloudtrail_files = sorted(glob.glob("cloudtrail_logs/*.json"))

if not snapshot_files or not cloudtrail_files:
    print("Missing infrastructure snapshots or CloudTrail logs")
    exit(1)

snapshot_file = snapshot_files[-1]
cloudtrail_file = cloudtrail_files[-1]

with open(snapshot_file) as file:
    instances = json.load(file)

with open(cloudtrail_file) as file:
    events = json.load(file)


# --------------------------------------------------
# 2. Load the latest incident correlation report
# --------------------------------------------------

correlation_files = sorted(
    glob.glob("reports/incident_correlation_*.json")
)

if correlation_files:
    correlation_file = correlation_files[-1]

    with open(correlation_file) as file:
        correlations = json.load(file)

    print("Correlation report:", correlation_file)

else:
    correlation_file = None
    correlations = []
    print("No correlation report found")


# --------------------------------------------------
# 3. Build an EC2 instance lookup
# --------------------------------------------------

instance_map = {
    instance["InstanceId"]: instance
    for instance in instances
}


# --------------------------------------------------
# 4. Build a CloudTrail EventId lookup
# --------------------------------------------------

correlation_map = {}

for change in correlations:
    for evidence in change.get("CloudTrailEvidence", []):
        event_id = evidence.get("EventId")

        if event_id:
            correlation_map.setdefault(event_id, []).append({
                "ChangeID": change.get("ChangeID"),
                "ResourceID": change.get("ResourceID"),
                "ChangeType": change.get("ChangeType"),
                "Attribute": change.get("Attribute"),
                "OldValue": change.get("OldValue"),
                "NewValue": change.get("NewValue"),
                "PreviousSnapshot": change.get("PreviousSnapshot"),
                "CurrentSnapshot": change.get("CurrentSnapshot"),
                "Correlation": change.get("Correlation"),
                "CloudTrailEvidence": evidence
            })


# --------------------------------------------------
# 5. Risk classification
# --------------------------------------------------

HIGH_RISK = [
    "TerminateInstances",
    "DeleteSecurityGroup",
    "DeleteVpc",
    "DeleteSubnet",
    "DeleteNetworkAcl",
    "DeleteRouteTable",
    "RevokeSecurityGroupIngress"
]

MEDIUM_RISK = [
    "StopInstances",
    "ModifyInstanceAttribute",
    "AuthorizeSecurityGroupIngress",
    "AuthorizeSecurityGroupEgress",
    "RevokeSecurityGroupEgress",
    "ModifySecurityGroupRules",
    "ModifyVpcAttribute",
    "ModifySubnetAttribute"
]

LOW_RISK = [
    "StartInstances",
    "SendSSHPublicKey",
    "CreateTags",
    "DeleteTags"
]


# --------------------------------------------------
# 6. Generate incident report
# --------------------------------------------------

report = []

for event in events:

    if str(event.get("ReadOnly")).lower() != "false":
        continue

    action = event.get("EventName", "Unknown")

    if action in HIGH_RISK:
        risk = "HIGH"
    elif action in MEDIUM_RISK:
        risk = "MEDIUM"
    elif action in LOW_RISK:
        risk = "LOW"
    else:
        risk = "OTHER"

    event_id = event.get("EventId")

    matched_instances = []

    for resource in event.get("Resources", []):
        resource_name = resource.get("ResourceName", "")

        if resource_name in instance_map:
            matched_instances.append(instance_map[resource_name])

    correlated_changes = correlation_map.get(event_id, [])

    correlation_status = (
        "MATCHED" if correlated_changes else "UNMATCHED"
    )

    # Extract the state transition recorded at event time by CloudTrail
    cloudtrail_event = event.get("CloudTrailEvent", {})
    response_elements = cloudtrail_event.get("responseElements") or {}
    state_items = (
        response_elements
        .get("instancesSet", {})
        .get("items", [])
    )

    event_state_transitions = []

    for item in state_items:
        previous_state = item.get("previousState", {}).get("name")
        current_state = item.get("currentState", {}).get("name")

        event_state_transitions.append({
            "InstanceId": item.get("instanceId"),
            "PreviousState": previous_state,
            "CurrentState": current_state
        })

    # Keep latest snapshot state separate from historical event state
    latest_snapshot_states = [
        {
            "InstanceId": instance.get("InstanceId"),
            "State": instance.get("State", {}).get("Name") if isinstance(instance.get("State"), dict) else instance.get("State")
        }
        for instance in matched_instances
    ]

    report.append({
        "EventId": event_id,
        "RiskLevel": risk,
        "Action": action,
        "EventTime": event.get("EventTime"),
        "Username": event.get("Username"),
        "Service": event.get("EventSource"),
        "Resources": event.get("Resources", []),
        "MatchedInstances": matched_instances,
        "EventStateTransitions": event_state_transitions,
        "LatestSnapshotStates": latest_snapshot_states,
        "CorrelationStatus": correlation_status,
        "CorrelatedChanges": correlated_changes
    })


# --------------------------------------------------
# 7. Save incident report as JSON
# --------------------------------------------------

os.makedirs("reports", exist_ok=True)

filename = datetime.now().strftime(
    "incident_report_%Y%m%d_%H%M%S.json"
)

filepath = os.path.join("reports", filename)

with open(filepath, "w") as file:
    json.dump(report, file, indent=4, default=str)


# --------------------------------------------------
# 8. Display incident report
# --------------------------------------------------

print("\nINFRASTRUCTURE INCIDENT REPORT")
print("==============================")

print("Snapshot:", snapshot_file)
print("CloudTrail:", cloudtrail_file)
print("Write events analyzed:", len(report))

matched_count = 0
unmatched_count = 0

for item in report:

    print("\nRisk:", item["RiskLevel"])
    print("Action:", item["Action"])
    print("Time:", item["EventTime"])
    print("User:", item["Username"])
    print("Event ID:", item["EventId"])

    if item["MatchedInstances"]:
        for instance in item["MatchedInstances"]:
            print("Affected resource:", instance["InstanceId"])
            print("Instance state:", instance["State"])
    else:
        print("Affected resource: No EC2 match found")

    print("Correlation:", item["CorrelationStatus"])

    if item["CorrelatedChanges"]:
        matched_count += 1

        for change in item["CorrelatedChanges"]:
            print("  Change ID:", change["ChangeID"])
            print("  Resource:", change["ResourceID"])
            print("  Attribute:", change["Attribute"])
            print("  Old value:", change["OldValue"])
            print("  New value:", change["NewValue"])

    else:
        unmatched_count += 1


print("\nCORRELATION SUMMARY")
print("===================")
print("Matched write events:", matched_count)
print("Unmatched write events:", unmatched_count)

print("\nReport saved:", filepath)


# --------------------------------------------------
# 9. Save incident report to PostgreSQL
# --------------------------------------------------

conn = None

try:
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO incident_reports
            (
                snapshot_file,
                cloudtrail_file,
                report_file,
                total_events,
                report_data
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                snapshot_file,
                cloudtrail_file,
                filepath,
                len(report),
                Json(report)
            )
        )

    conn.commit()

    print("Incident report successfully saved to PostgreSQL!")

except Exception as error:

    if conn:
        conn.rollback()

    print("PostgreSQL save failed:", error)
    raise

finally:

    if conn:
        conn.close()
