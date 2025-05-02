import json
import numpy as np
import os
import re
import sys

from datasets import load_from_disk


if len(sys.argv) < 2:
    print("Usage: python convert_to_excel.py <dataset_name>")
    sys.exit(1)


def clean_illegal_chars(val):
    if isinstance(val, str):
        return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", val)
    return val


# get it from first cmd arg
dataset_name = sys.argv[1]

# Replace this path with your actual dataset directory
dataset_base_path = f"datasets/{dataset_name}/dataset/"
save_excels_to = f"datasets/{dataset_name}/excel/"
subsets = ["ingested", "summarized", "chunked", "single_shot_questions", "multi_hop_questions", "lighteval"]
dataset_paths = {k: dataset_base_path + k for k in subsets}

for title, path in dataset_paths.items():
    try:
        ds = load_from_disk(path)
        df = ds.to_pandas()

        df = df.map(clean_illegal_chars)

        if "citations" in df.columns:
            df["citations"] = df["citations"].apply(lambda x: json.dumps(x.tolist()) if isinstance(x, np.ndarray) else str(x))

        # create directory if it doesn't exist
        os.makedirs(save_excels_to, exist_ok=True)

        df.to_excel(f"{save_excels_to}{title}.xlsx", index=False)
        print(f"{title} -> {save_excels_to}{title}.xlsx")

    except Exception as e:
        print(f"{title} :: FAIL, skipping ({e})")
        continue
