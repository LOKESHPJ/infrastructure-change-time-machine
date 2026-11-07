import boto3
import json
from datetime import datetime
import os
from database import get_connection
from psycopg2.extras import Json

ec2 = boto3.client("ec2", region_name="us-east-1")

response = ec2.describe_instances()

instances = []

for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        instances.append({
            "InstanceId": instance["InstanceId"],
            "InstanceType": instance["InstanceType"],
            "State": instance["State"]["Name"],
            "PrivateIP": instance.get("PrivateIpAddress", "N/A"),
            "AvailabilityZone": instance["Placement"]["AvailabilityZone"]
        })

os.makedirs("snapshots", exist_ok=True)

filename = datetime.now().strftime("snapshot_%Y%m%d_%H%M%S.json")
filepath = os.path.join("snapshots", filename)

with open(filepath, "w") as file:
    json.dump(instances, file, indent=4)

print("Infrastructure snapshot saved successfully!")
print("File:", filepath)
print("Total EC2 instances:", len(instances))

conn = None

try:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO infrastructure_snapshots
        (source, instance_count, snapshot_data)
        VALUES (%s, %s, %s)
        """,
        ("AWS", len(instances), Json(instances))
    )

    conn.commit()
    cursor.close()

    print("Snapshot successfully saved to PostgreSQL!")

except Exception as error:
    if conn:
        conn.rollback()
    print("PostgreSQL save failed:", error)
    raise

finally:
    if conn:
        conn.close()
