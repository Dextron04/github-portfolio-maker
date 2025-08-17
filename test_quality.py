#!/usr/bin/env python3
"""
Test README quality assessment on a few sample repositories
"""

import os
from dotenv import load_dotenv
from main import get_user_repos, fetch_readme
from run import assess_readme_quality

load_dotenv('.env.local')

def test_readme_quality():
    print('🔍 Testing README Quality Assessment...')
    print('=' * 60)
    
    try:
        repos = get_user_repos()
        print(f'Found {len(repos)} repositories')
        
        # Test first 10 repositories
        test_repos = repos[:10]
        
        print('\n📊 README Quality Analysis:')
        print('-' * 60)
        
        high_quality = []
        low_quality = []
        
        for i, repo in enumerate(test_repos, 1):
            repo_name = repo['name']
            print(f"{i:2d}. {repo_name}", end="")
            
            readme = fetch_readme(repo_name, username=repo.get('owner', {}).get('login'))
            
            if readme != "No README found" and not readme.startswith("Error fetching README"):
                is_worth_processing, score, reason = assess_readme_quality(readme, repo_name, min_score=3)
                
                status = "✅ INCLUDE" if is_worth_processing else "❌ SKIP"
                print(f" - {status} - {reason}")
                
                if is_worth_processing:
                    high_quality.append((repo_name, score))
                else:
                    low_quality.append((repo_name, score, reason))
                    
                # Show snippet of README for context
                readme_snippet = readme[:200].replace('\n', ' ').strip()
                if len(readme_snippet) == 200:
                    readme_snippet += "..."
                print(f"     📄 README: {readme_snippet}")
                print()
            else:
                print(f" - ❌ SKIP - {readme}")
                low_quality.append((repo_name, 0, readme))
                print()
        
        print('=' * 60)
        print('📊 SUMMARY:')
        print(f'✅ High-quality repositories: {len(high_quality)}')
        print(f'❌ Low-quality/skipped repositories: {len(low_quality)}')
        
        if high_quality:
            print(f'\n✅ Would process these {len(high_quality)} repositories:')
            for repo_name, score in high_quality:
                print(f'   - {repo_name} (score: {score})')
        
        if low_quality:
            print(f'\n❌ Would skip these {len(low_quality)} repositories:')
            for item in low_quality:
                if len(item) == 3:
                    repo_name, score, reason = item
                    print(f'   - {repo_name}: {reason}')
                else:
                    repo_name, score = item
                    print(f'   - {repo_name} (score: {score})')
        
        savings = len(low_quality)
        total = len(test_repos)
        percentage_saved = (savings / total) * 100 if total > 0 else 0
        
        print(f'\n💰 API Cost Savings:')
        print(f'   Total repositories checked: {total}')
        print(f'   LLM calls saved: {savings}')
        print(f'   Percentage saved: {percentage_saved:.1f}%')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_readme_quality()
