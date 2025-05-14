FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy all yourbench files
COPY . .

# Install python3-pip
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install dependencies and yourbench in editable mode
RUN pip install --upgrade pip && \
    pip install boto3 pyyaml awscli && \
    pip install -e .

# Verify installation
RUN yourbench --version || echo "Yourbench installation verification failed but continuing build"

# Environment variables (will be overridden at runtime)
ENV INPUT_S3_BUCKET=""
ENV INPUT_S3_KEY=""
ENV OUTPUT_S3_BUCKET=""
ENV OUTPUT_S3_KEY=""
ENV OPENROUTER_API_KEY=""
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_DEFAULT_REGION="us-east-1"
ENV WORKDIR="/app"

# Create a startup script to run the processing workflow
RUN echo '#!/bin/bash\n\
echo "Running yourbench workflow..."\n\
exec python run_yourbench.py' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Use the startup script as entry point
ENTRYPOINT ["/app/entrypoint.sh"]
