import json
import glob
import os

files = sorted(glob.glob("cloudtrail_logs/*.json"))

if not files:
    print("No CloudTrail files found")
    exit()

latest_file = files[-1]

with open(latest_file) as file:
    events = json.load(file)

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

print("\nINFRASTRUCTURE RISK ANALYSIS")
print("============================")
print("Source file:", latest_file)
print("Total events scanned:", len(events))

risk_counts = {
    "HIGH": 0,
    "MEDIUM": 0,
    "LOW": 0,
    "OTHER": 0
}

for event in events:

    if str(event.get("ReadOnly")).lower() != "false":
        continue

    action = event.get("EventName")

    if action in HIGH_RISK:
        risk = "HIGH"

    elif action in MEDIUM_RISK:
        risk = "MEDIUM"

    elif action in LOW_RISK:
        risk = "LOW"

    else:
        risk = "OTHER"

    risk_counts[risk] += 1

    print("\n[RISK LEVEL:", risk, "]")
    print("Action:", action)
    print("Time:", event.get("EventTime"))
    print("User:", event.get("Username"))
    print("Service:", event.get("EventSource"))
    print("Resources:", event.get("Resources"))

print("\nRISK SUMMARY")
print("============")

for risk, count in risk_counts.items():
    print(risk, ":", count)

print("\nTotal write events:", sum(risk_counts.values()))
