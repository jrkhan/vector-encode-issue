import os
import json
from sentence_transformers import SentenceTransformer
from github import Github

def main():
    issue_number = int(os.getenv("ISSUE_NUMBER"))
    repo_name = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")

    gh = Github(token)
    repo = gh.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding = model.encode([issue.body or ""], normalize_embeddings=True).tolist()[0]

    os.makedirs("embeddings", exist_ok=True)
    path = f"embeddings/issue-{issue_number}.json"

    with open(path, "w") as f:
        json.dump({
            "id": str(issue_number),
            "embedding": embedding
        }, f, indent=2)

    print(f"✅ Saved embedding for issue #{issue_number} to {path}")

if __name__ == "__main__":
    main()
