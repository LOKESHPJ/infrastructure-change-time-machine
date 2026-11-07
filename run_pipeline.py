import subprocess
import sys
from datetime import datetime

PIPELINE = [
    ("AWS Infrastructure Collection", "aws_collector.py"),
    ("CloudTrail Collection", "cloudtrail_collector.py"),
    ("Infrastructure Change Detection", "change_detector.py"),
    ("CloudTrail Event Analysis", "event_analyzer.py"),
    ("Incident Correlation", "incident_correlator.py"),
    ("Incident Report Generation", "incident_report.py"),
    ("Recovery Plan Generation", "recovery_planner.py"),
    ("Terraform vs AWS Comparison", "terraform_reader.py"),
]


def run_pipeline():
    start_time = datetime.now()

    print("\nINFRASTRUCTURE TIME MACHINE")
    print("===========================")
    print("Pipeline started:", start_time)

    for index, (stage, script) in enumerate(PIPELINE, start=1):
        print(f"\n[{index}/{len(PIPELINE)}] {stage}")
        print("-" * 50)

        result = subprocess.run(
            [sys.executable, script],
            check=False
        )

        if result.returncode != 0:
            print(f"\n[FAILED] {stage}")
            print("Pipeline stopped.")
            sys.exit(result.returncode)

        print(f"[SUCCESS] {stage}")

    end_time = datetime.now()

    print("\nPIPELINE COMPLETED SUCCESSFULLY")
    print("===============================")
    print("Started:", start_time)
    print("Finished:", end_time)
    print("Duration:", end_time - start_time)


if __name__ == "__main__":
    run_pipeline()
