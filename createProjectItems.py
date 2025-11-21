import os
import subprocess
import json

TODO_FILE = "todo.txt"
LABEL = "agent-task"

def run_gh_json(command_list):
    """Run a GH CLI command that returns JSON."""
    result = subprocess.run(
        command_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        return None

    try:
        return json.loads(result.stdout)
    except:
        return None


def find_existing_issue(title: str):
    """Search for an issue with exactly matching title."""
    issues = run_gh_json([
        "gh", "issue", "list",
        "--search", f'"{title}"',
        "--state", "open",
        "--json", "number,title,labels"
    ])

    if not issues:
        return None

    for issue in issues:
        if issue["title"].strip().lower() == title.strip().lower():
            return issue

    return None


def retag_issue(issue_number: int):
    """Remove and re-add the label to trigger workflows."""
    print(f"Retagging existing issue #{issue_number}")

    # Remove label (ignore errors if not present)
    subprocess.run(["gh", "issue", "edit", str(issue_number), "--remove-label", LABEL])

    # Re-add label to trigger automation
    subprocess.run(["gh", "issue", "edit", str(issue_number), "--add-label", LABEL])


def create_new_issue(title: str):
    """Create a new issue with label."""
    print(f"Creating new issue: {title}")

    cmd = [
        "gh", "issue", "create",
        "--title", title,
        "--body", "Automatically generated task from todo.txt.",
        "--label", LABEL
    ]

    subprocess.run(cmd, check=True)


def process_title(title: str):
    existing = find_existing_issue(title)

    if existing:
        print(f"Issue already exists: #{existing['number']} — retagging")
        retag_issue(existing["number"])
    else:
        create_new_issue(title)


def main():
    if not os.path.exists(TODO_FILE):
        print("ERROR: todo.txt not found")
        return

    with open(TODO_FILE, "r", encoding="utf-8") as f:
        for line in f:
            title = line.strip()
            if title:
                process_title(title)


if __name__ == "__main__":
    main()
