terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
data "aws_instances" "all" {
  instance_state_names = ["pending", "running", "stopping", "stopped"]
}

output "aws_instance_ids" {
  description = "EC2 instances discovered by Terraform"
  value       = data.aws_instances.all.ids
}
