import json
import boto3
import logging
from aws_lambda_powertools import Tracer, Logger

# Initialize Logger and Tracer
logger = Logger()
tracer = Tracer()

# Set logger level
logger.setLevel(logging.INFO)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    # Log incoming event
    logger.info(f"Event: {event}")

    # Retrieve the path parameter (item_id)
    path_param = event.get("pathParameters", {})
    item_id = path_param.get("item_id")
    if not item_id:
        logger.error("item_id is missing in pathParameters")
        return {"statusCode": 400, "body": json.dumps({"error": "item_id is required"})}

    logger.info(f"Fetching todo item with item_id: {item_id}")

    # Initialize DynamoDB client and table
    client = boto3.resource("dynamodb")
    table = client.Table("Todos")

    # Fetch the item from DynamoDB
    db_response = table.get_item(Key={"item_id": item_id})

    if "Item" not in db_response:
        logger.error(f"Item with item_id {item_id} not found")
        return {"statusCode": 404, "body": json.dumps({"error": "Item not found"})}

    logger.info(f"Fetched item: {db_response['Item']} from DynamoDB table")

    # Return the item in the response body
    return {"statusCode": 200, "body": json.dumps(db_response["Item"])}
