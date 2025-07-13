import os
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from github_client import GitHubIssueClient

def check_similarity_and_comment(issue_number: int, client: GitHubIssueClient):
    # Embed issue content
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    issue_body = client.get_issue_body(issue_number)

    if not issue_body:
        print(f"Issue #{issue_number} has no body. Skipping.")
        return

    query_embedding = embedding_model.encode(issue_body, normalize_embeddings=True)[0].tolist()

    # Load Chroma DB
    chroma_path = os.getenv("CHROMA_PATH", "./chroma")
    collection = PersistentClient(path=chroma_path).get_or_create_collection("github_issues")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "distances"]
    )

    similar_ids = results["documents"][0] if results["documents"] else []
    distances = results["distances"][0] if results["distances"] else []

    comment_lines = []
    for id_val, dist in zip(similar_ids, distances):
        if float(dist) < 1:  # similarity threshold
            comment_lines.append(
                f"- [Issue #{id_val}](https://github.com/{os.getenv('GITHUB_REPO')}/issues/{id_val}) – distance: {dist:.2f}"
            )

    if comment_lines:
        comment = "🔎 Similar issues I found:\n\n" + "\n".join(comment_lines)
        client.post_comment(issue_number, comment)
    else:
        comment = "🔎 No similar issues found"
        client.post_comment(issue_number, comment)
