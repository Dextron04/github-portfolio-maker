#!/usr/bin/env python3
"""
Analyze GitHub Token Permissions and API Access
"""

import os
import requests
import datetime
from dotenv import load_dotenv

load_dotenv('.env.local')

def main():
    headers = {'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'}
    
    print('🔐 Analyzing GitHub Token Permissions and Scope...')
    print('=' * 60)
    
    # Get user info to check token validity and basic info
    user_response = requests.get('https://api.github.com/user', headers=headers)
    if user_response.status_code == 200:
        user_data = user_response.json()
        print(f'✅ Token is valid and active')
        print(f'👤 User: {user_data["login"]} ({user_data.get("name", "No name")})')
        print(f'📧 Email: {user_data.get("email", "Private")}')
        print(f'🏢 Company: {user_data.get("company", "None")}')
        print(f'📍 Location: {user_data.get("location", "Not specified")}')
        print(f'📅 Account created: {user_data.get("created_at", "Unknown")[:10]}')
        print()
        
        # Check scopes from response headers
        scopes = user_response.headers.get('X-OAuth-Scopes', '')
        print(f'🔑 Token Scopes: {scopes if scopes else "Unable to determine"}')
        
        # Test specific permissions by trying different API endpoints
        print('\n🧪 Testing API Endpoint Access:')
        
        # Test repo access
        test_endpoints = [
            ('📁 Repository access', 'https://api.github.com/user/repos'),
            ('👥 Organization access', 'https://api.github.com/user/orgs'),
            ('⭐ Starred repos access', 'https://api.github.com/user/starred'),
            ('👥 Following access', 'https://api.github.com/user/following'),
            ('🔔 Notifications access', 'https://api.github.com/notifications'),
            ('🔑 SSH Keys access', 'https://api.github.com/user/keys'),
            ('📧 Email access', 'https://api.github.com/user/emails'),
        ]
        
        for desc, endpoint in test_endpoints:
            test_response = requests.get(endpoint, headers=headers)
            status = '✅' if test_response.status_code == 200 else '❌'
            print(f'   {status} {desc}: {test_response.status_code}')
            
        print()
        
        # Check rate limit
        rate_limit_response = requests.get('https://api.github.com/rate_limit', headers=headers)
        if rate_limit_response.status_code == 200:
            rate_data = rate_limit_response.json()
            core_limit = rate_data['resources']['core']
            print(f'📊 Rate Limit Status:')
            print(f'   Limit: {core_limit["limit"]} requests/hour')
            print(f'   Used: {core_limit["used"]} requests')
            print(f'   Remaining: {core_limit["remaining"]} requests')
            reset_time = core_limit["reset"]
            reset_datetime = datetime.datetime.fromtimestamp(reset_time)
            print(f'   Resets at: {reset_datetime.strftime("%Y-%m-%d %H:%M:%S")}')
            
    else:
        print(f'❌ Token validation failed: {user_response.status_code}')
        print(f'Response: {user_response.text}')

if __name__ == '__main__':
    main()
