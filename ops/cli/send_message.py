#!/usr/bin/env python3
import argparse
import json
import sys
import uuid
from typing import Optional

import boto3
from botocore.config import Config


def get_sqs_client():
    """Get SQS client with LocalStack configuration."""
    return boto3.client(
        "sqs",
        endpoint_url="http://localhost:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=Config(
            retries={"max_attempts": 3},
            connect_timeout=5,
            read_timeout=5,
        ),
    )


def send_message(queue_name: str, message: str) -> Optional[str]:
    """Send a message to the specified SQS queue."""
    try:
        # Get queue URL
        sqs = get_sqs_client()
        queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]

        # Send message
        message_id = str(uuid.uuid4())
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message,
            MessageGroupId=message_id,
            MessageDeduplicationId=message_id,
        )
        print(f"Message sent successfully! MessageId: {response['MessageId']}")
        return response["MessageId"]

    except Exception as e:
        print(f"Error sending message: {str(e)}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Send a message to LocalStack SQS queue")
    parser.add_argument("queue_name", help="Name of the SQS queue")
    parser.add_argument("message", help="JSON message to send (must be a valid JSON string)")

    args = parser.parse_args()

    # Validate JSON
    try:
        json.loads(args.message)
    except json.JSONDecodeError:
        print("Error: Message must be a valid JSON string", file=sys.stderr)
        sys.exit(1)

    send_message(args.queue_name, args.message)


if __name__ == "__main__":
    main()
