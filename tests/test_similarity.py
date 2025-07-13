# test_similarity_end_to_end.py
import os
import shutil
import tempfile
import numpy as np
from github import Github
from github_client import GitHubIssueClient
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from similarity_check import check_similarity_and_comment

def test_similarity_detection_real_chroma(tmp_path):
    # Setup Chroma DB in isolated temp dir
    chroma_path = tmp_path / "chroma"
    os.environ["CHROMA_PATH"] = str(chroma_path)
    os.environ["GITHUB_REPO"] = "fakeuser/fakerepo"

    # Use real Chroma and embedding model
    client = PersistentClient(path=str(chroma_path))
    collection = client.get_or_create_collection("github_issues")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Simulate Issue #1
    issue1_id = "101"
    issue1_text = "How can I retrieve related meanings from encoded representations efficiently?"
    embedding1 = model.encode(issue1_text, normalize_embeddings=True).tolist()
    collection.add(ids=[issue1_id], documents=[issue1_id], embeddings=[embedding1])

    # Simulate GitHub repo with two issues
    mock_repo = _fake_repo({
        101: issue1_text,
        102: "What's the best approach to querying vector embeddings for similarity?"
    })

    # Run similarity detection for issue #102
    check_similarity_and_comment(issue_number=102, client=GitHubIssueClient(repo=mock_repo))

    # Validate that a comment was posted
    posted = mock_repo.get_issue(102).create_comment.call_args[0][0]
    assert f"Issue #{issue1_id}" in posted
    assert "similarity" in posted

def _fake_repo(issue_texts: dict):
    from unittest.mock import MagicMock
    repo = MagicMock()

    issue_map = {}
    for issue_num, body in issue_texts.items():
        issue = MagicMock()
        issue.number = issue_num
        issue.body = body
        issue.create_comment = MagicMock()
        issue_map[issue_num] = issue

    def get_issue(number: int):
        return issue_map[number]

    repo.get_issue.side_effect = get_issue
    return repo
