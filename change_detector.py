import json
import os
from database import get_connection

snapshot_dir = "snapshots"

files = sorted(
    f for f in os.listdir(snapshot_dir)
    if f.endswith(".json")
)

if len(files) < 2:
    print("Need at least two snapshots")
    exit()

old_file = os.path.join(snapshot_dir, files[-2])
new_file = os.path.join(snapshot_dir, files[-1])

with open(old_file) as f:
    old_data = json.load(f)

with open(new_file) as f:
    new_data = json.load(f)

old_instances = {i["InstanceId"]: i for i in old_data}
new_instances = {i["InstanceId"]: i for i in new_data}

changes = []

for instance_id in new_instances.keys() - old_instances.keys():
    changes.append({
        "resource_id": instance_id,
        "change_type": "NEW INSTANCE",
        "attribute": "Instance",
        "old_value": None,
        "new_value": "Created"
    })

for instance_id in old_instances.keys() - new_instances.keys():
    changes.append({
        "resource_id": instance_id,
        "change_type": "DELETED INSTANCE",
        "attribute": "Instance",
        "old_value": "Present",
        "new_value": None
    })

for instance_id in old_instances.keys() & new_instances.keys():
    old = old_instances[instance_id]
    new = new_instances[instance_id]

    for key in new:
        if old.get(key) != new.get(key):
            changes.append({
                "resource_id": instance_id,
                "change_type": "MODIFIED",
                "attribute": key,
                "old_value": str(old.get(key)),
                "new_value": str(new.get(key))
            })

print("\nINFRASTRUCTURE CHANGE REPORT")
print("============================")
print("Previous snapshot:", files[-2])
print("Current snapshot:", files[-1])

if changes:
    for change in changes:
        print(
            "[CHANGE DETECTED]",
            change["resource_id"],
            change["attribute"],
            change["old_value"],
            "->",
            change["new_value"]
        )

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        for change in changes:
            cursor.execute(
                """
                INSERT INTO infrastructure_changes
                (resource_id, change_type, attribute, old_value, new_value)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    change["resource_id"],
                    change["change_type"],
                    change["attribute"],
                    change["old_value"],
                    change["new_value"]
                )
            )

        conn.commit()
        cursor.close()

        print("\nChanges successfully saved to PostgreSQL!")

    except Exception as error:
        if conn:
            conn.rollback()
        print("Database save failed:", error)
        raise

    finally:
        if conn:
            conn.close()

else:
    print("[OK] NO INFRASTRUCTURE CHANGES DETECTED")

print("\nTotal changes detected:", len(changes))
