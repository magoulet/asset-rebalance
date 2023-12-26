## Asset Rebalancer

This Python project includes an AWS CDK stack that provisions the necessary resources to host a Lambda function for the rebalancing of assets. The solution also utilizes Amazon DynamoDB for data persistence. The Lambda function implemented in Python uses Pandas to manage and calculate asset rebalancing based on given portfolio models.

### Prerequisites

Before you deploy the stack, make sure you have the following installed:

- AWS Command Line Interface (CLI)
- AWS CDK Toolkit
- Python 3.7 or later
- Node.js (for AWS CDK)

### Installation

1. Clone the repository to your local machine by running:

   ```bash
   git clone https://github.com/your-repo/asset-rebalancer.git
   cd asset-rebalancer
   ```

2. Install the required Python packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Bootstrap your AWS environment to use the AWS CDK:

   ```bash
   cdk bootstrap aws://ACCOUNT_ID/REGION
   ```

   Replace `ACCOUNT_ID` with your AWS account ID and `REGION` with your preferred region.

### Deployment

Deploy the AWS CDK stack with the following command:

```bash
cdk deploy
```

This command deploys the `AssetRebalanceStack` to your default AWS account/region.

### Usage

After deployment, the Lambda function can be triggered via the API Gateway endpoint that is created as part of the CDK stack. The endpoint takes in a JSON payload containing the portfolio model, new money to allocate, and current values of assets.

A sample payload would look like this:

```json
{
    "model": {
        "Asset1": 0.20,
        "Asset2": 0.15,
        "Asset3": 0.15,
        "Asset4": 0.5
    },
    "new_money": 2000,
    "values": {
        "Asset1": 1000,
        "Asset2": 1000,
        "Asset3": 1000,
        "Asset4": 1000
    }
}
```

Use your preferred tool (e.g., `curl`, Postman) to send a `POST` request to the API Gateway endpoint with the payload.

### Architecture

The CDK stack does the following:

- Creates a Python Lambda function for asset rebalancing logic.
- Sets up an API Gateway REST API to expose the Lambda function as an HTTP endpoint.
- Provisions a DynamoDB table for storing execution records.
- Grants the Lambda function permission to write to the DynamoDB table and access environment variables.

The Lambda function accepts a JSON input containing an asset model with desired weights, additional funds to include (new money), and current asset values. It calculates the necessary rebalancing actions and outputs them.

### Local Testing

For local testing, you can use AWS SAM with the lambda code, but be aware that for full AWS integrations, you should use your AWS Cloud environment.

### Contributing

Contributions to this project are welcome. Please follow these steps:

1. Fork the repo and create your branch from `main`.
2. Make your changes and test.
3. Issue a pull request with a comprehensive description of changes.

### Support

Raise an issue in the repository for any questions or concerns.

### License

This project is MIT licensed. See the [LICENSE](LICENSE) file for details.