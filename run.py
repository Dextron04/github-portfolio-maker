#!/usr/bin/env python3
"""
GitHub Portfolio Generator
A script to generate a PDF portfolio from your GitHub repositories
"""

import os
import argparse
from dotenv import load_dotenv
from main import get_user_repos, fetch_readme
from process import generate_pdf, clean_text_for_pdf
from fpdf import FPDF
import re

# Load environment variables from .env.local file
load_dotenv('.env.local')

def get_readme_preview(readme_content, max_lines=10):
    """
    Get a preview of the README content for manual review.
    Returns a formatted preview string.
    """
    if not readme_content or readme_content in ["No README found", ""] or readme_content.startswith("Error fetching README"):
        return "No README content available"
    
    lines = readme_content.split('\n')
    preview_lines = lines[:max_lines]
    
    # Show basic stats
    total_lines = len(lines)
    total_chars = len(readme_content)
    total_words = len(readme_content.split())
    
    preview = f"📊 README Stats: {total_chars} chars, {total_words} words, {total_lines} lines\n"
    preview += "─" * 60 + "\n"
    
    for line in preview_lines:
        # Truncate very long lines
        if len(line) > 80:
            line = line[:77] + "..."
        preview += line + "\n"
    
    if total_lines > max_lines:
        preview += f"... ({total_lines - max_lines} more lines)\n"
    
    preview += "─" * 60
    
    return preview

def should_include_repository(repo, readme_content):
    """
    Ask user whether to include this repository in the portfolio.
    Returns True if should include, False otherwise.
    """
    if not readme_content or readme_content in ["No README found", ""] or readme_content.startswith("Error fetching README"):
        print(f"   ❌ No README found - automatically skipping")
        return False
    
    repo_name = repo['name']
    repo_desc = repo.get('description', 'No description')
    repo_lang = repo.get('language', 'Unknown')
    repo_stars = repo.get('stargazers_count', 0)
    repo_private = repo.get('private', False)
    
    print(f"\n📁 Repository: {repo_name}")
    print(f"   📝 Description: {repo_desc}")
    print(f"   💻 Language: {repo_lang}")
    print(f"   ⭐ Stars: {repo_stars}")
    print(f"   🔒 Private: {repo_private}")
    print()
    
    # Show README preview
    preview = get_readme_preview(readme_content)
    print("📄 README Preview:")
    print(preview)
    print()
    
    # Ask for user decision
    while True:
        response = input(f"Include '{repo_name}' in portfolio? (y/n/s=show more/q=quit): ").strip().lower()
        
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        elif response in ['s', 'show', 'show more']:
            # Show more of the README
            print("\n📄 Full README Content:")
            print("=" * 80)
            print(readme_content)
            print("=" * 80)
            print()
        elif response in ['q', 'quit']:
            print("Exiting portfolio generation...")
            exit(0)
        else:
            print("Please enter 'y' (yes), 'n' (no), 's' (show more), or 'q' (quit)")

def test_pdf_creation():
    """Test PDF creation capabilities before making expensive LLM calls"""
    test_filename = "test_portfolio.pdf"
    
    try:
        print("🔧 Running pre-flight PDF test...")
        
        # Create a simple test PDF with potential problematic characters
        class TestPDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, 'Test PDF', 0, 1, 'C')
                self.ln(5)
        
        pdf = TestPDF()
        pdf.add_page()
        
        # Test various text scenarios that could cause issues
        test_cases = [
            "Regular ASCII text",
            "Text with Unicode: • – — " " ' '",  # Problematic Unicode
            "Mixed content: Project #1 - Feature list",
            "Special chars: @#$%^&*()[]{}",
            clean_text_for_pdf("Unicode test: • – — " " ' '")  # Cleaned version
        ]
        
        pdf.set_font('Arial', '', 12)
        for i, test_text in enumerate(test_cases, 1):
            try:
                cleaned_text = clean_text_for_pdf(test_text)
                pdf.cell(0, 10, f"Test {i}: {cleaned_text}", 0, 1)
            except Exception as e:
                raise Exception(f"Failed to add test text {i}: {str(e)}")
        
        # Test multi-cell functionality
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "Multi-cell test:", 0, 1)
        pdf.set_font('Arial', '', 11)
        
        test_multiline = """This is a multi-line test with various content:
* Bullet point 1
* Bullet point 2
Regular paragraph text that spans multiple lines and tests the multi_cell functionality."""
        
        cleaned_multiline = clean_text_for_pdf(test_multiline)
        pdf.multi_cell(0, 6, cleaned_multiline)

        # --- NEW TESTS FOR HORIZONTAL SPACE ERRORS ---
        pdf.ln(5)
        pdf.set_font('Arial', '', 12)
        try:
            # Test: Single wide character in a very narrow cell
            pdf.cell(1, 10, 'W', 0, 1)  # Should fail or be caught
        except Exception as e:
            if 'Not enough horizontal space' in str(e):
                print(f"❌ PDF test failed: {str(e)} (single wide char in narrow cell)")
                raise
            else:
                print(f"⚠️  Unexpected error in narrow cell test: {str(e)}")
                raise
        try:
            # Test: Long unbreakable string in a cell with width 0 (auto width)
            long_unbreakable = 'W' * 1000
            pdf.cell(0, 10, long_unbreakable, 0, 1)
        except Exception as e:
            if 'Not enough horizontal space' in str(e):
                print(f"❌ PDF test failed: {str(e)} (long unbreakable string)")
                raise
            else:
                print(f"⚠️  Unexpected error in long unbreakable string test: {str(e)}")
                raise
        # --- END NEW TESTS ---
        
        # Try to save the PDF
        pdf.output(test_filename)
        
        # Verify the file was created
        if not os.path.exists(test_filename):
            raise Exception("PDF file was not created")
        
        # Check file size (should be > 0)
        file_size = os.path.getsize(test_filename)
        if file_size == 0:
            raise Exception("PDF file is empty")
        
        print(f"✅ PDF test passed! Test file size: {file_size} bytes")
        
        # Clean up test file
        os.remove(test_filename)
        print("🗑️  Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF test failed: {str(e)}")
        
        # Clean up test file if it exists
        try:
            if os.path.exists(test_filename):
                os.remove(test_filename)
                print("🗑️  Test file cleaned up")
        except:
            pass
        
        return False

def main():
    parser = argparse.ArgumentParser(description="GitHub Portfolio Generator")
    parser.add_argument("--no-llm", action="store_true", help="Generate summaries heuristically without calling the LLM")
    parser.add_argument("--name", type=str, default=None, help="Name to display on the portfolio cover (non-interactive)")
    parser.add_argument("--auto-include-all", action="store_true", help="Automatically include all repositories with READMEs (skip manual selection)")
    args = parser.parse_args()

    # Check for required environment variables
    no_llm = args.no_llm or str(os.getenv("PORTFOLIO_NO_LLM", "")).lower() in ("1", "true", "yes")
    required_vars = ['GITHUB_TOKEN'] + ([] if no_llm else ['ANTHROPIC_API_KEY'])
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following environment variables in your .env.local file:")
        print("GITHUB_TOKEN=your_github_token_here")
        print("ANTHROPIC_API_KEY=your_anthropic_api_key_here")
        return
    
    # Run pre-flight PDF test
    if not test_pdf_creation():
        print("\n❌ PDF test failed. Please fix the issues above before proceeding.")
        print("This check prevents wasting money on LLM calls when PDF generation will fail.")
        return
    
    # Get user's name (CLI arg preferred to avoid interactive prompt in automation)
    user_name = args.name
    if not user_name:
        user_name = input("Enter your name (as you want it to appear on the portfolio): ").strip()
        if not user_name:
            print("❌ Name cannot be empty. Exiting.")
            return
    
    try:
        print("\n🚀 Starting GitHub portfolio generation...")
        print("Fetching all your GitHub repositories...")
        repos = get_user_repos()
        print(f"Found {len(repos)} repositories")
        
        # Filter repositories with READMEs and manual selection
        repos_with_readme = []
        skipped_repos = []
        print(f"\n📋 Found {len(repos)} repositories. Now checking for READMEs...")
        
        if args.auto_include_all:
            print("🤖 Auto-include mode: Adding all repositories with READMEs")
        else:
            print("👤 Manual selection mode: You'll choose which repositories to include")
        
        print()
        
        for i, repo in enumerate(repos, 1):
            repo_name = repo['name']
            print(f"📁 Checking {i}/{len(repos)}: {repo_name}", end="")
            
            # Use the actual repo owner to support org repos and fine-grained tokens
            readme = fetch_readme(repo_name, username=repo.get('owner', {}).get('login'))
            
            if readme != "No README found" and not readme.startswith("Error fetching README"):
                print(" ✅ Has README")
                
                if args.auto_include_all:
                    # Automatically include all repos with READMEs
                    repos_with_readme.append((repo, readme))
                    print(f"   🤖 Auto-included")
                else:
                    # Ask user for manual selection
                    should_include = should_include_repository(repo, readme)
                    
                    if should_include:
                        repos_with_readme.append((repo, readme))
                        print(f"   ✅ Included by user")
                    else:
                        skipped_repos.append(repo_name)
                        print(f"   ❌ Skipped by user")
            else:
                print(f" ❌ No README - {readme}")
                skipped_repos.append(repo_name)
        
        if not repos_with_readme:
            print("\n❌ No repositories selected for portfolio generation.")
            if skipped_repos:
                print(f"Skipped repositories: {', '.join(skipped_repos[:5])}")
                if len(skipped_repos) > 5:
                    print(f"... and {len(skipped_repos) - 5} more")
            return
        
        print(f"\n💰 Selected {len(repos_with_readme)} repositories for processing.")
        if skipped_repos:
            print(f"🚫 Skipped {len(skipped_repos)} repositories")
        
        if no_llm:
            print("Running in NO-LLM mode (heuristic summaries). No API cost.")
        else:
            print(f"This will make {len(repos_with_readme)} LLM calls.")
        
        # Ask for confirmation before making expensive LLM calls
        if not no_llm:
            response = input(f"Continue with {len(repos_with_readme)} LLM calls? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("❌ Operation cancelled by user.")
                return

        # Now process with LLM (expensive operations)
        print(f"\n🤖 Processing {len(repos_with_readme)} repositories{' without LLM' if no_llm else ' with LLM'}...")
        projects = []
        
        for i, (repo, readme) in enumerate(repos_with_readme, 1):
            repo_name = repo['name']
            print(f"Processing {i}/{len(repos_with_readme)}: {repo_name}")
            
            # Import here to avoid loading the LLM client if not needed
            from process import summarize_project
            
            print(f"  🤖 Generating AI summary...")
            summary = summarize_project(readme)
            
            if not summary.startswith("Error generating summary"):
                projects.append({
                    'title': repo_name,
                    'summary': summary
                })
                print(f"  ✅ Summary generated successfully")
            else:
                print(f"  ❌ Failed: {summary}")
        
        print(f"\n📊 Successfully processed {len(projects)} out of {len(repos_with_readme)} repositories")
        
        if projects:
            print(f"📄 Generating final PDF portfolio...")
            generate_pdf(projects, user_name=user_name)
        else:
            print("⚠️ No projects were successfully processed. Creating a placeholder portfolio PDF...")
            placeholder_projects = [{
                'title': 'No Projects Processed',
                'summary': (
                    '**Project Overview:**\n'
                    'No eligible repositories with valid READMEs were processed. This PDF is a placeholder to confirm generation works.\n\n'
                    '**Key Features:**\n'
                    '* Placeholder portfolio generation\n* Verified PDF creation pipeline\n\n'
                    '**Technologies Used:**\n'
                    'fpdf2, Python\n\n'
                    '**Impact & Benefits:**\n'
                    'Confirms your setup works even when no repositories are processed.'
                )
            }]
            generate_pdf(placeholder_projects, user_name=user_name)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 