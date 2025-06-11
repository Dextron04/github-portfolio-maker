#!/usr/bin/env python3
"""
GitHub Portfolio Generator
A script to generate a PDF portfolio from your GitHub repositories
"""

import os
from dotenv import load_dotenv
from main import get_user_repos, fetch_readme
from process import generate_pdf, clean_text_for_pdf
from fpdf import FPDF

# Load environment variables from .env.local file
load_dotenv('.env.local')

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
    # Check for required environment variables
    required_vars = ['GITHUB_TOKEN', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following environment variables in your .env.local file:")
        print("GITHUB_TOKEN=your_github_token_here")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        return
    
    # Run pre-flight PDF test
    if not test_pdf_creation():
        print("\n❌ PDF test failed. Please fix the issues above before proceeding.")
        print("This check prevents wasting money on LLM calls when PDF generation will fail.")
        return
    
    try:
        print("\n🚀 Starting GitHub portfolio generation...")
        print("Fetching all your GitHub repositories...")
        repos = get_user_repos()
        print(f"Found {len(repos)} repositories")
        
        # Filter repositories with READMEs first (cheaper operation)
        repos_with_readme = []
        print("\n📋 Checking repositories for READMEs...")
        
        for i, repo in enumerate(repos, 1):
            repo_name = repo['name']
            print(f"Checking {i}/{len(repos)}: {repo_name}", end="")
            
            readme = fetch_readme(repo_name)
            if readme != "No README found" and not readme.startswith("Error fetching README"):
                repos_with_readme.append((repo, readme))
                print(" ✅")
            else:
                print(f" ⚠️ ({readme})")
        
        if not repos_with_readme:
            print("\n❌ No repositories with READMEs found. Nothing to generate.")
            return
        
        print(f"\n💰 Found {len(repos_with_readme)} repositories with READMEs.")
        print(f"This will make {len(repos_with_readme)} LLM calls.")
        
        # Ask for confirmation before making expensive LLM calls
        response = input(f"Continue with {len(repos_with_readme)} LLM calls? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Operation cancelled by user.")
            return
        
        # Now process with LLM (expensive operations)
        print(f"\n🤖 Processing {len(repos_with_readme)} repositories with LLM...")
        projects = []
        
        for i, (repo, readme) in enumerate(repos_with_readme, 1):
            repo_name = repo['name']
            print(f"Processing {i}/{len(repos_with_readme)}: {repo_name}")
            
            # Import here to avoid loading OpenAI if not needed
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
            generate_pdf(projects)
        else:
            print("❌ No projects were successfully processed.")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 