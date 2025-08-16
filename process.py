import anthropic
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

def truncate_text_to_fit(pdf, text, cell_width, font_family=None, font_style=None, font_size=None):
    """Truncate text with ellipsis to fit in the given cell width for the current font settings."""
    cleaned = clean_text_for_pdf(text)
    if cell_width == 0:
        # 0 means extend up to the right margin, so we use the current page width minus margins
        cell_width = pdf.w - pdf.r_margin - pdf.x
    # Save current font
    if font_family and font_size:
        pdf.set_font(font_family, font_style or '', font_size)
    ellipsis = '...'
    max_width = cell_width
    if pdf.get_string_width(cleaned) <= max_width:
        return cleaned
    # Truncate and add ellipsis
    for i in range(len(cleaned), 0, -1):
        candidate = cleaned[:i] + ellipsis
        if pdf.get_string_width(candidate) <= max_width:
            return candidate
    # If even one char + ellipsis doesn't fit, return ellipsis only
    return ellipsis

def summarize_project(readme, code_snippets=""):
    """Summarize a project for portfolio using Anthropic Claude.
    If PORTFOLIO_NO_LLM=true, generate a heuristic summary from README without API calls.
    """
    try:
        # Heuristic/no-LLM mode for fast verification and zero-cost runs
        if str(os.getenv("PORTFOLIO_NO_LLM", "")).lower() in ("1", "true", "yes"):  
            overview = ""
            key_features = []
            technologies = []
            impact = ""

            # Clean input
            readme_text = readme or ""
            readme_text = readme_text.replace("\r\n", "\n")

            # Overview: first non-empty paragraph
            for para in readme_text.split("\n\n"):
                p = para.strip()
                if p and len(p) > 40:
                    overview = p.split("\n")[0]
                    break
            if not overview:
                overview = "This project provides utilities and code samples as described in the README."

            # Key features: look for bullet points
            for line in readme_text.split("\n"):
                ls = line.strip()
                if ls.startswith(('- ', '* ', '+ ')) and len(key_features) < 5:
                    key_features.append(ls[2:].strip())
                elif re.match(r"^\d+\.\s+", ls) and len(key_features) < 5:
                    key_features.append(re.sub(r"^\d+\.\s+", "", ls))

            # Technologies: simple keyword scan
            tech_keywords = [
                'python', 'javascript', 'typescript', 'java', 'go', 'rust', 'c++', 'c#', 'php', 'ruby',
                'react', 'next.js', 'vue', 'svelte', 'angular', 'node', 'express',
                'django', 'flask', 'fastapi', 'spring', 'rails',
                'postgresql', 'mysql', 'sqlite', 'mongodb', 'redis',
                'docker', 'kubernetes', 'aws', 'gcp', 'azure'
            ]
            lower = readme_text.lower()
            technologies = sorted({kw for kw in tech_keywords if kw in lower})[:12]
            tech_str = ", ".join(technologies) if technologies else "Not specified"

            # Impact
            impact = "Improves productivity and provides a practical solution based on the repository's goals."

            summary = (
                "**Project Overview:**\n"
                f"{overview}\n\n"
                "**Key Features:**\n" + (
                    "\n".join([f"* {f}" for f in key_features]) if key_features else "* Clear README documentation\n* Practical example code"
                ) +
                "\n\n**Technologies Used:**\n"
                f"{tech_str}\n\n"
                "**Impact & Benefits:**\n"
                f"{impact}"
            )
            return clean_text_for_pdf(summary)

        # Initialize Anthropic client only when needed
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
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
        
        response = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest"),
            max_tokens=1000,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text from Anthropic response and clean for PDF compatibility
        text = ""
        try:
            # response.content is a list of content blocks; take first text block
            for block in response.content:
                if getattr(block, "type", None) == "text" or hasattr(block, "text"):
                    text += getattr(block, "text", str(block))
            if not text and hasattr(response, "content"):  # fallback
                text = str(response.content)
        except Exception:
            text = str(response)
        return clean_text_for_pdf(text)
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def generate_pdf(projects, user_name=None):
    """Generate a beautifully formatted PDF portfolio, personalized with the user's name"""
    try:
        class PortfolioPDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 20)
                self.set_text_color(44, 62, 80)
                safe_title = truncate_text_to_fit(self, 'GitHub Portfolio', 0, 'Arial', 'B', 20)
                self.cell(0, 15, safe_title, 0, 1, 'C')
                self.set_text_color(0, 0, 0)
                self.ln(5)
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.set_text_color(128, 128, 128)
                page_str = f'Page {self.page_no()}'
                safe_page = truncate_text_to_fit(self, page_str, 0, 'Arial', 'I', 8)
                self.cell(0, 10, safe_page, 0, 0, 'C')
                self.set_text_color(0, 0, 0)
            def safe_cell(self, w, h, txt='', border=0, ln=0, align='', fill=False, font_family=None, font_style=None, font_size=None):
                try:
                    cleaned_txt = clean_text_for_pdf(str(txt))
                    # Ensure there is enough horizontal space; if not, move to next line first
                    min_char_width = self.get_string_width('W') + 0.5
                    avail_width = (self.w - self.r_margin - self.x) if w == 0 else w
                    if avail_width <= min_char_width:
                        self.ln(h or 6)
                    safe_txt = truncate_text_to_fit(self, cleaned_txt, w, font_family, font_style, font_size)
                    try:
                        self.cell(w, h, safe_txt, border, ln, align, fill)
                    except Exception as e:
                        if 'Not enough horizontal space' in str(e):
                            # Try on a new line
                            self.ln(h or 6)
                            self.cell(w, h, safe_txt, border, ln, align, fill)
                        else:
                            raise
                except Exception as e:
                    self.cell(w, h, '[Text encoding error]', border, ln, align, fill)
            def safe_multi_cell(self, w, h, txt, border=0, align='J', fill=False):
                try:
                    cleaned_txt = clean_text_for_pdf(str(txt))
                    # Ensure enough horizontal space for at least one char; if not, new line first
                    min_char_width = self.get_string_width('W') + 0.5
                    avail_width = (self.w - self.r_margin - self.x) if w == 0 else w
                    if avail_width <= min_char_width:
                        self.ln(h or 6)
                    try:
                        self.multi_cell(w, h, cleaned_txt, border, align, fill)
                    except Exception as e:
                        if 'Not enough horizontal space' in str(e):
                            # Force new line and retry once
                            self.ln(h or 6)
                            self.multi_cell(w, h, cleaned_txt, border, align, fill)
                        else:
                            raise
                except Exception as e:
                    self.multi_cell(w, h, '[Text encoding error]', border, align, fill)

        pdf = PortfolioPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        pdf.ln(30)
        pdf.set_font('Arial', 'B', 28)
        pdf.set_text_color(44, 62, 80)
        pdf.safe_cell(0, 20, 'GitHub Portfolio', 0, 1, 'C', font_family='Arial', font_style='B', font_size=28)
        pdf.set_font('Arial', 'I', 16)
        pdf.set_text_color(52, 73, 94)
        pdf.safe_cell(0, 15, 'Project Showcase & Technical Summary', 0, 1, 'C', font_family='Arial', font_style='I', font_size=16)
        # Add user's name if provided
        if user_name:
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 18)
            pdf.set_text_color(39, 174, 96)  # Green accent
            pdf.safe_cell(0, 12, f'Prepared for: {user_name}', 0, 1, 'C', font_family='Arial', font_style='B', font_size=18)
        from datetime import datetime
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(128, 128, 128)
        pdf.ln(20)
        pdf.safe_cell(0, 10, f'Generated on {datetime.now().strftime("%B %d, %Y")}', 0, 1, 'C', font_family='Arial', font_size=12)
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(44, 62, 80)
        pdf.ln(10)
        pdf.safe_cell(0, 10, f'Featuring {len(projects)} Projects', 0, 1, 'C', font_family='Arial', font_style='B', font_size=14)
        pdf.set_text_color(0, 0, 0)
        for i, project in enumerate(projects, 1):
            pdf.add_page()
            pdf.set_font('Arial', 'B', 24)
            pdf.set_text_color(231, 76, 60)
            pdf.safe_cell(0, 15, f"Project {i}", 0, 1, 'L', font_family='Arial', font_style='B', font_size=24)
            pdf.set_font('Arial', 'B', 20)
            pdf.set_text_color(44, 62, 80)
            pdf.safe_cell(0, 12, project['title'], 0, 1, 'L', font_family='Arial', font_style='B', font_size=20)
            pdf.set_fill_color(52, 152, 219)
            pdf.rect(10, pdf.get_y(), 190, 1, 'F')
            pdf.ln(8)
            summary = clean_text_for_pdf(project['summary'])
            sections = summary.split('**')
            pdf.set_text_color(0, 0, 0)
            for j, section in enumerate(sections):
                if not section.strip():
                    continue
                if ':' in section and j % 2 == 1:
                    pdf.set_font('Arial', 'B', 14)
                    pdf.set_text_color(44, 62, 80)
                    pdf.ln(3)
                    pdf.safe_cell(0, 8, section.strip(), 0, 1, 'L', font_family='Arial', font_style='B', font_size=14)
                    pdf.ln(2)
                else:
                    pdf.set_font('Arial', '', 11)
                    pdf.set_text_color(0, 0, 0)
                    lines = section.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('*'):
                            pdf.set_font('Arial', '', 10)
                            pdf.set_text_color(52, 73, 94)
                            pdf.cell(5, 6, '', 0, 0)
                            pdf.safe_multi_cell(0, 6, line)
                        elif line:
                            pdf.set_font('Arial', '', 11)
                            pdf.set_text_color(0, 0, 0)
                            pdf.safe_multi_cell(0, 6, line)
                            pdf.ln(2)
            pdf.ln(5)
        pdf.output("GitHub_Portfolio.pdf")
        print("✨ Beautiful PDF portfolio generated successfully: GitHub_Portfolio.pdf")
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")