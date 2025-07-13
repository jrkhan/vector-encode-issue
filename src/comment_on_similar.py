import os
import json
import glob
from sentence_transformers import SentenceTransformer
from github import Github
from chromadb import PersistentClient
from github_client import GitHubIssueClient
from similarity_check import check_similarity_and_comment

def load_all_embeddings():
    """
    Loads all individual issue embedding files from the 'embeddings/' directory.
    Each file should contain a JSON object with 'id' and 'embedding' keys.
    """
    embeddings = []
    for file in glob.glob("embeddings/issue-*.json"):
        try:
            with open(file, "r") as f:
                embeddings.append(json.load(f))
        except Exception as e:
            print(f"⚠️ Failed to read {file}: {e}")
    return embeddings

def sync_chroma_with_embeddings():
    """
    Synchronizes the local Chroma vector database with all embeddings
    found in the 'embeddings/' directory.

    This is a brute-force re-sync: existing entries for matching IDs are deleted,
    then re-added. This avoids merge conflicts and ensures consistency.
    """
    chroma_path = os.getenv("CHROMA_PATH", "./chroma")
    client = PersistentClient(path=chroma_path)
    collection = client.get_or_create_collection("github_issues")

    embeddings = load_all_embeddings()

    if not embeddings:
        print("⚠️ No embeddings found. Skipping Chroma sync.")
        return

    ids = [str(row["id"]) for row in embeddings]
    vectors = [row["embedding"] for row in embeddings]

    # Remove any existing versions of these IDs
    collection.delete(ids=ids)

    # Add updated embeddings
    collection.add(
        ids=ids,
        embeddings=vectors,
        documents=ids  # optional — could be descriptions or titles in the future
    )

def main():
    """
    Main entry point: loads the current issue from GitHub,
    rebuilds the Chroma DB from existing local embedding files,
    and runs semantic similarity detection + comment.
    """
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPO")
    issue_number = int(os.getenv("ISSUE_NUMBER"))

    if not token or not repo_name:
        raise EnvironmentError("GITHUB_TOKEN and GITHUB_REPO must be set.")

    # Rebuild Chroma from disk
    sync_chroma_with_embeddings()

    # Run similarity check and comment
    gh = Github(token)
    repo = gh.get_repo(repo_name)
    client = GitHubIssueClient(repo)

    check_similarity_and_comment(issue_number, client)

if __name__ == "__main__":
    main()
