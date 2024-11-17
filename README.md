---

# **Lambda Function for Updating Todo Items in DynamoDB**

This AWS Lambda function is designed to update a Todo item in a DynamoDB table. The function takes an `item_id`, `title`, and `content` as input and updates the corresponding item in the `Todos` table. The updated fields are `title`, `content`, and `updated_date`.

## **Features**
- **Update Todo Item**: Allows you to update the title and content of a specific Todo item using its `item_id`.
- **Timestamping**: Automatically updates the `updated_date` with the current timestamp whenever an item is updated.
- **Error Handling**: Provides error handling for missing parameters and failures in DynamoDB operations.

## **Table of Contents**
- [Setup](#setup)
- [Lambda Function Details](#lambda-function-details)
- [Usage](#usage)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Logs](#logs)

---

## **Setup**

### Prerequisites
1. **AWS Lambda**: This function needs to be deployed in an AWS Lambda environment.
2. **DynamoDB Table**: A DynamoDB table named `Todos` should exist. The table should have a partition key `item_id` of type string.
3. **AWS IAM Role**: The Lambda function must have a role with permission to access DynamoDB.

### Lambda Permissions
Ensure that the Lambda function has the following IAM policy attached:
- `dynamodb:UpdateItem` for accessing the `Todos` table.

---

## **Lambda Function Details**

### Function Overview
This Lambda function updates a Todo item in a DynamoDB table by using the provided `item_id` and the new `title` and `content`. The function also updates the `updated_date` to the current timestamp whenever the Todo item is updated.

### Code Explanation

```python
import boto3
import json
import logging
from datetime import datetime
from aws_lambda_powertools import Tracer, Logger

tracer = Tracer()
logger = Logger()

logger.setLevel(logging.INFO)

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.info(f"Event: {event}")

    client = boto3.resource('dynamodb')
    table = client.Table('Todos')
    
    body = json.loads(event.get('body', '{}'))
    
    item_id = body.get('item_id')
    title = body.get('title')
    content = body.get('content')

    if not item_id or not title or not content:
        logger.error("Missing required fields (item_id, title, content) in request body.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required fields: item_id, title, content"})
        }

    try:
        response = table.update_item(
            Key={'item_id': item_id},
            UpdateExpression="set title=:r, content=:p, updated_date=:a",
            ExpressionAttributeValues={
                ':r': title,
                ':p': content,
                ':a': datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            },
            ReturnValues="UPDATED_NEW"
        )

        logger.info(f"Updated DynamoDB Table for item_id: {item_id}. Response: {response}")
        
        return {
            "statusCode": 204,
            "body": json.dumps({})
        }

    except Exception as e:
        logger.error(f"Failed to update item in DynamoDB: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to update item"})
        }
```

---

## **Usage**

To use this Lambda function, you need to invoke it through an API Gateway or other event source that passes an `event` containing the body with the following JSON structure:

### Input Body
```json
{
    "item_id": "12345",
    "title": "Updated Todo Title",
    "content": "Updated Todo Content"
}
```

- **item_id**: The unique identifier of the Todo item to be updated.
- **title**: The new title of the Todo item.
- **content**: The new content of the Todo item.

### Example API Request

You can trigger the Lambda function using an API Gateway endpoint, sending a `POST` request with the input body.

---

## **Response Format**

### Success Response

If the update is successful, the function will return a status code of `204 No Content` with no body.

```json
{
    "statusCode": 204,
    "body": "{}"
}
```

### Error Response

In case of missing fields (`item_id`, `title`, `content`), the function will return a `400 Bad Request` with a message indicating the missing fields.

```json
{
    "statusCode": 400,
    "body": "{\"error\": \"Missing required fields: item_id, title, content\"}"
}
```

In case of an internal failure (e.g., DynamoDB issues), the function will return a `500 Internal Server Error`.

```json
{
    "statusCode": 500,
    "body": "{\"error\": \"Failed to update item\"}"
}
```

---

## **Error Handling**

The Lambda function includes the following error handling mechanisms:
- **Missing Fields**: If `item_id`, `title`, or `content` are missing from the request body, a `400 Bad Request` is returned.
- **DynamoDB Update Failure**: If an error occurs during the DynamoDB update operation, a `500 Internal Server Error` is returned.

---

## **Logs**

The function uses AWS Lambda Powertools for logging and tracing. Logs are generated for the following actions:
- Incoming request (`Event`)
- Parameters (e.g., `item_id`, `title`, `content`)
- DynamoDB update response
- Errors (e.g., missing fields, DynamoDB issues)

These logs can be viewed in Amazon CloudWatch for monitoring and debugging purposes.

---

### Feel free to adapt this README to your project’s specifics.