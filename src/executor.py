import json
import logging
import os
import pickle
import sys

import boto3
import uuid

from datetime import datetime

from lambda_logic.main import main

# Set the level of logging
DEBUG = os.environ.get('DEBUG', False)
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

dynamodb_client = boto3.client("dynamodb")
table = os.environ.get("DYNAMO_TABLE_NAME")


def write_to_database(**kwargs):
    # Unpack arguments
    execution_id = kwargs.get('execution_id')
    start_execution = kwargs.get('start_execution')
    event = kwargs.get('event')
    result = kwargs.get('result')

    # Write event and result details to the database
    item = {
        'executionId': {'S': execution_id},
        'StartExecution': {'S': start_execution},
        'Event': {'S': event},
        'Result': {'S': result},
    }
    try:
        dynamodb_client.put_item(
            TableName=table,
            Item=item
        )
        logging.info(f"Successfully wrote item to the database")
    except Exception as e:
        logging.error(f"## {e}")
        raise


def handler(event, context):
    # Get current date
    now = datetime.now().isoformat()
    logging.info(f"## Starting Executor function at : {now}")  
    print(f"## Starting Executor function at : {now}")

    # Print the event 
    logging.debug(f"## event: {event}")

    # Parse the JSON body
    event_body = json.loads(event['body'])

    # Print the parsed body for troubleshooting
    logging.debug(f"## event_body: {event_body}")

    model = event_body['model']
    new_money = event_body['new_money']
    values = event_body['values']

    # Execute the main logic
    result = main(model=model, new_money=new_money, values=values)

    # Convert UUID to string
    execution_id = str(uuid.uuid4())

    # Convert event and result to strings
    event_str = json.dumps(event)
    result_str = result.to_json(orient='records')

    write_to_database(
        execution_id=execution_id,
        start_execution=now,
        event=event_str,
        result=result_str,
        )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": result_str
    }
