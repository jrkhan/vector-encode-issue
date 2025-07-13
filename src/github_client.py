# github_client.py

class GitHubIssueClient:
    def __init__(self, repo):
        self.repo = repo

    def get_issue_body(self, issue_number: int) -> str:
        return self.repo.get_issue(number=issue_number).body or ""

    def post_comment(self, issue_number: int, comment: str):
        self.repo.get_issue(number=issue_number).create_comment(comment)
