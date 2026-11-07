import json
import glob
import os

snapshot_files = sorted(glob.glob("snapshots/*.json"))
cloudtrail_files = sorted(glob.glob("cloudtrail_logs/*.json"))

if not snapshot_files or not cloudtrail_files:
    print("Missing snapshots or CloudTrail logs")
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

print("\nINCIDENT RESOURCE CORRELATION")
print("=============================")

print("Snapshot:", snapshot_file)
print("CloudTrail:", cloudtrail_file)

matched = 0
unmatched = 0

for event in events:

    if str(event.get("ReadOnly")).lower() != "false":
        continue

    resources = event.get("Resources", [])
    event_matched = False

    for resource in resources:

        resource_name = resource.get("ResourceName", "")

        if resource_name in instance_map:

            instance = instance_map[resource_name]
            event_matched = True
            matched += 1

            print("\n[RESOURCE MATCHED]")
            print("Action:", event.get("EventName"))
            print("Time:", event.get("EventTime"))
            print("User:", event.get("Username"))
            print("Instance ID:", instance["InstanceId"])
            print("Instance Type:", instance["InstanceType"])
            print("Current State:", instance["State"])
            print("Private IP:", instance["PrivateIP"])
            print("Availability Zone:", instance["AvailabilityZone"])

    if not event_matched:
        unmatched += 1

print("\nCORRELATION SUMMARY")
print("===================")
print("Matched events:", matched)
print("Unmatched write events:", unmatched)
