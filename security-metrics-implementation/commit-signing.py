import time
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
    # print(client.get_user().login)
    repo = client.get_repo(repo_name)
    commits = repo.get_commits().get_page(0) # 0-th page already contains latest 30 commits
    # print (len(commits))
    assert len(commits) == NUMBER_OF_COMMITS_TO_CHECK
    # If all commits are signed return True
    ret = True
    for commit in commits:
        # print(commit)
        # print (commit.commit.raw_data["verification"]["verified"])
        ret &= commit.commit.raw_data["verification"]["verified"]
    return ret

def check_signed_commit_with_time(client, repo_name):
    # Starting time
    st = time.time()
    is_signed_commit_enabled = check_code_signing(client=client, repo_name=repo_name)
    # Ending time
    et = time.time()
    return is_signed_commit_enabled, (et - st)


if __name__ == "__main__":
    load_access_token_in_env()
    client = authenticate_user()

    repo = "PyGithub/PyGithub"
    is_signed_commit_enabled, time_elapsed = check_signed_commit_with_time(client=client, repo_name=repo)
    print(f"repo: {repo} \t signed_commit_enabled: {is_signed_commit_enabled}, time_elapsed: {time_elapsed} sec")
    
    repo = "chromium/chromium"
    is_signed_commit_enabled, time_elapsed = check_signed_commit_with_time(client=client, repo_name=repo)
    print(f"repo: {repo} \t signed_commit_enabled: {is_signed_commit_enabled}, time_elapsed: {time_elapsed} sec")
    
    repo = "imranur-rahman/risk-explorer-for-software-supply-chains"
    is_signed_commit_enabled, time_elapsed = check_signed_commit_with_time(client=client, repo_name=repo)
    print(f"repo: {repo} \t signed_commit_enabled: {is_signed_commit_enabled}, time_elapsed: {time_elapsed} sec")