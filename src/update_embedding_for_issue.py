import os, json
from sentence_transformers import SentenceTransformer
from github import Github

issue_number = int(os.getenv("ISSUE_NUMBER"))
repo_name = os.getenv("GITHUB_REPO")
token = os.getenv("GITHUB_TOKEN")

client = Github(token)
repo = client.get_repo(repo_name)
issue = repo.get_issue(number=issue_number)

model = SentenceTransformer("all-MiniLM-L6-v2")
embedding = model.encode([issue.body or ""], normalize_embeddings=True).tolist()[0]

# Update embedding file (e.g. embeddings.json)
path = "embeddings.json"
try:
    with open(path, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    data = []

data = [e for e in data if e["id"] != str(issue_number)]
data.append({"id": str(issue_number), "embedding": embedding})
with open(path, "w") as f:
    json.dump(data, f, indent=2)
