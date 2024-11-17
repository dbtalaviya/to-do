import boto3
import json
import logging
from aws_lambda_powertools import Tracer, Logger

# Initialize Tracer and Logger
tracer = Tracer()
logger = Logger()

# Set logger level
logger.setLevel(logging.INFO)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    # Log incoming event for debugging
    logger.info(f"Event: {event}")

    # Initialize S3 client and specify the bucket
    s3_client = boto3.resource("s3")
    archive_bucket = s3_client.Bucket("todo-list-archive-bucket-cb")

    archives = []

    # Fetch and log each archive item in the bucket
    for archive_item in archive_bucket.objects.all():
        archives.append(archive_item.key)
        logger.info(f"Archive Item: {archive_item.key}")

    logger.info(f"Total Archives Found: {len(archives)}")

    # Return the list of archives as a response
    return {"statusCode": 200, "body": json.dumps(archives)}
