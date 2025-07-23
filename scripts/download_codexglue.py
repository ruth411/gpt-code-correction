#!/usr/bin/env python3
from datasets import load_dataset, DownloadConfig

download_config = DownloadConfig(force_download=True)

ds = load_dataset(
    "code_x_glue_cc_code_to_code_trans",
    "bug-fix",
    download_config=download_config
)

for split in ["train", "validation", "test"]:
    out_path = f"data_raw/codexglue_{split}.jsonl"
    ds[split].to_json(out_path, orient="records", lines=True)
    print(f"Wrote {split} → {out_path}")
