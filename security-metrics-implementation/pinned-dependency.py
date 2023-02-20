import csv
import time
import os
import json
from dotenv import load_dotenv
from github import Github, UnknownObjectException

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

def repo_extract_from_url(repo_url: str) -> str:
    repo = repo_url.split("/")
    username = repo[-2]
    repo_name = repo[-1]
    return username + "/" + repo_name

def find_ecosystem(repo):
    # TODO: Need to add setup.py?
    try:
        repo.get_contents("requirements.txt")
        return "pypi"
    except UnknownObjectException:
        None
    try:
        repo.get_contents("package-lock.json")
        return "npm"
    except UnknownObjectException:
        None
    try:
        repo.get_contents("package.json")
        return "npm"
    except UnknownObjectException:
        None
    
    # default value return
    return ""

def check_pypi_dependency(repo):
    dependency_file = repo.get_contents("requirements.txt")
    print (repo)
    print (dependency_file)
    print (dependency_file.decoded_content.decode())

    lines = dependency_file.decoded_content.decode()

    # If any line does not contain "==", we consider that this
    # dependency is not pinned
    for line in lines:
        if "==" not in line:
            return False
    return True

def check_npm_dependency(repo):
    try:
        repo.get_contents("package-lock.json")
        return True
    except UnknownObjectException:
        None
    dependency_file = repo.get_contents("package.json")
    print (repo)
    print (dependency_file)
    print (dependency_file.decoded_content.decode())

    file = json.loads(dependency_file.decoded_content.decode())
    if file.get("devDependencies") is None and file.get("dependencies") is None:
        # there exists no dependency in "package.json" file
        return True
    # TODO: What if "dependencies" is present instead of/along with devDependencies?: DONE
    dependencies = {}
    if file.get("devDependencies") is not None:
        dependencies.update(file["devDependencies"])
    if file.get("dependencies") is not None:
        dependencies.update(file["dependencies"])

    print (dependencies)
    # TODO: case "asd": "http://adf.com/adf.tar.gz"???
    # TODO: case "qwe": "1.0.0 - 2.9.9"???
    # TODO: case "jkl": "file:../jkl"???
    # TODO: case "fgh": "3.3.x"
    # TODO: What about nested dependency list in sub modules?
    for dependency, version in dependencies.items():
        print (dependency)
        print (version)
        # Exclusion criteria
        if version.startswith("^") or version.startswith("~") or \
            ("<" or ">" or "||" or "latest") in version:
            return False
    return True

def check_pinned_dependency(client, repo_name):
    repo = client.get_repo(repo_name)
    ecosystem = find_ecosystem(repo=repo)
    if ecosystem == "pypi":
        return check_pypi_dependency(repo)
    elif ecosystem == "npm":
        return check_npm_dependency(repo)
    else:
        print ("Don't know what ecosystem it is!")
        return False

def check_pinned_dependency_with_time(client, repo_name):
    
    # Starting time
    st = time.time()
    is_signed_commit_enabled = check_pinned_dependency(client=client, repo_name=repo_name)
    # Ending time
    et = time.time()
    return is_signed_commit_enabled, (et - st)

def open_csv_file():
    """
    This function creates a CSV file with headers, "Repository",
    "Are All Dependencies Pinned", "Time Elapsed (s)", "Repo URL".
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
    csv_file = open("pinned_dependency_demo.csv", "w")
    header = ["Repository", "Are All Dependencies Pinned", "Time Elapsed (s)", "Repo URL"]
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()
    return writer

def func(csv_writer, client, repo_name):
    """
    This function calls the "check_pinned_dependency_with_time" function
    to find the pinned_dependency status and the time needed to do the 
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
    are_all_dependencies_pinned, time_elapsed = check_pinned_dependency_with_time(client=client, repo_name=repo_name)
    csv_writer.writerow({
        "Repository": repo_name,
        "Are All Dependencies Pinned": are_all_dependencies_pinned,
        "Time Elapsed (s)": time_elapsed,
        "Repo URL": "https://github.com/" + repo_name
    })

def main():
    load_access_token_in_env()
    client = authenticate_user()

    csv_writer = open_csv_file()
    
    with open("npm_repos.txt") as file:
        for line in file:
            repo_url = line.rstrip()
            repo = repo_extract_from_url(repo_url)
            print (repo)
            func(csv_writer=csv_writer, client=client, repo_name=repo)

if __name__ == "__main__":
    main()