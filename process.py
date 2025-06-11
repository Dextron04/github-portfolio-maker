from openai import OpenAI
import os
from main import fetch_readme, get_user_repos
from fpdf import FPDF
import re

def clean_text_for_pdf(text):
    """Clean text to be compatible with PDF encoding"""
    # Replace Unicode bullet points with ASCII alternatives
    text = text.replace('•', '* ')
    text = text.replace('–', '-')
    text = text.replace('—', '-')
    text = text.replace('"', '"')
    text = text.replace('"', '"')
    text = text.replace(''', "'")
    text = text.replace(''', "'")
    
    # Remove or replace other problematic Unicode characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    
    return text

def summarize_project(readme, code_snippets=""):
    """Summarize a project for portfolio using OpenAI"""
    try:
        # Initialize OpenAI client only when needed
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""
        Create a professional portfolio summary for this project. Format your response with clear sections:

        **Project Overview:**
        [Write a compelling 2-3 sentence description of what this project does and its main purpose]

        **Key Features:**
        * [List 3-5 main features or capabilities, each as a bullet point]
        * [Each feature should be concise but descriptive]
        * [Focus on the most impressive or unique aspects]

        **Technologies Used:**
        [List the main technologies, frameworks, languages, and tools used - keep it concise]

        **Impact & Benefits:**
        [1-2 sentences about the value this project provides or problems it solves]

        README Content:
        {readme}

        Sample Code:
        {code_snippets[:1000]}

        Keep the response professional, engaging, and formatted exactly as shown above with the section headers and bullet points.
        Use only ASCII characters and avoid special Unicode symbols.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Clean the response text for PDF compatibility
        return clean_text_for_pdf(response.choices[0].message.content)
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def generate_pdf(projects):
    """Generate a beautifully formatted PDF portfolio"""
    try:
        class PortfolioPDF(FPDF):
            def header(self):
                # Add a header to each page
                self.set_font('Arial', 'B', 20)
                self.set_text_color(44, 62, 80)  # Dark blue
                self.cell(0, 15, 'GitHub Portfolio', 0, 1, 'C')
                self.set_text_color(0, 0, 0)  # Reset to black
                self.ln(5)
            
            def footer(self):
                # Add page numbers
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.set_text_color(128, 128, 128)  # Gray
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
                self.set_text_color(0, 0, 0)  # Reset to black
            
            def safe_cell(self, w, h, txt='', border=0, ln=0, align='', fill=False):
                """Safe cell method that handles encoding"""
                try:
                    cleaned_txt = clean_text_for_pdf(str(txt))
                    self.cell(w, h, cleaned_txt, border, ln, align, fill)
                except:
                    # Fallback for any remaining encoding issues
                    self.cell(w, h, '[Text encoding error]', border, ln, align, fill)
            
            def safe_multi_cell(self, w, h, txt, border=0, align='J', fill=False):
                """Safe multi_cell method that handles encoding"""
                try:
                    cleaned_txt = clean_text_for_pdf(str(txt))
                    self.multi_cell(w, h, cleaned_txt, border, align, fill)
                except:
                    # Fallback for any remaining encoding issues
                    self.multi_cell(w, h, '[Text encoding error]', border, align, fill)

        pdf = PortfolioPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        
        # Add cover page
        pdf.add_page()
        pdf.ln(30)
        
        # Title
        pdf.set_font('Arial', 'B', 28)
        pdf.set_text_color(44, 62, 80)  # Dark blue
        pdf.safe_cell(0, 20, 'GitHub Portfolio', 0, 1, 'C')
        
        # Subtitle
        pdf.set_font('Arial', 'I', 16)
        pdf.set_text_color(52, 73, 94)  # Lighter blue
        pdf.safe_cell(0, 15, 'Project Showcase & Technical Summary', 0, 1, 'C')
        
        # Date
        from datetime import datetime
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(128, 128, 128)  # Gray
        pdf.ln(20)
        pdf.safe_cell(0, 10, f'Generated on {datetime.now().strftime("%B %d, %Y")}', 0, 1, 'C')
        
        # Project count
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(44, 62, 80)
        pdf.ln(10)
        pdf.safe_cell(0, 10, f'Featuring {len(projects)} Projects', 0, 1, 'C')
        
        # Reset colors
        pdf.set_text_color(0, 0, 0)
        
        # Add projects
        for i, project in enumerate(projects, 1):
            pdf.add_page()
            
            # Project number and title
            pdf.set_font('Arial', 'B', 24)
            pdf.set_text_color(231, 76, 60)  # Red accent
            pdf.safe_cell(0, 15, f"Project {i}", 0, 1, 'L')
            
            pdf.set_font('Arial', 'B', 20)
            pdf.set_text_color(44, 62, 80)  # Dark blue
            pdf.safe_cell(0, 12, project['title'], 0, 1, 'L')
            
            # Add a colored line under the title
            pdf.set_fill_color(52, 152, 219)  # Blue
            pdf.rect(10, pdf.get_y(), 190, 1, 'F')
            pdf.ln(8)
            
            # Project summary with better formatting
            summary = clean_text_for_pdf(project['summary'])
            
            # Split summary into sections and format each differently
            sections = summary.split('**')
            
            pdf.set_text_color(0, 0, 0)  # Black text
            
            for j, section in enumerate(sections):
                if not section.strip():
                    continue
                    
                if ':' in section and j % 2 == 1:  # This is a header
                    pdf.set_font('Arial', 'B', 14)
                    pdf.set_text_color(44, 62, 80)  # Dark blue
                    pdf.ln(3)
                    pdf.safe_cell(0, 8, section.strip(), 0, 1, 'L')
                    pdf.ln(2)
                else:  # This is content
                    pdf.set_font('Arial', '', 11)
                    pdf.set_text_color(0, 0, 0)  # Black
                    
                    # Handle bullet points
                    lines = section.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('*'):
                            pdf.set_font('Arial', '', 10)
                            pdf.set_text_color(52, 73, 94)  # Darker gray
                            # Add some indentation for bullet points
                            pdf.cell(5, 6, '', 0, 0)  # Indent
                            pdf.safe_multi_cell(0, 6, line)
                        elif line:
                            pdf.set_font('Arial', '', 11)
                            pdf.set_text_color(0, 0, 0)
                            pdf.safe_multi_cell(0, 6, line)
                            pdf.ln(2)
            
            # Add some space before next project
            pdf.ln(5)
        
        # Generate the PDF
        pdf.output("GitHub_Portfolio.pdf")
        print("✨ Beautiful PDF portfolio generated successfully: GitHub_Portfolio.pdf")
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")