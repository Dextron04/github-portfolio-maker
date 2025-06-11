# GitHub Portfolio Generator

🚀 **Automatically generate a beautiful PDF portfolio from your GitHub repositories using AI**

Transform your GitHub repositories into a professional portfolio document with AI-generated summaries, beautiful formatting, and comprehensive project descriptions.

## ✨ Features

- 🤖 **AI-Powered Summaries**: Uses OpenAI GPT-4 to create compelling project descriptions
- 📄 **Beautiful PDF Generation**: Professional, multi-colored portfolio with modern design
- 🔍 **Smart Repository Detection**: Automatically finds all your repositories with READMEs
- 💰 **Cost-Efficient**: Pre-flight checks prevent wasted API calls
- 🛡️ **Error Prevention**: Comprehensive testing before expensive operations
- 🎨 **Professional Formatting**: Cover page, headers, footers, and structured layouts
- 📊 **Progress Tracking**: Real-time feedback on processing status
- 🧹 **Automatic Cleanup**: Handles encoding issues and text formatting

## 🏗️ Project Structure

```
github-portfolio-maker/
├── main.py              # GitHub API interactions
├── process.py           # AI processing and PDF generation
├── run.py              # Main execution script with pre-flight checks
├── requirements.txt     # Python dependencies
├── .env.local          # Environment variables (create this)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 📋 Prerequisites

- **Python 3.7+**
- **GitHub Personal Access Token**
- **OpenAI API Key**

## 🚀 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/github-portfolio-maker.git
   cd github-portfolio-maker
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env.local` file in the project root:

   ```bash
   touch .env.local
   ```

   Add your API keys to `.env.local`:

   ```
   GITHUB_TOKEN=ghp_your_github_token_here
   OPENAI_API_KEY=sk-your_openai_api_key_here
   ```

## 🔑 Getting API Keys

### GitHub Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (for private repos) or `public_repo` (for public only)
4. Copy the generated token

### OpenAI API Key

1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)

## 🎯 Usage

### Basic Usage

```bash
python run.py
```

### What Happens:

1. **Pre-flight Check**: Tests PDF creation capabilities
2. **Repository Discovery**: Finds all your GitHub repositories
3. **README Detection**: Identifies repos with documentation
4. **Cost Estimation**: Shows how many AI calls will be made
5. **User Confirmation**: Asks permission before expensive operations
6. **AI Processing**: Generates summaries for each project
7. **PDF Creation**: Builds your professional portfolio

### Example Output:

```
🔧 Running pre-flight PDF test...
✅ PDF test passed! Test file size: 1247 bytes
🗑️ Test file cleaned up

🚀 Starting GitHub portfolio generation...
Found 25 repositories

📋 Checking repositories for READMEs...
Checking 1/25: my-awesome-project ✅
Checking 2/25: old-experiment ⚠️ (No README found)

💰 Found 8 repositories with READMEs.
This will make 8 LLM calls.
Continue with 8 LLM calls? (y/N): y

🤖 Processing 8 repositories with LLM...
Processing 1/8: my-awesome-project
  🤖 Generating AI summary...
  ✅ Summary generated successfully

📄 Generating final PDF portfolio...
✨ Beautiful PDF portfolio generated successfully: GitHub_Portfolio.pdf
```

## 📊 Generated Portfolio Features

Your PDF portfolio will include:

- **🎨 Professional Cover Page**

  - Project title and subtitle
  - Generation date
  - Total project count

- **📑 Individual Project Pages**

  - Project numbering and titles
  - Colored section headers
  - Structured summaries with:
    - Project Overview
    - Key Features (bulleted)
    - Technologies Used
    - Impact & Benefits

- **🎯 Professional Styling**
  - Multi-color design scheme
  - Page headers and footers
  - Proper typography hierarchy
  - Clean bullet point formatting

## 🛠️ Troubleshooting

### Common Issues

#### Missing Environment Variables

```
❌ Error: Missing required environment variables: GITHUB_TOKEN, OPENAI_API_KEY
```

**Solution**: Create `.env.local` file with your API keys

#### PDF Creation Failed

```
❌ PDF test failed: 'latin-1' codec can't encode character
```

**Solution**: The pre-flight check should catch this. If it persists, check your Python/FPDF installation

#### No Repositories Found

```
❌ No repositories with READMEs found. Nothing to generate.
```

**Solution**: Add README files to your repositories or check your GitHub token permissions

#### OpenAI API Errors

```
Error generating summary: The api_key client option must be set
```

**Solution**: Verify your `OPENAI_API_KEY` in `.env.local`

### Rate Limits

- **GitHub API**: 5,000 requests/hour (authenticated)
- **OpenAI API**: Depends on your plan and model usage

## 💰 Cost Considerations

- **GitHub API**: Free (within rate limits)
- **OpenAI API**: ~$0.01-0.03 per repository (GPT-4 pricing)
- **Example**: 10 repositories ≈ $0.10-0.30

The script shows exactly how many API calls will be made and asks for confirmation.

## 🔧 Configuration

### Customize PDF Styling

Edit `process.py` to modify:

- Colors (RGB values)
- Fonts and sizes
- Layout and spacing
- Section formatting

### Modify AI Prompts

Edit the prompt in `summarize_project()` function in `process.py` to change how projects are described.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 API
- **GitHub** for repository API
- **FPDF** for PDF generation
- **python-dotenv** for environment management

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your API keys and permissions
3. Run the pre-flight test to isolate PDF issues
4. Open an issue with error details and environment info

---

**Made with ❤️ for developers who want to showcase their work professionally**
