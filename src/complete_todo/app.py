import boto3
import logging
from datetime import datetime
from aws_lambda_powertools import Tracer, Logger

# Initialize tracer and logger
tracer = Tracer()
logger = Logger()

# Set logger level
logger.setLevel(logging.INFO)


# Define Lambda handler with tracer and logger injected
@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.info(f"Event: {event}")

    # Initialize DynamoDB client
    client = boto3.resource("dynamodb")
    table = client.Table("Todos")

    # Extract item_id from path parameters
    item_id = event.get("pathParameters", {}).get("item_id")

    # Perform the update operation in DynamoDB
    response = table.update_item(
        Key={"item_id": item_id},
        UpdateExpression="SET is_done = :d, updated_date = :p",
        ExpressionAttributeValues={
            ":d": True,
            ":p": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        },
        ReturnValues="ALL_NEW",
    )

    # Log the DynamoDB response
    logger.info(f"Updated DynamoDB Table: {response}")

    # Return a successful response (204 No Content)
    return {"statusCode": 204}
