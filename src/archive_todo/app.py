import boto3
from botocore.exceptions import ClientError
import json
import logging
from datetime import datetime
from aws_lambda_powertools import Tracer, Logger

tracer = Tracer()
logger = Logger()

logger.setLevel(logging.DEBUG)


@tracer.capture_method
def create_csv_archive(item_id, response):
    csv_path = f"/tmp/{item_id}.csv"
    with open(csv_path, "w") as archive_file:
        archive_file.write(
            "Item Id,Title,Content,Created,Updated,Archived,Deleted,Complete,Archived Date\n"
        )
        item = response["Item"]
        archive_file.write(
            f"{item_id},{item['title']},{item['content']},{item['created_date']},{item['updated_date']},"
            f"True,{item['is_deleted']},{item['is_done']},{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
        )
    return csv_path


@tracer.capture_method
def update_item_as_archived(item_id, table):
    return table.update_item(
        Key={"item_id": item_id},
        UpdateExpression="SET is_archived = :archived, updated_date = :updated",
        ExpressionAttributeValues={
            ":archived": True,
            ":updated": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        },
        ReturnValues="UPDATED_NEW",
    )


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.info(f"Received event: {event}")

    path_param = event.get("pathParameters")
    item_id = path_param.get("item_id")
    logger.info(f"Archiving item with ID: {item_id}")

    s3 = boto3.client("s3")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("Todos")

    try:
        response = table.get_item(Key={"item_id": item_id})
        logger.info(f"Item retrieved from DynamoDB: {response}")

        csv_path = create_csv_archive(item_id, response)

        try:
            s3.upload_file(csv_path, "todo-list-archive-bucket-cb", f"{item_id}.csv")
            logger.info(f"File uploaded to S3: {item_id}.csv")
        except ClientError as upload_error:
            logger.error(f"S3 upload error: {upload_error}")
            return {
                "statusCode": 502,
                "body": json.dumps(
                    {"message": f"Error uploading to S3: {upload_error}"}
                ),
            }

        try:
            db_response = update_item_as_archived(item_id, table)
            logger.debug(f"DynamoDB update response: {db_response}")
        except ClientError as update_error:
            logger.error(f"DynamoDB update error: {update_error}")
            return {
                "statusCode": 502,
                "body": json.dumps(
                    {"message": f"Error updating DynamoDB: {update_error}"}
                ),
            }

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Item {item_id} archived successfully"}),
        }

    except ClientError as e:
        logger.error(f"Error fetching item: {e}")
        return {
            "statusCode": 502,
            "body": json.dumps({"message": f"Error fetching item: {e}"}),
        }
