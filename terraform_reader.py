import json
import glob
import os
import sys

STATE_FILE = "terraform/terraform.tfstate"


def load_json(path):
    with open(path) as file:
        return json.load(file)


if not os.path.exists(STATE_FILE):
    print("ERROR: Terraform state file not found!")
    sys.exit(1)

terraform_state = load_json(STATE_FILE)

terraform_instance_ids = set()
terraform_private_ips = set()
allowed_states = set()

for resource in terraform_state.get("resources", []):
    for instance in resource.get("instances", []):
        attributes = instance.get("attributes", {})

        if resource.get("type") == "aws_instances":
            terraform_instance_ids.update(attributes.get("ids") or [])
            terraform_private_ips.update(attributes.get("private_ips") or [])
            allowed_states.update(attributes.get("instance_state_names") or [])

        elif resource.get("type") == "aws_instance":
            instance_id = attributes.get("id")
            private_ip = attributes.get("private_ip")
            if instance_id:
                terraform_instance_ids.add(instance_id)
            if private_ip:
                terraform_private_ips.add(private_ip)

snapshot_files = sorted(glob.glob("snapshots/*.json"))

if not snapshot_files:
    print("ERROR: No AWS snapshots found!")
    sys.exit(1)

latest_snapshot = snapshot_files[-1]
snapshot_data = load_json(latest_snapshot)

aws_instances = {
    instance["InstanceId"]: instance
    for instance in snapshot_data
    if instance.get("InstanceId")
}

aws_instance_ids = set(aws_instances.keys())

aws_private_ips = {
    instance["PrivateIP"]
    for instance in aws_instances.values()
    if instance.get("PrivateIP")
}

terraform_only = terraform_instance_ids - aws_instance_ids
aws_only = aws_instance_ids - terraform_instance_ids
matched = terraform_instance_ids & aws_instance_ids

missing_private_ips = terraform_private_ips - aws_private_ips
unexpected_private_ips = aws_private_ips - terraform_private_ips

print("\nTERRAFORM VS AWS INFRASTRUCTURE COMPARISON")
print("==========================================")
print("Terraform state:", STATE_FILE)
print("AWS snapshot:", latest_snapshot)

print("\nINSTANCE ID RECONCILIATION")
print("--------------------------")
print("Terraform instances:", len(terraform_instance_ids))
print("AWS snapshot instances:", len(aws_instance_ids))

print("\nMATCHED INSTANCES")
for instance_id in sorted(matched):
    instance = aws_instances[instance_id]
    print(
        "[MATCH]",
        instance_id,
        "| Type:", instance.get("InstanceType"),
        "| State:", instance.get("State"),
        "| Private IP:", instance.get("PrivateIP")
    )

print("\nTERRAFORM ONLY")
for instance_id in sorted(terraform_only):
    print("[TERRAFORM ONLY]", instance_id)

print("\nAWS ONLY")
for instance_id in sorted(aws_only):
    print("[AWS ONLY]", instance_id)

print("\nPRIVATE IP CONSISTENCY")
print("----------------------")
print("Terraform discovered IPs:", len(terraform_private_ips))
print("AWS snapshot IPs:", len(aws_private_ips))

for ip in sorted(terraform_private_ips & aws_private_ips):
    print("[IP MATCH]", ip)

for ip in sorted(missing_private_ips):
    print("[IP MISSING FROM AWS SNAPSHOT]", ip)

for ip in sorted(unexpected_private_ips):
    print("[IP NOT IN TERRAFORM DISCOVERY]", ip)

print("\nINSTANCE STATE OBSERVATIONS")
print("---------------------------")
if allowed_states:
    print("Terraform allowed states:", ", ".join(sorted(allowed_states)))

for instance_id, instance in sorted(aws_instances.items()):
    state = instance.get("State", "unknown")
    status = "ALLOWED" if not allowed_states or state in allowed_states else "OUTSIDE ALLOWED STATES"
    print("[{}] {} -> {}".format(status, instance_id, state))

print("\nCOMPARISON SUMMARY")
print("==================")
print("Matched instances:", len(matched))
print("Terraform only:", len(terraform_only))
print("AWS only:", len(aws_only))
print("Matched private IPs:", len(terraform_private_ips & aws_private_ips))
print("Missing private IPs:", len(missing_private_ips))
print("Unexpected private IPs:", len(unexpected_private_ips))

print("\nNOTE: This is inventory consistency checking, not full Terraform configuration drift detection.")
