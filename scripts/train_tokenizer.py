#!/usr/bin/env python3
import os, json
from tokenizers import ByteLevelBPETokenizer

# 1) Gather all buggy/fixed code into one plaintext corpus
os.makedirs("tokenizer", exist_ok=True)
with open("tokenizer/train_corpus.txt", "w", encoding="utf-8") as out:
    for fn in os.listdir("data_processed"):
        if not fn.endswith("_pairs.jsonl"):
            continue
        with open(f"data_processed/{fn}", encoding="utf-8") as rf:
            for line in rf:
                obj = json.loads(line)
                out.write(obj["buggy"] + "\n")
                out.write(obj["fixed"] + "\n")

# 2) Initialize & train
tokenizer = ByteLevelBPETokenizer()
tokenizer.train(
    files=["tokenizer/train_corpus.txt"],
    vocab_size=50_000,
    min_frequency=2,
    special_tokens=["<s>", "<pad>", "</s>", "<unk>", "<mask>"]
)

# 3) Save vocab + merges
tokenizer.save_model("tokenizer")
print("✅ Tokenizer trained and saved under ./tokenizer/")
