#!/usr/bin/env python3
from datasets import load_dataset, DownloadConfig

# Force a fresh download so we don’t hit the old parquet cache
dlc = DownloadConfig(force_download=True)

# Two subsets: "small" (≈58K train examples) and "medium" (≈52K train examples) :contentReference[oaicite:0]{index=0}
DATASET_NAME = "google/code_x_glue_cc_code_refinement"
OUTPUT_DIR   = "data_raw"

for subset in ["small", "medium"]:
    print(f"→ Downloading {DATASET_NAME} config='{subset}' …")
    ds = load_dataset(
      DATASET_NAME,
      subset,
      download_config=dlc,
      cache_dir=f"{OUTPUT_DIR}/hf_cache"
    )
    for split in ["train", "validation", "test"]:
        out_path = f"{OUTPUT_DIR}/code_refinement_{subset}_{split}.jsonl"
        ds[split].to_json(out_path, orient="records", lines=True)
        print(f"  • Wrote {split} → {out_path}")

print("✅ All done.")
