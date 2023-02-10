import csv
import time
import os
from dotenv import load_dotenv
from github import Github

NUMBER_OF_COMMITS_TO_CHECK = 30

def load_access_token_in_env():
    """
    This functions loads the Github access token stored in the ".env" file
    and makes it available to use later in the program by simply accessing
    the token (e.g., with os.environ).

    Parameters
    ----------
    No parameter necessary. However, it assumes that the secret is stored
    in the ".env" file and the ".env" file is located in the same folder 
    of this script.

    Returns
    -------
    This function returns nothing.

    """
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

def authenticate_user():
    """
    This function authenticates an user from the access token.

    This function first access the environment variable to get the
    Github access token and verifies whether an access token is 
    available in the environment variable. Then, it calls the Github
    REST API to verify if the access token is correct and returns
    the client object found from calling the REST API.
    
    In this function and the following functions we are using the 
    PyGithub library to communicate with Github REST API.

    Parameters
    ----------
    This function takes no parameter.

    Returns
    -------
    object
        Instantiation of the object which can be used further to
        make calls to the Github REST API.

    """
    # Reading the personal access token from os environ
    access_token = os.environ.get("GITHUB_ACCESS_TOKEN")

    # To check if the access token is actually in env variable
    assert access_token != None
    
    client = Github(login_or_token=access_token)
    return client

def check_code_signing(client, repo_name):
    """
    This function checks whether the last check of commits are
    signed or not.

    The function first get the repo by calling Github REST API
    with the "repo_name" argument. Then it again calls the REST
    API to get the last 30 commits of the repository. After getting
    the list of commits, it does a sanity checking. It also handles
    the case when the repository contains less than 30 commits in
    total. After that, it uses a for loop to do AND operation with
    "verified" status associated with each commit in the commit list.
    If all commits contain "True" in the "verified" field, the function
    return "True". If any one of the commits has "False" in the "verified"
    field, it return "False".

    Parameters
    ----------
    client : object
        Instance of the Github REST API object.
    repo_name : string
        The repository name in the format "user_name/repository_name".

    Returns
    -------
    boolean
        If the latest "NUMBER_OF_COMMITS_TO_CHECK" commits are signed,
        return True, otherwise False.

    """
    repo = client.get_repo(repo_name)
    commits = repo.get_commits().get_page(0) # 0-th page already contains latest 30 commits
    
    assert len(commits) <= NUMBER_OF_COMMITS_TO_CHECK

    # If all commits are signed return True
    ret = True
    for commit in commits:
        ret &= commit.commit.raw_data["verification"]["verified"]
    return ret

def check_signed_commit_with_time(client, repo_name):
    """
    Utility to call the "check_code_signing" function and
    calculate the time needed for getting the commit list
    and the computation.

    Parameters
    ----------
    client : object
        Instance of the Github REST API object.
    repo_name : string
        The repository name in the format "user_name/repository_name".

    Returns
    -------
    boolean
        The return value from calling the function "check_code_signing".
    int
        Time needed to find the "code_signing" status.

    """
    # Starting time
    st = time.time()
    is_signed_commit_enabled = check_code_signing(client=client, repo_name=repo_name)
    # Ending time
    et = time.time()
    return is_signed_commit_enabled, (et - st)

def open_csv_file():
    """
    This function creates a CSV file with headers, "Repository",
    "Is Signed Commit Enabled", "Time Elapsed (s)", "Repo URL".
    Then it returns the writer object to write on the CSV file
    later.

    Parameters
    ----------
    No parameters

    Returns
    -------
    object
        Instance of CSV writer object.

    """
    # Open CSV file to store the data
    csv_file = open("signed_commit_demo.csv", "w")
    header = ["Repository", "Is Signed Commit Enabled", "Time Elapsed (s)", "Repo URL"]
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()
    return writer

def func(csv_writer, client, repo_name):
    """
    This function calls the "check_signed_commit_with_time" function
    to find the signed_commit status and the time needed to do the 
    computation. After that, it writes the informations to the CSV
    file by using csv_writer object.

    Parameters
    ----------
    csv_writer : object
        Instance of CSV writer object.
    client : object
        Instance of the Github REST API object.
    repo_name : string
        The repository name in the format "user_name/repository_name".

    Returns
    -------
    This function returns nothing.

    """
    is_signed_commit_enabled, time_elapsed = check_signed_commit_with_time(client=client, repo_name=repo_name)
    csv_writer.writerow({
        "Repository": repo_name,
        "Is Signed Commit Enabled": is_signed_commit_enabled,
        "Time Elapsed (s)": time_elapsed,
        "Repo URL": "https://github.com/" + repo_name
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

    repo = "imranur-rahman/security-metrics"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "storaged-project/blivet"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "magma/magma"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "david942j/seccomp-tools"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "csutils/csmock"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "Mellanox/mstflint"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "niklasb/libc-database"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "ZhiningLiu1998/awesome-imbalanced-learning"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "david942j/one_gadget"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "Mansimran7/ASE_Group12_Hws"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "gabibi123/analise-gabriela"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "mirellalima07/analise"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "rodrigo081/rodrigo-andres-analise-e-projetos"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "IokioCaina/an-lise"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "tharsoj/analise"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "driiih/ANALISE-"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "pliang279/awesome-phd-advice"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "xairy/linux-kernel-exploitation"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "papers-we-love/papers-we-love"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "Beerkay/IoTResearch"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "husnainfareed/Awesome-Ethical-Hacking-Resources"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "missing-semester/missing-semester"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "MahdiMashrur/Awesome-Coding-Interview-Question-Patterns"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "yangshun/tech-interview-handbook"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "aalhour/awesome-compilers"
    func(csv_writer=csv_writer, client=client, repo_name=repo)

    repo = "Yale-LILY/FOLIO"
    func(csv_writer=csv_writer, client=client, repo_name=repo)


    #main()