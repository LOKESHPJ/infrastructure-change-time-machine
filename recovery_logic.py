def get_recovery_action(incident):
    action = incident.get("Action", "Unknown")
    risk = incident.get("RiskLevel", "OTHER")

    if action == "TerminateInstances":
        return [
            "Check whether the instance termination was authorized.",
            "Identify the affected instance and its dependencies.",
            "Check available backups, AMIs, and recovery options.",
            "Restore the workload using an approved recovery procedure."
        ]

    elif action == "StopInstances":
        return [
            "Verify whether stopping the instance was intentional.",
            "Check application availability and dependent services.",
            "Confirm whether the instance should be restarted.",
            "If approved, start the instance and verify application health."
        ]

    elif action in [
        "AuthorizeSecurityGroupIngress",
        "AuthorizeSecurityGroupEgress",
        "ModifySecurityGroupRules"
    ]:
        return [
            "Inspect the security group rule changes.",
            "Verify whether the new network access is authorized.",
            "Check for unintended public or excessive access.",
            "If unauthorized, prepare a controlled rule rollback."
        ]

    elif action in [
        "DeleteSecurityGroup",
        "DeleteVpc",
        "DeleteSubnet",
        "DeleteNetworkAcl",
        "DeleteRouteTable"
    ]:
        return [
            "Identify the deleted networking resource and dependencies.",
            "Check service connectivity and application impact.",
            "Review available infrastructure backups and Terraform state.",
            "Prepare an infrastructure restoration plan."
        ]

    elif action == "ModifyInstanceAttribute":
        return [
            "Review the changed EC2 instance attributes.",
            "Compare the current configuration with the previous snapshot.",
            "Determine whether the modification affected service availability.",
            "Prepare a rollback using the approved configuration."
        ]

    elif action == "SendSSHPublicKey":
        return [
            "Verify whether the EC2 Instance Connect access was authorized.",
            "Review the identity and source details in the full CloudTrail event.",
            "Check for unexpected administrative activity.",
            "No infrastructure rollback is required if the access was legitimate."
        ]

    elif risk == "HIGH":
        return [
            "Investigate the high-risk infrastructure event immediately.",
            "Identify affected resources and service dependencies.",
            "Review CloudTrail details and infrastructure snapshots.",
            "Prepare an approved recovery or rollback procedure."
        ]

    elif risk == "MEDIUM":
        return [
            "Review the infrastructure configuration change.",
            "Determine whether any service was affected.",
            "Compare the configuration with the previous known state.",
            "Prepare a rollback if the change was unauthorized."
        ]

    else:
        return [
            "Review the event and verify whether it was authorized.",
            "Check the affected infrastructure resource.",
            "Monitor for unexpected changes or service impact."
        ]
