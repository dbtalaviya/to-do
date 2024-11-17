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
    # Log the incoming event for debugging
    logger.info(f"Event: {event}")

    # Retrieve the item_id from the path parameters
    path_param = event.get("pathParameters", {})
    item_id = path_param.get("item_id")

    if not item_id:
        logger.error("Item ID not found in path parameters")
        return {"statusCode": 400, "body": json.dumps({"error": "Item ID is required"})}

    logger.info(f"Requesting to delete item: {item_id} from todo list")

    # Initialize AWS clients for SSM and SQS
    ssm_client = boto3.client("ssm")
    sqs_client = boto3.client("sqs")

    # Fetch the SQS delete queue URL from SSM parameter store
    try:
        delete_queue_url_param = ssm_client.get_parameter(
            Name="/todolist/deletequeue/url", WithDecryption=False
        )
        delete_queue_url = delete_queue_url_param["Parameter"]["Value"]
        logger.debug(f"Delete Queue URL fetched: {delete_queue_url}")
    except ssm_client.exceptions.ParameterNotFound:
        logger.error("SQS queue URL not found in SSM Parameter Store")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to fetch delete queue URL"}),
        }

    # Send the delete request to the SQS queue
    try:
        logger.debug(
            f"Sending delete request for item {item_id} to SQS queue: {delete_queue_url}"
        )
        response = sqs_client.send_message(
            QueueUrl=delete_queue_url, DelaySeconds=10, MessageBody=json.dumps(item_id)
        )
        logger.info(
            f"Sent delete request for item {item_id} to SQS. Message ID: {response.get('MessageId')}"
        )
    except Exception as e:
        logger.error(f"Failed to send message to SQS: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to send delete request"}),
        }

    # Return a success response
    return {
        "statusCode": 204,
        "body": json.dumps({"message": "Delete requested successfully"}),
    }
