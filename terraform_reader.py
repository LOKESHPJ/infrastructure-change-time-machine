import json
import glob
import os

STATE_FILE = "terraform/terraform.tfstate"

if not os.path.exists(STATE_FILE):
    print("Terraform state file not found!")
    exit()

with open(STATE_FILE) as file:
    terraform_state = json.load(file)

terraform_instance_ids = set()

for resource in terraform_state.get("resources", []):
    if resource.get("type") == "aws_instances":
        for instance in resource.get("instances", []):
            attributes = instance.get("attributes", {})
            terraform_instance_ids.update(attributes.get("ids", []))

    if resource.get("type") == "aws_instance":
        for instance in resource.get("instances", []):
            instance_id = instance.get("attributes", {}).get("id")
            if instance_id:
                terraform_instance_ids.add(instance_id)

snapshot_files = sorted(glob.glob("snapshots/*.json"))

if not snapshot_files:
    print("No AWS snapshots found!")
    exit()

latest_snapshot = snapshot_files[-1]

with open(latest_snapshot) as file:
    snapshot_data = json.load(file)

aws_instance_ids = {
    instance["InstanceId"]
    for instance in snapshot_data
}

terraform_only = terraform_instance_ids - aws_instance_ids
aws_only = aws_instance_ids - terraform_instance_ids
matched = terraform_instance_ids & aws_instance_ids

print("\nTERRAFORM VS AWS INFRASTRUCTURE COMPARISON")
print("==========================================")
print("Terraform state:", STATE_FILE)
print("AWS snapshot:", latest_snapshot)

print("\nTerraform instances:", len(terraform_instance_ids))
print("AWS snapshot instances:", len(aws_instance_ids))

print("\nMATCHED INSTANCES")
for instance_id in sorted(matched):
    print("[MATCH]", instance_id)

print("\nTERRAFORM ONLY")
for instance_id in sorted(terraform_only):
    print("[TERRAFORM ONLY]", instance_id)

print("\nAWS ONLY")
for instance_id in sorted(aws_only):
    print("[AWS ONLY]", instance_id)

print("\nCOMPARISON SUMMARY")
print("==================")
print("Matched:", len(matched))
print("Terraform only:", len(terraform_only))
print("AWS only:", len(aws_only))
