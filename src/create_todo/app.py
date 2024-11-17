import json
import boto3
import uuid
import logging
from datetime import datetime
from aws_lambda_powertools import Tracer, Logger

# Initialize Tracer and Logger
tracer = Tracer()
logger = Logger()

# Set logger level
logger.setLevel(logging.INFO)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    # Log incoming event and context for debugging
    logger.debug(f"Event: {event}")
    logger.debug(f"Context: {context}")

    # Log the action being performed
    logger.info(f"Inserting todo into database: {event}")

    # Parse the request body
    body = json.loads(event.get("body", "{}"))

    # Initialize DynamoDB client and table
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("Todos")

    # Generate a unique item_id for the new todo
    item_id = str(uuid.uuid1())

    # Insert the new todo item into DynamoDB
    table.put_item(
        Item={
            "item_id": item_id,
            "title": body.get("title"),
            "content": body.get("content"),
            "created_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "updated_date": None,
            "is_archived": False,
            "is_deleted": False,
            "is_done": False,
        }
    )

    # Log successful insertion
    logger.info(f"Inserted todo with item_id: {item_id} into database")

    # Return a successful response
    return {
        "statusCode": 201,
        "body": json.dumps(
            {"message": "Todo created successfully", "item_id": item_id}
        ),
    }
