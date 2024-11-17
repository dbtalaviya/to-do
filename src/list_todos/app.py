import json
import boto3
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
    # Log the incoming event
    logger.info(f"Event: {event}")
    logger.info("Fetching all todos from DynamoDB")

    # Initialize DynamoDB client and table
    dynamodb_client = boto3.resource("dynamodb")
    table = dynamodb_client.Table("Todos")

    # Scan the table (consider performance concerns for large tables)
    results = table.scan()

    # Log the results (logging too much data can be inefficient)
    logger.debug(f"Scan Results: {results}")

    # Return the results as a JSON response
    return {"statusCode": 200, "body": json.dumps(results)}
