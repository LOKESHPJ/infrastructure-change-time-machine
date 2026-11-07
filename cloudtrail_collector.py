
import boto3
import json
import os
from datetime import datetime, timedelta, timezone

from database import get_connection
from psycopg2.extras import Json


# Connect to AWS CloudTrail
cloudtrail = boto3.client(
    "cloudtrail",
    region_name="us-east-1"
)

# Collect events from the previous 24 hours
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(hours=24)

response = cloudtrail.lookup_events(
    StartTime=start_time,
    EndTime=end_time,
    MaxResults=50
)

events = []

for event in response["Events"]:
    events.append({
        "EventId": event.get("EventId"),
        "EventName": event.get("EventName"),
        "EventTime": event.get("EventTime").isoformat(),
        "Username": event.get("Username"),
        "EventSource": event.get("EventSource"),
        "ReadOnly": event.get("ReadOnly"),
        "Resources": event.get("Resources", [])
    })


# Save events as a JSON file
os.makedirs("cloudtrail_logs", exist_ok=True)

filename = datetime.now().strftime(
    "cloudtrail_%Y%m%d_%H%M%S.json"
)

filepath = os.path.join("cloudtrail_logs", filename)

with open(filepath, "w") as file:
    json.dump(events, file, indent=4, default=str)

print("\nCLOUDTRAIL COLLECTION REPORT")
print("============================")
print("Events collected:", len(events))
print("File saved:", filepath)


# Save events into PostgreSQL
if events:
    conn = None

    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            for event in events:

                event_time = datetime.fromisoformat(
                    event["EventTime"]
                ).astimezone(timezone.utc).replace(tzinfo=None)

                cursor.execute(
                    """
                    INSERT INTO cloudtrail_events
                    (
                        event_id,
                        event_name,
                        event_source,
                        username,
                        event_time,
                        event_data
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        event["EventId"],
                        event["EventName"],
                        event["EventSource"],
                        event["Username"],
                        event_time,
                        Json(event)
                    )
                )

        conn.commit()

        print(
            "CloudTrail events successfully saved to PostgreSQL!"
        )

    except Exception as error:
        if conn:
            conn.rollback()

        print("PostgreSQL save failed:", error)
        raise

    finally:
        if conn:
            conn.close()

else:
    print("No CloudTrail events to save.")
