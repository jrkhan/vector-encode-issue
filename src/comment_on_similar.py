import os
from github import Github
from github_client import GitHubIssueClient
from similarity_check import check_similarity_and_comment

def main():
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPO")
    issue_number = int(os.getenv("ISSUE_NUMBER"))

    if not token or not repo_name:
        raise EnvironmentError("GITHUB_TOKEN and GITHUB_REPO must be set.")

    gh = Github(token)
    repo = gh.get_repo(repo_name)
    client = GitHubIssueClient(repo)

    check_similarity_and_comment(issue_number, client)

if __name__ == "__main__":
    main()
