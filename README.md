# Infrastructure Change Time Machine

An AWS infrastructure monitoring, change-tracking, and incident investigation project built using Python, Boto3, Terraform, Docker, and PostgreSQL.

The project captures AWS infrastructure snapshots, detects infrastructure changes, analyzes CloudTrail activity, correlates events with affected resources, generates incident reports, and recommends recovery actions.

## Project Overview

Infrastructure changes can happen because of manual actions, automation, or configuration updates. Identifying what changed, when it changed, and which resources were affected is important for cloud operations and incident investigation.

Infrastructure Change Time Machine provides a centralized workflow to:

- Capture AWS EC2 infrastructure snapshots.
- Store infrastructure history in PostgreSQL.
- Detect changes between consecutive snapshots.
- Collect and analyze AWS CloudTrail events.
- Identify potentially risky write operations.
- Detect transient infrastructure activities.
- Correlate CloudTrail events with EC2 resources.
- Generate structured incident reports.
- Recommend recovery actions without automatically modifying infrastructure.
- Compare Terraform state with actual AWS infrastructure inventory.

## Architecture

```text
                    AWS CLOUD
                        |
             +----------+----------+
             |                     |
          Amazon EC2           CloudTrail
             |                     |
             v                     v
       AWS Collector       CloudTrail Collector
             |                     |
             v                     v
       Infrastructure       Event Analyzer
         Snapshots                 |
             |                     v
             v              Transient Activity
       Change Detector          Detector
             |                     |
             +----------+----------+
                        |
                        v
                Incident Correlator
                        |
                        v
                 Incident Report
                        |
                        v
                 Recovery Planner
                        |
                        v
                   PostgreSQL
                        |
             +----------+----------+
             |                     |
             v                     v
         Terraform               Docker
         Comparison          Containerization
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Automation and processing |
| Boto3 | AWS API integration |
| Amazon EC2 | Infrastructure inventory |
| AWS CloudTrail | Activity and event collection |
| Terraform | Infrastructure state comparison |
| PostgreSQL | Historical data storage |
| Docker | Application containerization |
| Docker Compose | Multi-container orchestration |
| Linux | Project execution environment |
| Git and GitHub | Version control |

## Core Modules

| Module | Responsibility |
|---|---|
| `aws_collector.py` | Collects EC2 infrastructure snapshots |
| `change_detector.py` | Detects changes between snapshots |
| `cloudtrail_collector.py` | Collects CloudTrail events |
| `event_analyzer.py` | Analyzes write events and assigns heuristic risk levels |
| `transient_activity_detector.py` | Identifies transient infrastructure activities |
| `incident_correlator.py` | Matches CloudTrail events to EC2 resources |
| `incident_report.py` | Generates structured incident reports |
| `recovery_planner.py` | Recommends recovery actions |
| `recovery_logic.py` | Supports recovery recommendation logic |
| `terraform_reader.py` | Compares Terraform state with AWS inventory |
| `database.py` | Manages PostgreSQL connections |
| `database_schema.sql` | Defines database tables |
| `run_pipeline.py` | Coordinates the project workflow |

## Project Workflow

1. Collect AWS EC2 infrastructure information.
2. Save timestamped snapshots as JSON files.
3. Store snapshot information in PostgreSQL.
4. Compare consecutive snapshots to identify changes.
5. Collect recent CloudTrail events.
6. Analyze write operations and assign heuristic risk levels.
7. Detect transient infrastructure activities.
8. Correlate events with infrastructure resources.
9. Generate incident reports.
10. Recommend recovery actions.
11. Compare Terraform state with AWS inventory.

## Database

PostgreSQL stores historical project data, including:

- Infrastructure snapshots
- Infrastructure changes
- CloudTrail events
- Incident reports
- Recovery plans

The database maintains relationships between incident reports and recovery plans to support incident investigation and traceability.

## Security Design

- Uses an EC2 IAM role for AWS API access.
- Uses read-only AWS permissions for infrastructure discovery.
- Avoids storing AWS access keys in source code or Docker images.
- Uses environment variables for database credentials.
- Excludes sensitive Terraform state and generated data from Git.
- Runs the application container as a non-root user.
- Enables Docker's `no-new-privileges` security option.
- Does not automatically execute recovery actions.

## Docker

The application is packaged using Docker and Docker Compose.

The application and PostgreSQL database run as separate services.

Validate the Compose configuration:

```bash
docker compose config -q
```

Build the application image:

```bash
docker compose build app
```

Run the complete pipeline:

```bash
docker compose run --rm app python -u run_pipeline.py
```

Check container status:

```bash
docker compose ps -a
```

## Terraform Integration

Terraform is used to maintain infrastructure configuration and state.

The project reads Terraform state and compares recorded EC2 instance IDs and available private IP information with the actual AWS infrastructure inventory.

This provides an inventory consistency check that can help identify differences between Terraform state and discovered AWS resources.

This functionality is an inventory comparison, not a complete Terraform configuration drift detection engine.

## Recovery Planning

The recovery planner analyzes incident information and generates recommended recovery actions.

Recovery execution is intentionally disabled:

```python
automatic_execution = False
```

This ensures that the system recommends actions for investigation rather than automatically modifying production infrastructure.

## Project Status

The project includes the following implemented components:

- AWS EC2 infrastructure collection
- Infrastructure snapshot generation
- Change detection
- CloudTrail event collection and analysis
- Transient activity detection
- Incident correlation
- Incident report generation
- Recovery recommendations
- PostgreSQL persistence
- Terraform inventory comparison
- Docker-based application execution

The integrated pipeline has been tested across its major stages.

## Future Improvements

- CloudTrail pagination and duplicate-event handling.
- More detailed infrastructure change detection.
- Automated scheduled snapshots.
- Improved risk classification.
- Web-based incident dashboard.
- Multi-region AWS inventory support.
- Infrastructure dependency tracking.
- Historical infrastructure reconstruction.
- More advanced recovery validation.

## Author

**Lokesh P J**

GitHub: [LOKESHPJ](https://github.com/LOKESHPJ)
