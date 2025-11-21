import subprocess
import json
import time

LABEL = "agent-task"

def gh_json(cmd):
    """Run a gh CLI command and return JSON output."""
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        print("Error:", result.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("JSON decode error:", result.stdout)
        return None


def get_all_issues():
    """Get ALL open issues."""
    return gh_json(["gh", "issue", "list", "--state", "open", "--json", "number,title,author,createdAt"])


def delete_issue(number):
    print(f"Deleting duplicate issue #{number}")
    subprocess.run(["gh", "issue", "delete", str(number), "--yes"])


def retag_issue(number):
    print(f"Retagging keeper issue #{number}")
    subprocess.run(["gh", "issue", "edit", str(number), "--remove-label", LABEL])
    subprocess.run(["gh", "issue", "edit", str(number), "--add-label", LABEL])


def main():
    issues = get_all_issues()
    if not issues:
        print("No issues found.")
        return

    # Group issues by title
    groups = {}
    for issue in issues:
        title = issue["title"].strip().lower()
        groups.setdefault(title, []).append(issue)

    # Process groups with duplicates
    for title, group in groups.items():
        if len(group) <= 1:
            continue

        print(f"\nFound duplicates for title: {title}")

        # Sort by creation date: oldest = keeper
        group.sort(key=lambda x: x["createdAt"])
        keeper = group[0]
        duplicates = group[1:]

        print(f"Keeping issue #{keeper['number']}")
        retag_issue(keeper["number"])

        for dup in duplicates:
            delete_issue(dup["number"])
            time.sleep(0.5)  # avoid GH rate limiting

    print("\nCleanup complete!")


if __name__ == "__main__":
    main()
