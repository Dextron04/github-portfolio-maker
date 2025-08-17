#!/usr/bin/env python3
"""
Test private repository access with the GitHub token
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

def test_private_repo_access():
    headers = {'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'}
    
    print('🔍 Investigating Private Repository Access...')
    print('=' * 60)
    
    # Check the token scopes more thoroughly
    response = requests.get('https://api.github.com/user', headers=headers)
    print('🔐 Token Response Headers:')
    for key, value in response.headers.items():
        if 'scope' in key.lower() or 'oauth' in key.lower():
            print(f'  {key}: {value}')
    
    # Check if we can see the actual scopes
    token_info = response.headers.get('X-OAuth-Scopes', 'Not available')
    print(f'🔑 OAuth Scopes: {token_info}')
    print()
    
    # Try different API endpoints to test private repo access
    print('🧪 Testing Different Repository Endpoints:')
    
    endpoints_to_test = [
        ('All repos (default)', 'https://api.github.com/user/repos'),
        ('All repos (explicit)', 'https://api.github.com/user/repos?visibility=all'),
        ('Public repos only', 'https://api.github.com/user/repos?visibility=public'),
        ('Private repos only', 'https://api.github.com/user/repos?visibility=private'),
        ('Owner repos', 'https://api.github.com/user/repos?affiliation=owner'),
        ('All affiliations', 'https://api.github.com/user/repos?affiliation=owner,collaborator,organization_member'),
    ]
    
    for desc, endpoint in endpoints_to_test:
        try:
            resp = requests.get(endpoint, headers=headers)
            if resp.status_code == 200:
                repos = resp.json()
                private_count = sum(1 for repo in repos if repo.get('private', False))
                public_count = sum(1 for repo in repos if not repo.get('private', False))
                print(f'✅ {desc}:')
                print(f'   Total: {len(repos)}, Public: {public_count}, Private: {private_count}')
                
                # Show first few private repos if any
                if private_count > 0:
                    private_repos = [r for r in repos if r.get('private', False)]
                    print('   Private repos found:')
                    for repo in private_repos[:3]:
                        print(f'     - {repo["name"]} ({repo.get("language", "Unknown")})')
                    if len(private_repos) > 3:
                        print(f'     ... and {len(private_repos) - 3} more')
                        
            else:
                print(f'❌ {desc}: HTTP {resp.status_code}')
                if resp.status_code == 403:
                    try:
                        error_msg = resp.json().get('message', 'Access denied')
                        print(f'   Error: {error_msg}')
                    except:
                        print('   Error: Access denied (no JSON response)')
        except Exception as e:
            print(f'❌ {desc}: Error - {e}')
        print()
    
    # Check what the current main.py function is actually getting
    print('🔍 Testing Current main.py Implementation:')
    try:
        from main import get_user_repos
        repos = get_user_repos()
        private_count = sum(1 for repo in repos if repo.get('private', False))
        public_count = sum(1 for repo in repos if not repo.get('private', False))
        print(f'   Current function results: {len(repos)} total, {public_count} public, {private_count} private')
        
        if private_count == 0:
            print('   ⚠️  No private repositories found with current implementation!')
        
    except Exception as e:
        print(f'   ❌ Error testing main.py function: {e}')

if __name__ == '__main__':
    test_private_repo_access()
