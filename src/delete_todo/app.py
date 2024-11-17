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
    # Initialize AWS Clients
    ssm_client = boto3.client("ssm")
    sqs_client = boto3.client("sqs")
    dynamodb_client = boto3.resource("dynamodb")
    dynamodb_table = dynamodb_client.Table("Todos")

    # Fetch delete queue URL from SSM Parameter Store
    delete_queue_url_param = ssm_client.get_parameter(
        Name="/todolist/deletequeue/url", WithDecryption=False
    )
    delete_queue_url = delete_queue_url_param["Parameter"]["Value"]
    logger.debug(f"Delete Queue URL: {delete_queue_url}")

    # Receive messages from the SQS queue
    response = sqs_client.receive_message(QueueUrl=delete_queue_url)
    messages = response.get("Messages", [])
    logger.debug(f"Fetched {len(messages)} messages from SQS Queue")

    # Process each message
    for message in messages:
        logger.info(f"Processing message: {message['MessageId']}")
        receipt_handle = message["ReceiptHandle"]

        item_id = message["Body"]
        logger.info(f"Deleting item: {item_id} from todo list")

        # Update DynamoDB to mark the item as deleted
        db_response = dynamodb_table.update_item(
            Key={"item_id": item_id},
            UpdateExpression="SET is_deleted = :d, updated_date = :u",
            ExpressionAttributeValues={
                ":d": True,
                ":u": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            },
            ReturnValues="UPDATED_NEW",
        )
        logger.debug(f"DynamoDB response: {db_response}")

        # Delete the message from the SQS queue once processed
        sqs_client.delete_message(
            QueueUrl=delete_queue_url, ReceiptHandle=receipt_handle
        )

    # Log the last message processed
    if messages:
        logger.info(f"Received and deleted message: {messages[-1]['MessageId']}")
    else:
        logger.info("No messages to process.")
