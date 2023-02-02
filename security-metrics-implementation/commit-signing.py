import csv
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
    access_token = os.environ.get("GITHUB_ACCESS_TOKEN")

    # To check if the access token is actually in env variable
    assert access_token != None
    
    client = Github(login_or_token=access_token)
    return client

def check_code_signing(client, repo_name):
    repo = client.get_repo(repo_name)
    commits = repo.get_commits().get_page(0) # 0-th page already contains latest 30 commits
    
    assert len(commits) <= NUMBER_OF_COMMITS_TO_CHECK

    # If all commits are signed return True
    ret = True
    for commit in commits:
        ret &= commit.commit.raw_data["verification"]["verified"]
    return ret

def check_signed_commit_with_time(client, repo_name):
    # Starting time
    st = time.time()
    is_signed_commit_enabled = check_code_signing(client=client, repo_name=repo_name)
    # Ending time
    et = time.time()
    return is_signed_commit_enabled, (et - st)

def open_csv_file():
    # Open CSV file to store the   data
    csv_file = open("signed_commit_demo.csv", "w")
    header = ["Repository", "Is Signed Commit Enabled", "Time Elapsed (s)"]
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()
    return writer

def func(csv_writer, client, repo_name):
    is_signed_commit_enabled, time_elapsed = check_signed_commit_with_time(client=client, repo_name=repo)
    csv_writer.writerow({
        "Repository": repo_name,
        "Is Signed Commit Enabled": is_signed_commit_enabled,
        "Time Elapsed (s)": time_elapsed
    })

if __name__ == "__main__":
    load_access_token_in_env()
    client = authenticate_user()

    csv_writer = open_csv_file()

    repo = "PyGithub/PyGithub"
    func(csv_writer=csv_writer, client=client, repo_name=repo)
    
    repo = "chromium/chromium"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "imranur-rahman/risk-explorer-for-software-supply-chains"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "imranur-rahman/dns-cache-poisoning-attack-reloaded"
    func(csv_writer=csv_writer, client=client, repo_name=repo)