#!/usr/bin/env python3
import os, json
from tokenizers import ByteLevelBPETokenizer
from tqdm import tqdm

# Load your trained tokenizer
tokenizer = ByteLevelBPETokenizer(
    "tokenizer/vocab.json",
    "tokenizer/merges.txt",
)

IN_DIR  = "data_processed"
OUT_DIR = "data_tokens"
os.makedirs(OUT_DIR, exist_ok=True)

SHARD_LIMIT = 100 * 1024 * 1024  # ~100 MB per shard

def write_shard(records, split, idx):
    path = f"{OUT_DIR}/{split}_shard{idx:03d}.jsonl"
    with open(path, "w", encoding="utf-8") as wf:
        for r in records:
            wf.write(json.dumps(r) + "\n")
    print(f"Wrote {path}")

for fname in sorted(os.listdir(IN_DIR)):
    if not fname.endswith("_pairs.jsonl"):
        continue
    split = fname.replace("_pairs.jsonl", "")
    shard_idx = 0
    shard_records = []
    shard_size = 0

    for line in tqdm(open(f"{IN_DIR}/{fname}", encoding="utf-8"), desc=split):
        obj = json.loads(line)
        # encode to token IDs
        buggy_ids = tokenizer.encode(obj["buggy"]).ids
        fixed_ids = tokenizer.encode(obj["fixed"]).ids
        rec = {"buggy_ids": buggy_ids, "fixed_ids": fixed_ids}
        rec_bytes = len((json.dumps(rec) + "\n").encode("utf-8"))

        # if this record would overflow the shard, flush first
        if shard_records and shard_size + rec_bytes > SHARD_LIMIT:
            write_shard(shard_records, split, shard_idx)
            shard_idx += 1
            shard_records, shard_size = [], 0

        shard_records.append(rec)
        shard_size += rec_bytes

    # write any remaining
    if shard_records:
        write_shard(shard_records, split, shard_idx)
