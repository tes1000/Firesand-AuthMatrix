import os
import subprocess
import json
import shutil
import unicodedata

TODO_FILE = "todo.txt"
LABEL = "agent-task"

def norm(s):
    return " ".join(unicodedata.normalize("NFKC", s).split()).lower()

def gh(*args, check=False):
    return subprocess.run(["gh", *args], text=True, capture_output=True, check=check)

def get_open_issues():
    proc = gh("issue", "list", "--state", "open", "--json", "number,title,labels")
    if proc.returncode != 0:
        print("Error fetching issues:", proc.stderr)
        return []
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        print("Failed to decode JSON:", proc.stdout)
        return []

def find_existing_issue(title, issues):
    t = norm(title)
    for issue in issues:
        if norm(issue["title"]) == t:
            return issue
    return None

def retag_issue(issue):
    num = str(issue["number"])
    print(f"Retagging issue #{num}")

    labels = [l["name"] for l in issue.get("labels", [])]
    if LABEL in labels:
        gh("issue", "edit", num, "--remove-label", LABEL)

    gh("issue", "edit", num, "--add-label", LABEL)

def create_new_issue(title):
    print(f"Creating issue: {title}")
    proc = gh(
        "issue", "create",
        "--title", title,
        "--body", "Automatically generated task from todo.txt.",
        "--label", LABEL
    )
    if proc.returncode != 0:
        print("Issue creation failed:", proc.stderr)

def process_title(title):
    issues = get_open_issues()
    existing = find_existing_issue(title, issues)

    if existing:
        retag_issue(existing)
    else:
        create_new_issue(title)

def main():
    if shutil.which("gh") is None:
        print("ERROR: GitHub CLI not installed or not in PATH.")
        return

    if not os.path.exists(TODO_FILE):
        print(f"ERROR: {TODO_FILE} not found")
        return

    with open(TODO_FILE, "r", encoding="utf-8") as f:
        for line in f:
            title = line.strip()
            if title:
                process_title(title)

if __name__ == "__main__":
    main()
