import os
import subprocess
import json

TODO_FILE = "../todo.txt"
LABEL = "agent-task"

def get_open_issues():
    """Get all open issues via gh CLI (no GraphQL)."""
    result = subprocess.run(
        ["gh", "issue", "list", "--state", "open", "--json", "number,title,labels"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        print("Error fetching issues:", result.stderr)
        return []

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to decode JSON:", result.stdout)
        return []


def find_existing_issue(title, issues):
    """Exact match on title, case-insensitive."""
    title_norm = title.strip().lower()
    for issue in issues:
        if issue["title"].strip().lower() == title_norm:
            return issue
    return None


def retag_issue(issue_number):
    print(f"Retagging issue #{issue_number}")

    subprocess.run(["gh", "issue", "edit", str(issue_number), "--remove-label", LABEL])
    subprocess.run(["gh", "issue", "edit", str(issue_number), "--add-label", LABEL])


def create_new_issue(title):
    print(f"Creating new issue: {title}")
    subprocess.run(
        [
            "gh",
            "issue",
            "create",
            "--title",
            title,
            "--body",
            "Automatically generated task from todo.txt.",
            "--label",
            LABEL,
        ],
        check=True,
    )


def process_title(title, issues):
    existing = find_existing_issue(title, issues)

    if existing:
        retag_issue(existing["number"])
    else:
        create_new_issue(title)


def main():
    if not os.path.exists(TODO_FILE):
        print(f"ERROR: {TODO_FILE} not found")
        return

    issues = get_open_issues()

    with open(TODO_FILE, "r", encoding="utf-8") as f:
        for line in f:
            title = line.strip()
            if title:
                process_title(title, issues)


if __name__ == "__main__":
    main()
