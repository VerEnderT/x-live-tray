import requests
import subprocess
import sys

def get_update_info(username, repo):
    """
    Holt die neuesten Versionsnummern der Releases und die Download-URLs eines GitHub-Repositories.
    
    :param username: GitHub-Nutzername
    :param repo: GitHub-Repository-Name
    :return: Ein Dictionary mit der neuesten Versionsnummer und der Download-URL des neuesten Releases
    """
    url = f"https://api.github.com/repos/{username}/{repo}/releases/latest"
    response = requests.get(url)
    
    #if response.status_code != 200:
     #   raise Exception(f"Fehler beim Abrufen der Daten: {response.status_code}")
    
    data = response.json()
    release_info = {
        "version": data["tag_name"].replace("v", "").strip(),
        "download_url": data["assets"][0]["browser_download_url"] if data["assets"] else "Keine Assets vorhanden"
    }
    
    return release_info

def get_version(package_name):
    try:
        result = subprocess.run(['dpkg', '-s', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            return "x"
        
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':', 1)[1].strip()
        
        return "x"
    
    except Exception as e:
        return "x"

def parse_version(v):
    return tuple(map(int, (v.replace(" ", "").split("."))))

def compare_versions(installed_version, latest_version):
    if installed_version == "x":
        return "x"
    
    installed = parse_version(installed_version)
    latest = parse_version(latest_version)
    
    if installed < latest:
        return "u"
    else:
        return "a"

def update_info(username,repo):
    repo_info = get_update_info(username,repo)
    installed_version = get_version(repo).replace(" ", "")
    latest_version = repo_info["version"].replace(" ", "")
    need_update = compare_versions(installed_version, latest_version)
    url = repo_info["download_url"].replace(" ", "")
    return {'version':latest_version,'installed':installed_version,"update":need_update,"url":url}


if __name__ == "__main__":
    if len(sys.argv) not in [3, 4]:
        print("Usage: python3 script.py <github_username> <repository> [<package_name>]")
        sys.exit(1)
    
    github_username = sys.argv[1]
    repository = sys.argv[2]
    
    if len(sys.argv) == 4:
        package_name = sys.argv[3]
    else:
        package_name = repository

    try:
        # Versionsinformation vom installierten Paket abrufen
        installed_version = get_version(package_name).replace(" ", "")
        
        # Versionsinformation von GitHub abrufen
        update_info = get_update_info(github_username, repository)
        latest_version = update_info["version"].replace(" ", "")
        download_url = update_info["download_url"]
        
        print(f"{installed_version}")
        print(f"{latest_version}")
        print(f"{download_url}")
        
        update_needed = compare_versions(installed_version, latest_version)
        print(update_needed)
        
    except Exception as e:
        print(f"Fehler: {e}")
