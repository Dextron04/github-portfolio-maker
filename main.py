import requests
import os
import base64

def get_github_username():
    """Get the authenticated user's GitHub username"""
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    response = requests.get("https://api.github.com/user", headers=headers)
    if response.status_code == 200:
        return response.json()['login']
    else:
        raise Exception(f"Failed to get user info: {response.status_code}")

def get_user_repos():
    """Get all repositories for the authenticated user with pagination support"""
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    all_repos = []
    page = 1
    per_page = 100  # Maximum allowed by GitHub API
    
    while True:
        url = f"https://api.github.com/user/repos?page={page}&per_page={per_page}&sort=updated"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            repos = response.json()
            if not repos:  # No more repositories
                break
            all_repos.extend(repos)
            page += 1
        else:
            raise Exception(f"Failed to get repositories: {response.status_code}")
    
    return all_repos

def fetch_readme(repo_name, username=None):
    """Fetch README content for a specific repository"""
    if username is None:
        username = get_github_username()
    
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    url = f'https://api.github.com/repos/{username}/{repo_name}/readme'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        content = response.json()['content']
        return base64.b64decode(content).decode('utf-8')
    elif response.status_code == 404:
        return "No README found"
    else:
        return f"Error fetching README: {response.status_code}"