import os
from dotenv import load_dotenv
from github import Github

NUMBER_OF_COMMITS_TO_CHECK = 30

def load_access_token_in_env():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

def authenticate_user():
    # Reading the personal access token from os environ
    access_token = os.environ["GITHUB_ACCESS_TOKEN"]
    # print (access_token)
    client = Github(login_or_token=access_token)
    user = client.get_user()
    # print (user.name)
    return client

def check_code_signing(client, repo_name):
    print(client.get_user().login)
    repo = client.get_repo(repo_name)
    commits = repo.get_commits().get_page(0) # 0-th page already contains latest 30 commits
    print (len(commits))
    assert len(commits) == NUMBER_OF_COMMITS_TO_CHECK
    # If all commits are signed return True
    ret = True
    for commit in commits:
        # print(commit)
        # print (commit.commit.raw_data["verification"]["verified"])
        ret &= commit.commit.raw_data["verification"]["verified"]
    return ret


if __name__ == "__main__":
    load_access_token_in_env()
    client = authenticate_user()
    # signed_commits = check_code_signing(client=client, repo_name="PyGithub/PyGithub")
    signed_commits = check_code_signing(client=client, repo_name="chromium/chromium")
    # signed_commits = check_code_signing(client=client, repo_name="imranur-rahman/risk-explorer-for-software-supply-chains")
    print(f"signed_commit: {signed_commits}")