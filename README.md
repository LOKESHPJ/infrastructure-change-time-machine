# Infrastructure Change Time Machine

An AWS infrastructure monitoring and change-tracking project built using Python, Boto3, Terraform, Docker, and PostgreSQL.

The project captures AWS infrastructure snapshots, detects infrastructure changes, analyzes CloudTrail activity, correlates events with affected resources, generates incident reports, and recommends recovery actions.

## Project Overview

Infrastructure changes can happen because of manual actions, automation, or configuration updates. Identifying what changed, when it changed, and which resources were affected is important for cloud operations and incident investigation.

Infrastructure Change Time Machine provides a centralized workflow to:

- Capture AWS EC2 infrastructure snapshots.
- Store infrastructure history in PostgreSQL.
- Detect changes between consecutive snapshots.
- Collect and analyze AWS CloudTrail events.
- Identify potentially risky write operations.
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
          |                     |
          v                     v
    Change Detector      Incident Correlator
          |                     |
          +----------+----------+
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
      Terraform             Docker
      Comparison          Containerization
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Automation and processing |
| Boto3 | AWS API integration |
| Amazon EC2 | Infrastructure inventory |# Infrastructure Change Time Machine

An AWS infrastructure monitoring and change-tracking project built using Python, Boto3, Terraform, Docker, and PostgreSQL.

The project captures AWS infrastructure snapshots, detects infrastructure changes, analyzes CloudTrail activity, correlates events with affected resources, generates incident reports, and recommends recovery actions.

## Project Overview

Infrastructure changes can happen because of manual actions, automation, or configuration updates. Identifying what changed, when it changed, and which resources were affected is important for cloud operations and incident investigation.

Infrastructure Change Time Machine provides a centralized workflow to:

- Capture AWS EC2 infrastructure snapshots.
- Store infrastructure history in PostgreSQL.
- Detect changes between consecutive snapshots.
- Collect and analyze AWS CloudTrail events.
- Identify potentially risky write operations.
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
          |                     |
          v                     v
    Change Detector      Incident Correlator
          |                     |
          +----------+----------+
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
      Terraform             Docker
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
| Linux | Project execution environment |
| Git and GitHub | Version control |

## Core Modules

| Module | Responsibility |
|---|---|
| `aws_collector.py` | Collects EC2 infrastructure snapshots |
| `change_detector.py` | Detects changes between snapshots |
| `cloudtrail_collector.py` | Collects CloudTrail events |
| `event_analyzer.py` | Analyzes write events and assigns heuristic risk levels |
| `incident_correlator.py` | Matches CloudTrail events to EC2 resources |
| `incident_report.py` | Generates structured incident reports |
| `recovery_planner.py` | Recommends recovery actions |
| `terraform_reader.py` | Compares Terraform state with AWS inventory |
| `database.py` | Manages PostgreSQL connections |
| `database_schema.sql` | Defines database tables |

## Project Workflow

1. Collect AWS EC2 infrastructure information.
2. Save timestamped snapshots as JSON files.
3. Store snapshot information in PostgreSQL.
4. Compare consecutive snapshots to identify changes.
5. Collect recent CloudTrail events.
6. Analyze write operations and assign heuristic risk levels.
7. Correlate events with infrastructure resources.
8. Generate incident reports.
9. Recommend recovery actions.
10. Compare Terraform state with AWS inventory.

## Database

PostgreSQL stores historical project data, including:

- Infrastructure snapshots
- Infrastructure changes
- CloudTrail events
- Incident reports
- Recovery plans

## Security Design

- Uses an EC2 IAM role for AWS API access.
- Uses read-only AWS permissions for infrastructure discovery.
- Avoids storing AWS access keys in source code or Docker images.
- Uses environment variables for database credentials.
- Excludes sensitive Terraform state and generated data from Git.
- Does not automatically execute recovery actions.

## Docker

The application is packaged using Docker.

Build the image:

```bash
docker build -t infrastructure-time-machine:v1 .
```

Run the default AWS collector:

```bash
docker run --rm infrastructure-time-machine:v1
```

Additional modules can be executed by overriding the container's default command.

## Terraform Integration

Terraform is used to maintain infrastructure configuration and state.

The project reads Terraform state and compares the recorded EC2 instance IDs with the actual AWS snapshot.

This provides an inventory comparison to help identify differences between Terraform state and discovered AWS resources.

## Future Improvements

- CloudTrail pagination and duplicate-event handling.
- More detailed infrastructure change detection.
- Automated scheduled snapshots.
- Improved risk classification.
- Web-based incident dashboard.
- Multi-region AWS inventory support.
- Infrastructure dependency tracking.
- Historical infrastructure reconstruction.

## Project Status

Core AWS collection, change detection, CloudTrail analysis, incident reporting, recovery recommendations, PostgreSQL persistence, Terraform inventory comparison, and Docker execution have been implemented and tested.

## Author

**Lokesh P J**

GitHub: [LOKESHPJ](https://github.com/LOKESHPJ)# Infrastructure Change Time Machine

An AWS infrastructure monitoring and change-tracking project built using Python, Boto3, Terraform, Docker, and PostgreSQL.

The project captures AWS infrastructure snapshots, detects infrastructure changes, analyzes CloudTrail activity, correlates events with affected resources, generates incident reports, and recommends recovery actions.

## Project Overview

Infrastructure changes can happen because of manual actions, automation, or configuration updates. Identifying what changed, when it changed, and which resources were affected is important for cloud operations and incident investigation.

Infrastructure Change Time Machine provides a centralized workflow to:

- Capture AWS EC2 infrastructure snapshots.
- Store infrastructure history in PostgreSQL.
- Detect changes between consecutive snapshots.
- Collect and analyze AWS CloudTrail events.
- Identify potentially risky write operations.
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
          |                     |
          v                     v
    Change Detector      Incident Correlator
          |                     |
          +----------+----------+
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
      Terraform             Docker
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
| Linux | Project execution environment |
| Git and GitHub | Version control |

## Core Modules

| Module | Responsibility |
|---|---|
| `aws_collector.py` | Collects EC2 infrastructure snapshots |
| `change_detector.py` | Detects changes between snapshots |
| `cloudtrail_collector.py` | Collects CloudTrail events |
| `event_analyzer.py` | Analyzes write events and assigns heuristic risk levels |
| `incident_correlator.py` | Matches CloudTrail events to EC2 resources |
| `incident_report.py` | Generates structured incident reports |
| `recovery_planner.py` | Recommends recovery actions |
| `terraform_reader.py` | Compares Terraform state with AWS inventory |
| `database.py` | Manages PostgreSQL connections |
| `database_schema.sql` | Defines database tables |

## Project Workflow

1. Collect AWS EC2 infrastructure information.
2. Save timestamped snapshots as JSON files.
3. Store snapshot information in PostgreSQL.
4. Compare consecutive snapshots to identify changes.
5. Collect recent CloudTrail events.
6. Analyze write operations and assign heuristic risk levels.
7. Correlate events with infrastructure resources.
8. Generate incident reports.
9. Recommend recovery actions.
10. Compare Terraform state with AWS inventory.

## Database

PostgreSQL stores historical project data, including:

- Infrastructure snapshots
- Infrastructure changes
- CloudTrail events
- Incident reports
- Recovery plans

## Security Design

- Uses an EC2 IAM role for AWS API access.
- Uses read-only AWS permissions for infrastructure discovery.
- Avoids storing AWS access keys in source code or Docker images.
- Uses environment variables for database credentials.
- Excludes sensitive Terraform state and generated data from Git.
- Does not automatically execute recovery actions.

## Docker

The application is packaged using Docker.

Build the image:

```bash
docker build -t infrastructure-time-machine:v1 .
```

Run the default AWS collector:

```bash
docker run --rm infrastructure-time-machine:v1
```

Additional modules can be executed by overriding the container's default command.

## Terraform Integration

Terraform is used to maintain infrastructure configuration and state.

The project reads Terraform state and compares the recorded EC2 instance IDs with the actual AWS snapshot.

This provides an inventory comparison to help identify differences between Terraform state and discovered AWS resources.

## Future Improvements

- CloudTrail pagination and duplicate-event handling.
- More detailed infrastructure change detection.
- Automated scheduled snapshots.
- Improved risk classification.
- Web-based incident dashboard.
- Multi-region AWS inventory support.
- Infrastructure dependency tracking.
- Historical infrastructure reconstruction.

## Project Status

Core AWS collection, change detection, CloudTrail analysis, incident reporting, recovery recommendations, PostgreSQL persistence, Terraform inventory comparison, and Docker execution have been implemented and tested.

## Author

**Lokesh P J**

GitHub: [LOKESHPJ](https://github.com/LOKESHPJ)
| AWS CloudTrail | Activity and event collection |
| Terraform | Infrastructure state comparison |
| PostgreSQL | Historical data storage |
| Docker | Application containerization |
| Linux | Project execution environment |
| Git and GitHub | Version control |

## Core Modules

| Module | Responsibility |
|---|---|
| `aws_collector.py` | Collects EC2 infrastructure snapshots |
| `change_detector.py` | Detects changes between snapshots |
| `cloudtrail_collector.py` | Collects CloudTrail events |
| `event_analyzer.py` | Analyzes write events and assigns heuristic risk levels |
| `incident_correlator.py` | Matches CloudTrail events to EC2 resources |
| `incident_report.py` | Generates structured incident reports |
| `recovery_planner.py` | Recommends recovery actions |
| `terraform_reader.py` | Compares Terraform state with AWS inventory |
| `database.py` | Manages PostgreSQL connections |
| `database_schema.sql` | Defines database tables |

## Project Workflow

1. Collect AWS EC2 infrastructure information.
2. Save timestamped snapshots as JSON files.
3. Store snapshot information in PostgreSQL.
4. Compare consecutive snapshots to identify changes.
5. Collect recent CloudTrail events.
6. Analyze write operations and assign heuristic risk levels.
7. Correlate events with infrastructure resources.
8. Generate incident reports.
9. Recommend recovery actions.
10. Compare Terraform state with AWS inventory.

## Database

PostgreSQL stores historical project data, including:

- Infrastructure snapshots
- Infrastructure changes
- CloudTrail events
- Incident reports
- Recovery plans

## Security Design

- Uses an EC2 IAM role for AWS API access.
- Uses read-only AWS permissions for infrastructure discovery.
- Avoids storing AWS access keys in source code or Docker images.
- Uses environment variables for database credentials.
- Excludes sensitive Terraform state and generated data from Git.
- Does not automatically execute recovery actions.

## Docker

The application is packaged using Docker.

Build the image:

```bash
docker build -t infrastructure-time-machine:v1 .
```

Run the default AWS collector:

```bash
docker run --rm infrastructure-time-machine:v1
```

Additional modules can be executed by overriding the container's default command.

## Terraform Integration

Terraform is used to maintain infrastructure configuration and state.

The project reads Terraform state and compares the recorded EC2 instance IDs with the actual AWS snapshot.

This provides an inventory comparison to help identify differences between Terraform state and discovered AWS resources.

## Future Improvements

- CloudTrail pagination and duplicate-event handling.
- More detailed infrastructure change detection.
- Automated scheduled snapshots.
- Improved risk classification.
- Web-based incident dashboard.
- Multi-region AWS inventory support.
- Infrastructure dependency tracking.
- Historical infrastructure reconstruction.

## Project Status

Core AWS collection, change detection, CloudTrail analysis, incident reporting, recovery recommendations, PostgreSQL persistence, Terraform inventory comparison, and Docker execution have been implemented and tested.

## Author

**Lokesh P J**

GitHub: [LOKESHPJ](https://github.com/LOKESHPJ)
# Infrastructure Change Time Machine

An AWS infrastructure monitoring and change-tracking project built using Python, Boto3, Terraform, Docker, and PostgreSQL.

The project captures AWS infrastructure snapshots, detects infrastructure changes, analyzes CloudTrail activity, correlates events with affected resources, generates incident reports, and recommends recovery actions.

## Project Overview

Infrastructure changes can happen because of manual actions, automation, or configuration updates. Identifying what changed, when it changed, and which resources were affected is important for cloud operations and incident investigation.

Infrastructure Change Time Machine provides a centralized workflow to:

- Capture AWS EC2 infrastructure snapshots.
- Store infrastructure history in PostgreSQL.
- Detect changes between consecutive snapshots.
- Collect and analyze AWS CloudTrail events.
- Identify potentially risky write operations.
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
          |                     |
          v                     v
    Change Detector      Incident Correlator
          |                     |
          +----------+----------+
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
      Terraform             Docker
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
| Linux | Project execution environment |
| Git and GitHub | Version control |

## Core Modules

| Module | Responsibility |
|---|---|
| `aws_collector.py` | Collects EC2 infrastructure snapshots |
| `change_detector.py` | Detects changes between snapshots |
| `cloudtrail_collector.py` | Collects CloudTrail events |
| `event_analyzer.py` | Analyzes write events and assigns heuristic risk levels |
| `incident_correlator.py` | Matches CloudTrail events to EC2 resources |
| `incident_report.py` | Generates structured incident reports |
| `recovery_planner.py` | Recommends recovery actions |
| `terraform_reader.py` | Compares Terraform state with AWS inventory |
| `database.py` | Manages PostgreSQL connections |
| `database_schema.sql` | Defines database tables |

## Project Workflow

1. Collect AWS EC2 infrastructure information.
2. Save timestamped snapshots as JSON files.
3. Store snapshot information in PostgreSQL.
4. Compare consecutive snapshots to identify changes.
5. Collect recent CloudTrail events.
6. Analyze write operations and assign heuristic risk levels.
7. Correlate events with infrastructure resources.
8. Generate incident reports.
9. Recommend recovery actions.
10. Compare Terraform state with AWS inventory.

## Database

PostgreSQL stores historical project data, including:

- Infrastructure snapshots
- Infrastructure changes
- CloudTrail events
- Incident reports
- Recovery plans

## Security Design

- Uses an EC2 IAM role for AWS API access.
- Uses read-only AWS permissions for infrastructure discovery.
- Avoids storing AWS access keys in source code or Docker images.
- Uses environment variables for database credentials.
- Excludes sensitive Terraform state and generated data from Git.
- Does not automatically execute recovery actions.

## Docker

The application is packaged using Docker.

Build the image:

```bash
docker build -t infrastructure-time-machine:v1 .
```

Run the default AWS collector:

```bash
docker run --rm infrastructure-time-machine:v1
```

Additional modules can be executed by overriding the container's default command.

## Terraform Integration

Terraform is used to maintain infrastructure configuration and state.

The project reads Terraform state and compares the recorded EC2 instance IDs with the actual AWS snapshot.

This provides an inventory comparison to help identify differences between Terraform state and discovered AWS resources.

## Future Improvements

- CloudTrail pagination and duplicate-event handling.
- More detailed infrastructure change detection.
- Automated scheduled snapshots.
- Improved risk classification.
- Web-based incident dashboard.
- Multi-region AWS inventory support.
- Infrastructure dependency tracking.
- Historical infrastructure reconstruction.

## Project Status

Core AWS collection, change detection, CloudTrail analysis, incident reporting, recovery recommendations, PostgreSQL persistence, Terraform inventory comparison, and Docker execution have been implemented and tested.

## Author

**Lokesh P J**

GitHub: [LOKESHPJ](https://github.com/LOKESHPJ)# Infrastructure Change Time Machine

An AWS infrastructure monitoring and change-tracking project built using Python, Boto3, Terraform, Docker, and PostgreSQL.

The project captures AWS infrastructure snapshots, detects infrastructure changes, analyzes CloudTrail activity, correlates events with affected resources, generates incident reports, and recommends recovery actions.

## Project Overview

Infrastructure changes can happen because of manual actions, automation, or configuration updates. Identifying what changed, when it changed, and which resources were affected is important for cloud operations and incident investigation.

Infrastructure Change Time Machine provides a centralized workflow to:

- Capture AWS EC2 infrastructure snapshots.
- Store infrastructure history in PostgreSQL.
- Detect changes between consecutive snapshots.
- Collect and analyze AWS CloudTrail events.
- Identify potentially risky write operations.
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
          |                     |
          v                     v
    Change Detector      Incident Correlator
          |                     |
          +----------+----------+
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
      Terraform             Docker
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
| Linux | Project execution environment |
| Git and GitHub | Version control |

## Core Modules

| Module | Responsibility |
|---|---|
| `aws_collector.py` | Collects EC2 infrastructure snapshots |
| `change_detector.py` | Detects changes between snapshots |
| `cloudtrail_collector.py` | Collects CloudTrail events |
| `event_analyzer.py` | Analyzes write events and assigns heuristic risk levels |
| `incident_correlator.py` | Matches CloudTrail events to EC2 resources |
| `incident_report.py` | Generates structured incident reports |
| `recovery_planner.py` | Recommends recovery actions |
| `terraform_reader.py` | Compares Terraform state with AWS inventory |
| `database.py` | Manages PostgreSQL connections |
| `database_schema.sql` | Defines database tables |

## Project Workflow

1. Collect AWS EC2 infrastructure information.
2. Save timestamped snapshots as JSON files.
3. Store snapshot information in PostgreSQL.
4. Compare consecutive snapshots to identify changes.
5. Collect recent CloudTrail events.
6. Analyze write operations and assign heuristic risk levels.
7. Correlate events with infrastructure resources.
8. Generate incident reports.
9. Recommend recovery actions.
10. Compare Terraform state with AWS inventory.

## Database

PostgreSQL stores historical project data, including:

- Infrastructure snapshots
- Infrastructure changes
- CloudTrail events
- Incident reports
- Recovery plans

## Security Design

- Uses an EC2 IAM role for AWS API access.
- Uses read-only AWS permissions for infrastructure discovery.
- Avoids storing AWS access keys in source code or Docker images.
- Uses environment variables for database credentials.
- Excludes sensitive Terraform state and generated data from Git.
- Does not automatically execute recovery actions.

## Docker

The application is packaged using Docker.

Build the image:

```bash
docker build -t infrastructure-time-machine:v1 .
```

Run the default AWS collector:

```bash
docker run --rm infrastructure-time-machine:v1
```

Additional modules can be executed by overriding the container's default command.

## Terraform Integration

Terraform is used to maintain infrastructure configuration and state.

The project reads Terraform state and compares the recorded EC2 instance IDs with the actual AWS snapshot.

This provides an inventory comparison to help identify differences between Terraform state and discovered AWS resources.

## Future Improvements

- CloudTrail pagination and duplicate-event handling.
- More detailed infrastructure change detection.
- Automated scheduled snapshots.
- Improved risk classification.
- Web-based incident dashboard.
- Multi-region AWS inventory support.
- Infrastructure dependency tracking.
- Historical infrastructure reconstruction.

## Project Status

Core AWS collection, change detection, CloudTrail analysis, incident reporting, recovery recommendations, PostgreSQL persistence, Terraform inventory comparison, and Docker execution have been implemented and tested.

## Author

**Lokesh P J**

GitHub: [LOKESHPJ](https://github.com/LOKESHPJ)

