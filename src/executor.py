import json
import logging
import os
import pickle
import sys
import pprint

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

# Configure a pretty printer for more readable logging
pp = pprint.PrettyPrinter(indent=4)

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

    # Log the entire event in a readable format
    logging.info("Received Event:")
    logging.info(pp.pformat(event))

    try:
        # Parse the JSON body
        event_body = json.loads(event['body'])

        # Log the parsed body with detailed, readable formatting
        logging.info("Parsed Event Body:")
        logging.info(pp.pformat(event_body))

        # Detailed logging of each parameter
        logging.info("Model:")
        logging.info(pp.pformat(event_body.get('model')))
        
        logging.info("New Money:")
        logging.info(pp.pformat(event_body.get('new_money')))
        
        logging.info("Values:")
        logging.info(pp.pformat(event_body.get('values')))

        # Extract parameters with more robust error handling
        model = event_body.get('model')
        new_money = event_body.get('new_money')
        values = event_body.get('values')

        # Validate parameters
        if model is None:
            raise ValueError("Missing 'model' in the request")
        if new_money is None:
            raise ValueError("Missing 'new_money' in the request")
        if values is None:
            raise ValueError("Missing 'values' in the request")

        # Validate model weights
        if not isinstance(model, dict):
            raise TypeError("Model must be a dictionary")
        
        total_weight = sum(model.values())
        logging.info(f"Total Weight Calculation: {total_weight}")
        
        if abs(total_weight - 1.0) > 1e-9:
            logging.error(f"Model weights do not sum to 1. Total weight: {total_weight}")
            raise ValueError(f"Model weights must sum to 1. Current total: {total_weight}")

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

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        logging.error(f"Exception type: {type(e)}")
        
        # Include full traceback for debugging
        import traceback
        logging.error(traceback.format_exc())

        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": str(e),
                "message": "Failed to process the request"
            })
        }