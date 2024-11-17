import boto3
import json
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
    # Log incoming event for debugging
    logger.info(f"Event: {event}")

    # Initialize DynamoDB client and table
    client = boto3.resource("dynamodb")
    table = client.Table("Todos")

    # Parse the body from the incoming event
    body = json.loads(event.get("body", "{}"))

    # Extract fields from the body
    item_id = body.get("item_id")
    title = body.get("title")
    content = body.get("content")

    if not item_id or not title or not content:
        logger.error(
            "Missing required fields (item_id, title, content) in request body."
        )
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"error": "Missing required fields: item_id, title, content"}
            ),
        }

    try:
        # Perform the update on DynamoDB
        response = table.update_item(
            Key={"item_id": item_id},
            UpdateExpression="set title=:r, content=:p, updated_date=:a",
            ExpressionAttributeValues={
                ":r": title,
                ":p": content,
                ":a": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            },
            ReturnValues="UPDATED_NEW",
        )

        logger.info(
            f"Updated DynamoDB Table for item_id: {item_id}. Response: {response}"
        )

        return {"statusCode": 204, "body": json.dumps({})}

    except Exception as e:
        logger.error(f"Failed to update item in DynamoDB: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to update item"}),
        }
