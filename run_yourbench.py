import os
import boto3
import zipfile
import yaml
import logging
from pathlib import Path

from yourbench.utils.convert_to_excel_module import convert_datasets_to_excel
from yourbench.utils.convert_to_atlas_module import convert_dataset

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def download_from_s3(bucket_name, object_key, local_path):
    """Download file from S3 bucket"""
    logger.info(f"Downloading {object_key} from bucket {bucket_name} to {local_path}")
    s3_client = boto3.client("s3")
    s3_client.download_file(bucket_name, object_key, local_path)
    logger.info("Download completed")


def unzip_file(zip_path, extract_dir):
    """Unzip file to specified directory"""
    logger.info(f"Extracting {zip_path} to {extract_dir}")
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    logger.info("Extraction completed")


def create_config_file(config_content, config_path):
    """Create config.yaml file"""
    logger.info(f"Creating config file at {config_path}")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        yaml.dump(yaml.safe_load(config_content), f)
    logger.info("Config file created")


def run_yourbench(config_path):
    """Run yourbench with the provided config using direct Python API call."""
    logger.info(f"Running yourbench with config {config_path}")
    try:
        from yourbench.main import main as yourbench_main
        import sys

        # Simulate CLI arguments for Typer
        sys_argv_backup = sys.argv.copy()
        sys.argv = ["yourbench", "run", "--config", str(config_path)]
        try:
            yourbench_main()
        except SystemExit as e:
            logger.info(
                f"yourbench exited with code {e.code} (caught SystemExit, continuing)"
            )
        finally:
            sys.argv = sys_argv_backup
        logger.info("yourbench execution completed successfully")
        return "Execution completed successfully"
    except Exception as e:
        logger.error(f"Error during yourbench execution: {str(e)}")
        raise


def upload_to_s3(local_path, bucket_name, object_key):
    logger.info(f"Uploading {local_path} to bucket {bucket_name} as {object_key}")
    s3_client = boto3.client("s3")
    s3_client.upload_file(local_path, bucket_name, object_key)
    logger.info("Upload completed")


def upload_directory_to_s3(directory_path, bucket_name, s3_prefix=""):
    for filename in os.listdir(directory_path):
        local_path = os.path.join(directory_path, filename)
        if os.path.isfile(local_path):
            object_key = os.path.join(s3_prefix, filename) if s3_prefix else filename
            upload_to_s3(local_path, bucket_name, object_key)


def main():
    # Get environment variables
    benchmark_name = os.environ.get("BENCHMARK_NAME")
    benchmark_system_prompt = os.environ.get("BENCHMARK_SYSTEM_PROMPT")
    input_bucket = os.environ.get("INPUT_S3_BUCKET")
    input_key = os.environ.get("INPUT_S3_KEY")
    output_bucket = os.environ.get("OUTPUT_S3_BUCKET")
    output_key = os.environ.get("OUTPUT_S3_KEY")

    if not all([input_bucket, input_key, output_bucket, output_key]):
        logger.error("Missing required environment variables")
        raise ValueError("Required environment variables are missing")

    # Define local paths
    base_dir = Path(os.environ.get("WORKDIR", "/app"))
    download_path = base_dir / "input.zip"
    raw_data_dir = base_dir / "task/data/raw"
    dataset_dir = base_dir / "task/dataset"
    config_path = dataset_dir / "config.yaml"
    excel_dir = base_dir / "task/excel"

    # Create required directories
    os.makedirs(raw_data_dir, exist_ok=True)
    os.makedirs(dataset_dir, exist_ok=True)

    # Step 1: Download file from S3
    download_from_s3(input_bucket, input_key, download_path)

    # Step 2: Unzip file to raw data directory
    unzip_file(download_path, raw_data_dir)

    # Step 3: Create config.yaml
    config_content = """
hf_configuration:
  hf_dataset_name: task

local_dataset_dir: task/dataset

model_list:
  - model_name: openai/gpt-4.1
    provider: null
    base_url: "https://openrouter.ai/api/v1"
    api_key: $OPENROUTER_API_KEY
    max_concurrent_requests: 10

pipeline:
  ingestion:
    source_documents_dir: task/data/raw
    output_dir: task/data/processed
  upload_ingest_to_hub:
  summarization:
  chunking:
  single_shot_question_generation:
  multi_hop_question_generation:
  lighteval:
  citation_score_filtering:
"""
    create_config_file(config_content, config_path)

    # Step 4: Run yourbench
    run_yourbench(config_path)

    # Step 5: Convert datasets to Excel
    convert_datasets_to_excel(str(dataset_dir), str(excel_dir), logger=logger)

    # Step 6: Convert to Atlas format
    try:
        lighteval_path = dataset_dir / "lighteval"
        if lighteval_path.exists():
            logger.info(f"Converting lighteval dataset to Atlas format")
            convert_dataset(
                hf_path=str(lighteval_path),
                name=benchmark_name,
                system_prompt=benchmark_system_prompt,
                full_description="Dataset for evaluating built-in knowledge",
                short_description="Fact-based knowledge",
                category="YourBench",
                output_dir=str(base_dir / "task"),  # creates task/atlas_dataset/
            )
            logger.info(f"Atlas conversion completed.")
        else:
            logger.warning(
                f"Lighteval dataset not found at {lighteval_path}, skipping Atlas conversion"
            )
    except Exception as e:
        logger.error(f"Atlas conversion failed: {e}")
        logger.warning("Continuing with the rest of the pipeline")

    upload_directory_to_s3(
        base_dir / "task" / benchmark_name, output_bucket, output_key
    )
    logger.info("All tasks completed successfully")


if __name__ == "__main__":
    main()
