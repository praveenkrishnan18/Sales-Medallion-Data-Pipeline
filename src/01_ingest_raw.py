# Databricks notebook source

import os
import requests

# ============================================================
# Configuration
# ============================================================

GITHUB_OWNER = "praveenkrishnan18"
GITHUB_REPO = "sales-data-source"
GITHUB_BRANCH = "main"

STORAGE_ACCOUNT = "<YOUR_STORAGE_ACCOUNT_NAME>"
CONTAINER = "sales-lake"

RAW_BASE_PATH = (
    f"abfss://{CONTAINER}@"
    f"{STORAGE_ACCOUNT}.dfs.core.windows.net/raw"
)

API_URL = (
    f"https://api.github.com/repos/"
    f"{GITHUB_OWNER}/{GITHUB_REPO}/git/trees/"
    f"{GITHUB_BRANCH}?recursive=1"
)

HEADERS = {
    "Accept": "application/vnd.github+json"
}


# ============================================================
# Discover every file in the source repository
# ============================================================

response = requests.get(API_URL, headers=HEADERS, timeout=30)
response.raise_for_status()

payload = response.json()
files = [item["path"] for item in payload["tree"] if item["type"] == "blob"]

print(f"Files discovered: {len(files)}")


# ============================================================
# Land the entire repository under ADLS raw/
# while preserving the GitHub folder structure.
# ============================================================

for file_path in files:
    raw_url = (
        f"https://raw.githubusercontent.com/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/"
        f"{GITHUB_BRANCH}/{file_path}"
    )

    target_path = f"{RAW_BASE_PATH}/{file_path}"

    print(f"Downloading: {file_path}")

    file_response = requests.get(raw_url, timeout=30)
    file_response.raise_for_status()

    content = file_response.text

    parent_dir = os.path.dirname(target_path)
    if parent_dir:
        dbutils.fs.mkdirs(parent_dir)

    dbutils.fs.put(target_path, content, overwrite=True)

    print(f"Landed: {target_path}")

print("RAW INGESTION COMPLETED")
