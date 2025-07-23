#!/usr/bin/env python3
import os
import sys
import time
import json
import requests

# --- Configuration ---
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    print("Error: Set GITHUB_TOKEN in your environment.", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.cloak-preview"  # needed for commit search
}

# Keywords and languages from your spec
KEYWORDS = ["fix", "bug", "typo"]
LANGUAGES = ["Python", "JavaScript"]
SINCE = "2025-01-01"  # adjust as needed

OUTPUT_PATH = "data_raw/bugfix_commits.jsonl"

def search_commits(keyword, language, page=1):
    query = f"{keyword}+language:{language}+committer-date:>={SINCE}"
    url = f"https://api.github.com/search/commits"
    params = {"q": query, "sort": "committer-date", "order": "desc", "page": page, "per_page": 100}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()

def fetch_diff(repo_full_name, sha):
    url = f"https://api.github.com/repos/{repo_full_name}/commits/{sha}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    # collect all file patches
    patches = []
    for f in data.get("files", []):
        patch = f.get("patch")
        if patch:
            patches.append(patch)
    return "\n---\n".join(patches)

def main():
    seen = set()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        for lang in LANGUAGES:
            for kw in KEYWORDS:
                page = 1
                while True:
                    result = search_commits(kw, lang, page)
                    items = result.get("items", [])
                    if not items: break
                    for item in items:
                        repo = item["repository"]["full_name"]
                        sha = item["sha"]
                        key = f"{repo}@{sha}"
                        if key in seen:
                            continue
                        seen.add(key)
                        try:
                            diff = fetch_diff(repo, sha)
                        except Exception as e:
                            print(f"Warning: failed to fetch {key}: {e}", file=sys.stderr)
                            continue
                        record = {"repo": repo, "sha": sha, "diff": diff}
                        out.write(json.dumps(record) + "\n")
                    page += 1
                    time.sleep(1)  # avoid rate limits
    print(f"Collected {len(seen)} commits into {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
