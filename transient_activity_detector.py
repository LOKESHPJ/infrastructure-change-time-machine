import json
import os
from datetime import datetime

from database import get_connection


STATE_EVENTS = {
    "StartInstances",
    "StopInstances",
    "RebootInstances"
}

ACCESS_EVENTS = {
    "SendSSHPublicKey"
}


def get_instance_ids(event_name, cloudtrail):
    if not isinstance(cloudtrail, dict):
        return []

    params = cloudtrail.get("requestParameters") or {}

    if not isinstance(params, dict):
        return []

    if event_name in ACCESS_EVENTS:
        instance_id = params.get("instanceId")
        return [instance_id] if isinstance(instance_id, str) and instance_id else []

    instance_set = params.get("instancesSet") or {}

    if not isinstance(instance_set, dict):
        return []

    items = instance_set.get("items") or []

    if not isinstance(items, list):
        return []

    return [
        item.get("instanceId")
        for item in items
        if isinstance(item, dict)
        and isinstance(item.get("instanceId"), str)
        and item.get("instanceId")
    ]


def analyze_event(event):
    try:
        (
            event_id,
            event_name,
            username,
            event_time,
            event_data
        ) = event

        if event_name not in STATE_EVENTS and event_name not in ACCESS_EVENTS:
            return None

        payload = event_data or {}

        if isinstance(payload, str):
            payload = json.loads(payload)

        if not isinstance(payload, dict):
            return None

        cloudtrail = payload.get("CloudTrailEvent", {})

        if isinstance(cloudtrail, str):
            cloudtrail = json.loads(cloudtrail)

        has_details = isinstance(cloudtrail, dict) and bool(cloudtrail)

        if not has_details:
            cloudtrail = {}

        outcome = (
            "DETAILS_UNAVAILABLE" if not has_details
            else "FAILED" if cloudtrail.get("errorCode")
            else "API_SUCCESS"
        )

        instance_ids = get_instance_ids(event_name, cloudtrail)

        # Fall back to top-level resource references when full details are missing.
        if not instance_ids and not has_details:
            resources = payload.get("Resources") or []

            if isinstance(resources, list):
                instance_ids = [
                    resource.get("ResourceName")
                    for resource in resources
                    if isinstance(resource, dict)
                    and resource.get("ResourceType") == "AWS::EC2::Instance"
                    and isinstance(resource.get("ResourceName"), str)
                    and resource.get("ResourceName")
                ]

        category = (
            "INSTANCE_STATE_TRANSITION"
            if event_name in STATE_EVENTS
            else "INSTANCE_ACCESS"
        )

        response = cloudtrail.get("responseElements") or {}

        if not isinstance(response, dict):
            response = {}

        instance_set = response.get("instancesSet") or {}

        if not isinstance(instance_set, dict):
            instance_set = {}

        response_items = instance_set.get("items") or []

        if not isinstance(response_items, list):
            response_items = []

        transitions = []

        for item in response_items:
            if not isinstance(item, dict):
                continue

            previous = item.get("previousState")
            current = item.get("currentState")

            transitions.append({
                "InstanceId": item.get("instanceId"),
                "PreviousState": (
                    previous.get("name")
                    if isinstance(previous, dict) else None
                ),
                "CurrentState": (
                    current.get("name")
                    if isinstance(current, dict) else None
                )
            })

        return {
            "EventId": event_id,
            "EventName": event_name,
            "Category": category,
            "Outcome": outcome,
            "Username": username,
            "EventTime": event_time.isoformat() if event_time else None,
            "SourceIPAddress": cloudtrail.get("sourceIPAddress"),
            "InstanceIDs": instance_ids,
            "StateTransitions": transitions,
            "Evidence": (
                "CloudTrail API event"
                if has_details
                else "Top-level EC2 resource reference; full event details unavailable"
            )
        }

    except (ValueError, TypeError, AttributeError, KeyError) as error:
        print(
            "Skipping malformed CloudTrail event:",
            event[0] if isinstance(event, (tuple, list)) and event else "Unknown",
            "-",
            str(error)
        )
        return None


def main():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                event_id,
                event_name,
                username,
                event_time,
                event_data
            FROM cloudtrail_events
            WHERE event_name IN (
                'StartInstances',
                'StopInstances',
                'RebootInstances',
                'SendSSHPublicKey'
            )
            ORDER BY event_time
        """)

        events = cursor.fetchall()

        activities = []

        for event in events:
            result = analyze_event(event)

            if result:
                activities.append(result)

        os.makedirs("reports", exist_ok=True)

        filename = datetime.now().strftime(
            "transient_activity_%Y%m%d_%H%M%S.json"
        )

        filepath = os.path.join("reports", filename)

        with open(filepath, "w") as file:
            json.dump(activities, file, indent=4)

        print("\nTRANSIENT INFRASTRUCTURE ACTIVITY REPORT")
        print("========================================")
        print("Events analyzed:", len(events))
        print("Activities identified:", len(activities))

        for activity in activities:
            print("\nEVENT:", activity["EventName"])
            print("CATEGORY:", activity["Category"])
            print("OUTCOME:", activity["Outcome"])
            print("INSTANCE IDs:", activity["InstanceIDs"])

            for transition in activity["StateTransitions"]:
                print(
                    "STATE:",
                    transition["PreviousState"],
                    "->",
                    transition["CurrentState"]
                )

        print("\nReport saved:", filepath)

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":
    main()
