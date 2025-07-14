import os
import json
from github import Github
from sentence_transformers import SentenceTransformer

COMMAND_PREFIX = "vectorbot"
EXPECTED_VERB = "embed"

def parse_should_embed():
    """Returns True if the GitHub comment explicitly requests embedding."""
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        return True  # fallback for non-comment triggers

    with open(event_path, "r") as f:
        event = json.load(f)

    if "comment" not in event:
        return True  # triggered from issue creation/edit, allow by default

    comment_body = event["comment"]["body"].strip().lower()
    parts = comment_body.split()
    if len(parts) >= 2 and parts[0] == COMMAND_PREFIX and parts[1] == EXPECTED_VERB:
        return True

    print(f"❌ Ignoring comment: '{comment_body}' — does not match `{COMMAND_PREFIX} {EXPECTED_VERB}`")
    return False

def main():
    if not parse_should_embed():
        return

    issue_number = int(os.getenv("ISSUE_NUMBER"))
    repo_name = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")

    gh = Github(token)
    repo = gh.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)

    # Include full thread (issue + comments)
    comments = issue.get_comments()
    thread = issue.body or ""
    for comment in comments:
        thread += f"\n\n[comment by @{comment.user.login}]: {comment.body or ''}"

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding = model.encode([thread], normalize_embeddings=True).tolist()[0]

    os.makedirs("embeddings", exist_ok=True)
    path = f"embeddings/issue-{issue_number}.json"

    with open(path, "w") as f:
        json.dump({
            "id": str(issue_number),
            "embedding": embedding
        }, f, indent=2)
    msg = f"✅ Saved embedding for issue #{issue_number} to {path}"
    issue.create_comment(msg)
    print(msg)

if __name__ == "__main__":
    main()
