"""
Helper script to provision AWS SNS Topic and Email Subscription for MLOps Alerts.
"""

import argparse
import boto3


def setup_sns(topic_name: str = "mlops-pipeline-alerts", email: str = None, region: str = "us-east-1"):
    print(f"[AWS SNS] Initializing SNS client for region: {region}...")
    sns = boto3.client("sns", region_name=region)

    print(f"[AWS SNS] Creating/fetching topic: {topic_name}...")
    topic_res = sns.create_topic(Name=topic_name)
    topic_arn = topic_res["TopicArn"]
    print(f"[AWS SNS] Topic ARN: {topic_arn}")

    if email:
        print(f"[AWS SNS] Subscribing email: {email} to topic...")
        sub_res = sns.subscribe(
            TopicArn=topic_arn,
            Protocol="email",
            Endpoint=email,
        )
        print(f"[AWS SNS] Subscription initiated. Status ARN: {sub_res['SubscriptionArn']}")
        print(f"[ACTION REQUIRED] Please check your inbox ({email}) and click 'Confirm subscription'!")

    print("\n--- Summary ---")
    print(f"SNS_TOPIC_ARN={topic_arn}")
    print("Add this ARN to your Lambda environment variables as SNS_TOPIC_ARN.")


def main():
    parser = argparse.ArgumentParser(description="Setup AWS SNS Topic and Email Subscription")
    parser.add_argument("--topic", type=str, default="mlops-pipeline-alerts", help="SNS Topic name")
    parser.add_argument("--email", type=str, required=False, help="Email address to receive MLOps alerts")
    parser.add_argument("--region", type=str, default="us-east-1", help="AWS Region")

    args = parser.parse_args()
    setup_sns(topic_name=args.topic, email=args.email, region=args.region)


if __name__ == "__main__":
    main()
