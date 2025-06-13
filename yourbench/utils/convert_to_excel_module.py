import os
import json
import numpy as np
import re
from datasets import load_from_disk
import pandas as pd

def convert_datasets_to_excel(dataset_dir, excel_dir=None, logger=None):
    """
    Convert all relevant dataset subsets in dataset_dir to Excel files in excel_dir.
    If excel_dir is None, will create 'excel' subdir in dataset_dir's parent.
    """
    if excel_dir is None:
        excel_dir = os.path.join(os.path.dirname(dataset_dir), "excel")
    subsets = [
        "ingested", "summarized", "chunked", "single_shot_questions", "multi_hop_questions", "lighteval"
    ]
    dataset_paths = {k: os.path.join(dataset_dir, k) for k in subsets}

    def clean_illegal_chars(val):
        if isinstance(val, str):
            return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", val)
        return val

    os.makedirs(excel_dir, exist_ok=True)
    for title, path in dataset_paths.items():
        try:
            if not os.path.exists(path):
                if logger:
                    logger.warning(f"Dataset subset '{title}' not found at {path}, skipping.")
                continue
            ds = load_from_disk(str(path))
            df = ds.to_pandas()
            df = df.map(clean_illegal_chars)
            if "citations" in df.columns:
                df["citations"] = df["citations"].apply(lambda x: json.dumps(x.tolist()) if isinstance(x, np.ndarray) else str(x))
            excel_path = os.path.join(excel_dir, f"{title}.xlsx")
            df.to_excel(excel_path, index=False)
            if logger:
                logger.info(f"Converted {title} to {excel_path}")
        except Exception as e:
            if logger:
                logger.warning(f"Failed to convert {title} to Excel: {e}")
            continue
    if logger:
        logger.info("Excel conversion completed.")
