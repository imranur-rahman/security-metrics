import os
from github import Github

NUMBER_OF_COMMITS_TO_CHECK = 30

def authenticate_user():
    # Reading the personal access token from os environ
    access_token = os.environ.get("GITHUB_ACCESS_TOKEN")

    client = Github(login_or_token=access_token)
    user = client.get_user()
    # print (user.name)
    return client

def check_code_signing(client, repo_name):
    print(client.get_user().login)
    repo = client.get_repo(repo_name)
    commits = repo.get_commits()[:NUMBER_OF_COMMITS_TO_CHECK]
    # print(commits.totalCount)
    # If all commits are signed return True
    ret = True
    for commit in commits:
        # print(commit)
        # print (commit.commit.raw_data["verification"]["verified"])
        ret &= commit.commit.raw_data["verification"]["verified"]
    return ret


if __name__ == "__main__":
    client = authenticate_user()
    # signed_commits = check_code_signing(client=client, repo_name="PyGithub/PyGithub")
    signed_commits = check_code_signing(client=client, repo_name="imranur-rahman/risk-explorer-for-software-supply-chains")
    print(f"signed_commit: {signed_commits}")