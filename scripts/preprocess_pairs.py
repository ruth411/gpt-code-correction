#!/usr/bin/env python3
import json
import os
from unidiff import PatchSet

# Input/output paths
GITHUB_RAW    = "data_raw/bugfix_commits.jsonl"
REFINEMENT_DIR= "data_raw"
OUT_DIR       = "data_processed"
os.makedirs(OUT_DIR, exist_ok=True)

def parse_github_diffs(in_path, out_path):
    """
    Simplified diff parser: collects all '-' lines as buggy, '+' lines as fixed.
    """
    with open(in_path, encoding="utf-8") as rf, open(out_path, "w", encoding="utf-8") as wf:
        for line in rf:
            rec = json.loads(line)
            before, after = [], []
            for l in rec.get("diff", "").splitlines():
                # skip file headers and hunk markers
                if l.startswith('--- ') or l.startswith('+++ ') or l.startswith('diff ') \
                   or l.startswith('index ') or l.startswith('@@'):
                    continue
                if l.startswith('-'):
                    before.append(l[1:])
                elif l.startswith('+'):
                    after.append(l[1:])
            if before and after:
                wf.write(json.dumps({
                    "buggy": "\n".join(before).rstrip(),
                    "fixed": "\n".join(after).rstrip()
                }) + "\n")
    print(f"→ Wrote simplified GitHub‑derived pairs to {out_path}")


def extract_refinement_pairs():
    """
    Read CodeXGLUE code‑refinement JSONL files (which have 'buggy' and 'fixed' fields) 
    :contentReference[oaicite:0]{index=0} and re‑emit just those two fields.
    """
    for subset in ["small", "medium"]:
        for split in ["train", "validation", "test"]:
            inp = os.path.join(
                REFINEMENT_DIR,
                f"code_refinement_{subset}_{split}.jsonl"
            )
            out = os.path.join(
                OUT_DIR,
                f"code_refinement_{subset}_{split}_pairs.jsonl"
            )
            with open(inp, encoding="utf-8") as rf, open(out, "w", encoding="utf-8") as wf:
                for line in rf:
                    obj = json.loads(line)
                    wf.write(json.dumps({
                        "buggy": obj["buggy"],
                        "fixed": obj["fixed"]
                    }) + "\n")
            print(f"→ Wrote CodeXGLUE‑derived pairs to {out}")

if __name__ == "__main__":
    # 1) GitHub diffs → pairs
    parse_github_diffs(GITHUB_RAW, os.path.join(OUT_DIR, "bugfix_pairs.jsonl"))
    # 2) CodeXGLUE refinement → pairs
    extract_refinement_pairs()
    print("✅ Step 4 complete.")
