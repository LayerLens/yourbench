# YourbenchProcessor Docker Container

This Docker container automates the process of:
1. Downloading data from AWS S3
2. Processing with yourbench
3. Uploading results back to AWS S3

## Required Environment Variables

The container requires the following environment variables:

- `INPUT_S3_BUCKET`: S3 bucket name for input data
- `INPUT_S3_KEY`: S3 object key for input data (ZIP file)
- `OUTPUT_S3_BUCKET`: S3 bucket name for output results
- `OUTPUT_S3_KEY`: S3 object key for output results
- `OPENROUTER_API_KEY`: API key for OpenRouter
- `AWS_ACCESS_KEY_ID`: AWS access key with S3 permissions
- `AWS_SECRET_ACCESS_KEY`: AWS secret key with S3 permissions
- `AWS_DEFAULT_REGION`: AWS region (default: us-east-1)

## Building the Docker Image

```bash
docker build -t yourbench-processor .
```

## Running the Container

```bash
docker run -e INPUT_S3_BUCKET=your-input-bucket \
           -e INPUT_S3_KEY=input/data.zip \
           -e OUTPUT_S3_BUCKET=your-output-bucket \
           -e OUTPUT_S3_KEY=output/results.zip \
           -e OPENROUTER_API_KEY=your-openrouter-key \
           -e AWS_ACCESS_KEY_ID=your-aws-key-id \
           -e AWS_SECRET_ACCESS_KEY=your-aws-secret \
           -e AWS_DEFAULT_REGION=us-east-1 \
           yourbench-processor
```

## Process Flow

1. Downloads the specified zip file from S3
2. Extracts contents to `task/data/raw` directory
3. Creates a `config.yaml` file in `task/dataset` directory
4. Runs yourbench with the created config
5. Zips the `task/dataset` directory
6. Uploads the zipped results back to S3

## Local Testing

For local testing without Docker:

```bash
# Set environment variables
export INPUT_S3_BUCKET=your-input-bucket
export INPUT_S3_KEY=input/data.zip
export OUTPUT_S3_BUCKET=your-output-bucket
export OUTPUT_S3_KEY=output/results.zip
export OPENROUTER_API_KEY=your-openrouter-key
export AWS_ACCESS_KEY_ID=your-aws-key-id
export AWS_SECRET_ACCESS_KEY=your-aws-secret
export AWS_DEFAULT_REGION=us-east-1

# Run the script
python run_yourbench.py
```
