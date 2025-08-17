#!/usr/bin/env python3
"""
Fetch and display all GitHub repositories accessible with the token
"""

import os
from dotenv import load_dotenv
from main import get_user_repos, get_github_username

# Load environment variables
load_dotenv('.env.local')

def main():
    try:
        print('🔍 Fetching ALL GitHub repositories accessible with your token...')
        print('=' * 70)
        
        username = get_github_username()
        print(f'👤 Authenticated as: {username}')
        
        repos = get_user_repos()
        print(f'📁 Total repositories found: {len(repos)}')
        print('=' * 70)
        
        # Group repos by language for better overview
        languages = {}
        private_count = 0
        public_count = 0
        total_stars = 0
        total_forks = 0
        
        print('\n📋 Complete Repository List:')
        print('-' * 70)
        
        for i, repo in enumerate(repos, 1):
            name = repo['name']
            desc = repo.get('description', 'No description')
            if desc is None:
                desc = 'No description'
            lang = repo.get('language', 'Unknown')
            updated = repo.get('updated_at', 'Unknown')[:10]  # Just date part
            private = repo.get('private', False)
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            
            # Count stats
            if private:
                private_count += 1
            else:
                public_count += 1
                
            total_stars += stars
            total_forks += forks
                
            if lang and lang != 'Unknown':
                languages[lang] = languages.get(lang, 0) + 1
            
            # Display repo info
            privacy_icon = '🔒' if private else '🌐'
            star_info = f' ⭐{stars}' if stars > 0 else ''
            fork_info = f' 🍴{forks}' if forks > 0 else ''
            
            # Truncate description
            desc_display = desc[:60] + '...' if len(desc) > 60 else desc
            
            print(f'{i:2d}. {privacy_icon} {name}')
            print(f'    📝 {desc_display}')
            print(f'    💻 {lang} | 📅 {updated}{star_info}{fork_info}')
            print()
        
        print('=' * 70)
        print('📊 SUMMARY STATISTICS:')
        print(f'🌐 Public repositories: {public_count}')
        print(f'🔒 Private repositories: {private_count}')
        print(f'📁 Total repositories: {len(repos)}')
        print(f'⭐ Total stars: {total_stars}')
        print(f'🍴 Total forks: {total_forks}')
        
        print('\n💻 Programming Languages Used:')
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(repos)) * 100
            print(f'   {lang}: {count} repos ({percentage:.1f}%)')
            
        # Find most recently updated repos
        print('\n🕒 Most Recently Updated (Top 5):')
        sorted_repos = sorted(repos, key=lambda x: x.get('updated_at', ''), reverse=True)
        for i, repo in enumerate(sorted_repos[:5], 1):
            updated = repo.get('updated_at', 'Unknown')[:10]
            print(f'   {i}. {repo["name"]} - {updated}')
            
        # Find repos with most stars
        if total_stars > 0:
            print('\n⭐ Most Starred Repositories:')
            starred_repos = [r for r in repos if r.get('stargazers_count', 0) > 0]
            starred_repos.sort(key=lambda x: x.get('stargazers_count', 0), reverse=True)
            for i, repo in enumerate(starred_repos[:5], 1):
                stars = repo.get('stargazers_count', 0)
                print(f'   {i}. {repo["name"]} - ⭐{stars}')
                
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
