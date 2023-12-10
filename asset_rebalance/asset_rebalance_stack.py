from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_lambda_python_alpha as alambda_,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
)


class AssetRebalanceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        TABLE_NAME = "asset-rebalance"

        # Create lambda function (with limited external dependencies)
        # run with >sam local invoke -t <*template.json>

        # my_lambda = lambda_.Function(
        #     self,
        #     "myLambda",
        #     handler='executor.handler',
        #     runtime=lambda_.Runtime.PYTHON_3_10,
        #     code=lambda_.Code.from_asset("src")
        # )

        my_lambda = alambda_.PythonFunction(
            self,
            "myLambda",
            handler='handler',
            entry="./src/",
            runtime=lambda_.Runtime.PYTHON_3_10,
            index="executor.py",
            timeout=Duration.seconds(20),
            memory_size=128,
            environment={
                "TZ": "America/Los_Angeles"
            },
        )

        # Create API Gateway
        apigw.LambdaRestApi(
            self,
            "asset_rebalance",
            handler=my_lambda,
            )

        # Create DynamoDb Table
        dynamo_db_table = dynamodb.Table(
            self,
            TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="executionId", type=dynamodb.AttributeType.STRING
            ),
        )

        # grant permission to lambda to write to the table
        dynamo_db_table.grant_write_data(my_lambda)

        # add environment variable to the lambda function
        my_lambda.add_environment("DYNAMO_TABLE_NAME", dynamo_db_table.table_name)
