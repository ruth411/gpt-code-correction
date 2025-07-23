#!/usr/bin/env python3
import json, random, os

# Paths
IN_FILE  = "data_processed/bugfix_pairs.jsonl"
OUT_DIR  = "data_processed/splits"
os.makedirs(OUT_DIR, exist_ok=True)

# Load all records
with open(IN_FILE, encoding="utf-8") as f:
    records = [json.loads(l) for l in f]

# Shuffle
random.seed(42)
random.shuffle(records)

# Compute split sizes
n = len(records)
n_train = int(n * 0.90)
n_val   = int(n * 0.05)
n_test  = n - n_train - n_val

# Partition
train = records[:n_train]
val   = records[n_train : n_train + n_val]
test  = records[n_train + n_val :]

# Helper to write JSONL
def write_split(name, recs):
    path = os.path.join(OUT_DIR, f"bugfix_{name}.jsonl")
    with open(path, "w", encoding="utf-8") as wf:
        for r in recs:
            wf.write(json.dumps(r) + "\n")
    print(f"Wrote {len(recs)} → {path}")

# Write out
write_split("train", train)
write_split("val",   val)
write_split("test",  test)
