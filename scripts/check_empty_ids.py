import glob, json, sys

errors = 0
for fn in glob.glob("data_tokens/*.jsonl"):
    with open(fn, encoding="utf-8") as f:
        for i, line in enumerate(f):
            rec = json.loads(line)
            if not rec["buggy_ids"] or not rec["fixed_ids"]:
                print(f"Empty IDs in {fn}, line {i}")
                errors += 1
                break
if errors == 0:
    print("✅ No empty ID lists found in any shard.")
else:
    sys.exit(1)
