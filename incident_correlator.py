import json
import os
from datetime import datetime
from database import get_connection

def parse_snapshot_time(filename):
    timestamp = os.path.basename(filename).replace(
        "snapshot_", ""
    ).replace(".json", "")

    return datetime.strptime(timestamp, "%Y%m%d_%H%M%S")


def extract_event_details(event_data):
    cloudtrail = event_data.get("CloudTrailEvent", {})
    params = cloudtrail.get("requestParameters") or {}

    resources = params.get("resourcesSet", {}).get("items", [])
    tags = params.get("tagSet", {}).get("items", [])

    return cloudtrail, resources, tags


connection = None
cursor = None
results = []

try:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            resource_id,
            change_type,
            attribute,
            old_value,
            new_value,
            previous_snapshot,
            current_snapshot
        FROM infrastructure_changes
        WHERE previous_snapshot IS NOT NULL
          AND current_snapshot IS NOT NULL
        ORDER BY id
    """)

    changes = cursor.fetchall()

    cursor.execute("""
        SELECT
            event_id,
            event_name,
            event_source,
            username,
            event_time,
            event_data
        FROM cloudtrail_events
        ORDER BY event_time
    """)

    events = cursor.fetchall()

    print("\nINFRASTRUCTURE INCIDENT CORRELATION")
    print("===================================")
    print("Changes analyzed:", len(changes))
    print("CloudTrail events analyzed:", len(events))

    matched_count = 0
    unmatched_count = 0

    for change in changes:
        (
            change_id,
            resource_id,
            change_type,
            attribute,
            old_value,
            new_value,
            previous_snapshot,
            current_snapshot
        ) = change

        start_time = parse_snapshot_time(previous_snapshot)
        end_time = parse_snapshot_time(current_snapshot)

        tag_key = (
            attribute.split(":", 1)[1]
            if attribute and attribute.startswith("Tag:")
            else None
        )

        matching_events = []

        for event in events:
            (
                event_id,
                event_name,
                event_source,
                username,
                event_time,
                event_data
            ) = event

            if not event_time or not (
                start_time <= event_time.replace(tzinfo=None) <= end_time
            ):
                continue

            payload = event_data or {}
            cloudtrail, resources, tags = extract_event_details(payload)

            if not cloudtrail:
                continue

            resource_matches = any(
                item.get("resourceId") == resource_id
                for item in resources
            )

            if not resource_matches:
                resource_matches = any(
                    item.get("ResourceName") == resource_id
                    for item in payload.get("Resources", [])
                )

            if not resource_matches:
                continue

            if tag_key:
                tag_matches = any(
                    tag.get("key") == tag_key
                    and str(tag.get("value")) == str(new_value)
                    for tag in tags
                )

                if event_name == "DeleteTags":
                    tag_matches = any(
                        tag.get("key") == tag_key
                        for tag in tags
                    )

                if not tag_matches:
                    continue

            matching_events.append({
                "EventId": event_id,
                "APIAction": event_name,
                "Actor": username,
                "EventTime": event_time.isoformat(),
                "EventSource": event_source
            })

        status = "MATCHED" if matching_events else "UNMATCHED"

        if matching_events:
            matched_count += 1
        else:
            unmatched_count += 1

        result = {
            "ChangeID": change_id,
            "ResourceID": resource_id,
            "ChangeType": change_type,
            "Attribute": attribute,
            "OldValue": old_value,
            "NewValue": new_value,
            "PreviousSnapshot": previous_snapshot,
            "CurrentSnapshot": current_snapshot,
            "Correlation": status,
            "CloudTrailEvidence": matching_events
        }

        results.append(result)

        print("\nRESOURCE:", resource_id)
        print("CHANGE:", attribute)
        print("OLD VALUE:", old_value)
        print("NEW VALUE:", new_value)

        if matching_events:
            for evidence in matching_events:
                print("API ACTION:", evidence["APIAction"])
                print("ACTOR:", evidence["Actor"])
                print("EVENT TIME:", evidence["EventTime"])
        else:
            print("API ACTION: No matching event")
            print("ACTOR: Unknown")

        print("CORRELATION:", status)

    os.makedirs("reports", exist_ok=True)

    filename = datetime.now().strftime(
        "incident_correlation_%Y%m%d_%H%M%S.json"
    )
    filepath = os.path.join("reports", filename)

    with open(filepath, "w") as file:
        json.dump(results, file, indent=4, default=str)

    print("\nCORRELATION SUMMARY")
    print("===================")
    print("Matched changes:", matched_count)
    print("Unmatched changes:", unmatched_count)
    print("Report saved:", filepath)

except Exception as error:
    if connection:
        connection.rollback()

    print("Correlation failed:", error)
    raise

finally:
    if cursor:
        cursor.close()

    if connection:
        connection.close()
