import json
import glob
import os
from datetime import datetime
from database import get_connection
from psycopg2.extras import Json

snapshot_files = sorted(glob.glob("snapshots/*.json"))
cloudtrail_files = sorted(glob.glob("cloudtrail_logs/*.json"))

if not snapshot_files or not cloudtrail_files:
    print("Missing infrastructure snapshots or CloudTrail logs")
    exit()

snapshot_file = snapshot_files[-1]
cloudtrail_file = cloudtrail_files[-1]

with open(snapshot_file) as file:
    instances = json.load(file)

with open(cloudtrail_file) as file:
    events = json.load(file)

instance_map = {
    instance["InstanceId"]: instance
    for instance in instances
}

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

    matched_instances = []

    for resource in event.get("Resources", []):
        resource_name = resource.get("ResourceName", "")

        if resource_name in instance_map:
            matched_instances.append(instance_map[resource_name])

    report.append({
        "RiskLevel": risk,
        "Action": action,
        "EventTime": event.get("EventTime"),
        "Username": event.get("Username"),
        "Service": event.get("EventSource"),
        "Resources": event.get("Resources", []),
        "MatchedInstances": matched_instances
    })

os.makedirs("reports", exist_ok=True)

filename = datetime.now().strftime("incident_report_%Y%m%d_%H%M%S.json")
filepath = os.path.join("reports", filename)

with open(filepath, "w") as file:
    json.dump(report, file, indent=4, default=str)

print("\nINFRASTRUCTURE INCIDENT REPORT")
print("==============================")
print("Snapshot:", snapshot_file)
print("CloudTrail:", cloudtrail_file)
print("Write events analyzed:", len(report))

for item in report:
    print("\nRisk:", item["RiskLevel"])
    print("Action:", item["Action"])
    print("Time:", item["EventTime"])
    print("User:", item["Username"])

    if item["MatchedInstances"]:
        for instance in item["MatchedInstances"]:
            print("Affected resource:", instance["InstanceId"])
            print("Instance state:", instance["State"])
    else:
        print("Affected resource: No EC2 match found")

print("\nReport saved:", filepath)
# Save incident report to PostgreSQL

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
                total_events,
                report_data
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                snapshot_file,
                cloudtrail_file,
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
