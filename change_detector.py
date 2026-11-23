
import json
import os
from database import get_connection

snapshot_dir = "snapshots"

files = sorted(
    f for f in os.listdir(snapshot_dir)
    if f.startswith("snapshot_") and f.endswith(".json")
)

if len(files) < 2:
    print("Need at least two snapshots")
    raise SystemExit(1)

old_file = os.path.join(snapshot_dir, files[-2])
new_file = os.path.join(snapshot_dir, files[-1])

with open(old_file) as f:
    old_data = json.load(f)

with open(new_file) as f:
    new_data = json.load(f)


def validate_snapshot(data, filename):
    if not isinstance(data, list):
        raise ValueError(f"{filename}: snapshot root must be a list")

    seen_ids = set()

    for index, instance in enumerate(data):
        if not isinstance(instance, dict):
            raise ValueError(f"{filename}: record {index} must be an object")

        instance_id = instance.get("InstanceId")

        if not isinstance(instance_id, str) or not instance_id.strip():
            raise ValueError(f"{filename}: record {index} has an invalid InstanceId")

        if instance_id in seen_ids:
            raise ValueError(f"{filename}: duplicate InstanceId {instance_id}")

        seen_ids.add(instance_id)

        tags = instance.get("Tags", {})
        if tags is not None and not isinstance(tags, dict):
            raise ValueError(f"{filename}: invalid Tags for {instance_id}")

    print(f"[OK] Snapshot validated: {filename} ({len(data)} instances)")


validate_snapshot(old_data, files[-2])
validate_snapshot(new_data, files[-1])
old_instances = {i["InstanceId"]: i for i in old_data}
new_instances = {i["InstanceId"]: i for i in new_data}

changes = []

# Detect new instances
for instance_id in sorted(new_instances.keys() - old_instances.keys()):
    changes.append({
        "resource_id": instance_id,
        "change_type": "NEW INSTANCE",
        "attribute": "Instance",
        "old_value": None,
        "new_value": "Created"
    })

# Detect deleted instances
for instance_id in sorted(old_instances.keys() - new_instances.keys()):
    changes.append({
        "resource_id": instance_id,
        "change_type": "DELETED INSTANCE",
        "attribute": "Instance",
        "old_value": "Present",
        "new_value": None
    })

# Detect modifications
for instance_id in sorted(old_instances.keys() & new_instances.keys()):
    old = old_instances[instance_id]
    new = new_instances[instance_id]

    for key in sorted(old.keys() | new.keys()):
        old_value = old.get(key)
        new_value = new.get(key)

        # Compare individual tags
        if key == "Tags":
            old_tags = old_value or {}
            new_tags = new_value or {}

            for tag_key in sorted(old_tags.keys() | new_tags.keys()):
                old_tag = old_tags.get(tag_key)
                new_tag = new_tags.get(tag_key)

                if old_tag != new_tag:
                    changes.append({
                        "resource_id": instance_id,
                        "change_type": "MODIFIED",
                        "attribute": f"Tag:{tag_key}",
                        "old_value": str(old_tag) if old_tag is not None else None,
                        "new_value": str(new_tag) if new_tag is not None else None
                    })

        elif old_value != new_value:
            changes.append({
                "resource_id": instance_id,
                "change_type": "MODIFIED",
                "attribute": key,
                "old_value": str(old_value) if old_value is not None else None,
                "new_value": str(new_value) if new_value is not None else None
            })

# Display report
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
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        inserted_count = 0

        for change in changes:
            cursor.execute(
                """
                INSERT INTO infrastructure_changes
                (
                    resource_id,
                    change_type,
                    attribute,
                    old_value,
                    new_value,
                    previous_snapshot,
                    current_snapshot
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (
                    change["resource_id"],
                    change["change_type"],
                    change["attribute"],
                    change["old_value"],
                    change["new_value"],
                    files[-2],
                    files[-1]
                )
            )

            inserted_count += cursor.rowcount

        conn.commit()

        print("\nNew changes saved:", inserted_count)
        print("Duplicate changes skipped:", len(changes) - inserted_count)

    except Exception as error:
        if conn:
            conn.rollback()

        print("Database save failed:", error)
        raise

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

else:
    print("[OK] NO INFRASTRUCTURE CHANGES DETECTED")

print("\nTotal changes detected:", len(changes))
