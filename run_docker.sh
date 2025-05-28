#!/bin/bash

# Script to build and run the yourbench Docker container
set -e

# Load environment variables from .env if present
if [ -f .env ]; then
  set -a
  . .env
  set +a
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t yourbench-processor .

# Check if environment variables are set
if [ -z "$INPUT_S3_BUCKET" ] || [ -z "$INPUT_S3_KEY" ] || [ -z "$OUTPUT_S3_BUCKET" ] || [ -z "$OUTPUT_S3_KEY" ] || [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Error: Required environment variables are not set."
    echo "Please set these variables before running:"
    echo "  - BENCHMARK_NAME: benchmark name"
    echo "  - BENCHMARK_SYSTEM_PROMPT: benchmark system prompt"
    echo "  - INPUT_S3_BUCKET: S3 bucket containing input data"
    echo "  - INPUT_S3_KEY: S3 key for input data zip file"
    echo "  - OUTPUT_S3_BUCKET: S3 bucket for output data"
    echo "  - OUTPUT_S3_KEY: S3 key for output data"
    echo "  - OPENROUTER_API_KEY: API key for OpenRouter"
    echo ""
    echo "Example:"
    echo "  export BENCHMARK_NAME=benchmark-name"
    echo "  export BENCHMARK_SYSTEM_PROMPT=benchmark-system-prompt"
    echo "  export INPUT_S3_BUCKET=my-input-bucket"
    echo "  export INPUT_S3_KEY=input/data.zip"
    echo "  export OUTPUT_S3_BUCKET=my-output-bucket"
    echo "  export OUTPUT_S3_KEY=output/results.zip"
    echo "  export OPENROUTER_API_KEY=your-api-key"
    exit 1
fi

# Run the Docker container
echo "Running yourbench processor Docker container..."
docker run --rm \
    -e BENCHMARK_NAME="$BENCHMARK_NAME" \
    -e BENCHMARK_SYSTEM_PROMPT="$BENCHMARK_SYSTEM_PROMPT" \
    -e INPUT_S3_BUCKET="$INPUT_S3_BUCKET" \
    -e INPUT_S3_KEY="$INPUT_S3_KEY" \
    -e OUTPUT_S3_BUCKET="$OUTPUT_S3_BUCKET" \
    -e OUTPUT_S3_KEY="$OUTPUT_S3_KEY" \
    -e OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
    -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
    -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
    -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}" \
    yourbench-processor

echo "Yourbench processing complete!"
