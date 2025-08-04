# Contributing to Alpaca CLI

Thank you for considering contributing to this project! We welcome all kinds of contributions—bug reports, feature suggestions, documentation improvements, and code.

---

## 🧰 Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/alpaca-cli.git
   cd alpaca-cli
   ```
3. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
🔐 No API keys are required during setup. The CLI will handle authentication during first-time login.

## 🛠️ How to Contribute

### 🐛 Report Bugs
- Use GitHub Issues.
- Include steps to reproduce, expected vs. actual behavior, and screenshots if helpful.

### 🌟 Suggest Features
- Open an issue with the [Feature Request] label.
- Describe the use case and potential implementation ideas.
### 🧪 Submit Code
1. Create a new branch:
  ```bash
  git checkout -b feature/your-feature-name
  ```
2. Follow the code style and testing guidelines below.
3. Push your branch and open a Pull Request against the dev branch.
4. Include a clear description of your changes.

### 🧼 Code Style & Standards
- Use Python 3.6+
- Format code with Black:
  ```bash
  black
  ```
- Use type hints and docstrings for all functions and classes.
- Write tests using pytest:
  ```bash
  pytest
  ```

💡 VSCode Formatter Setup
To automatically format your code with Black in VSCode, add the following to your ***.vscode/settings.json***:
```bash
{
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  },
  "editor.defaultFoldingRangeProvider": "ms-python.black-formatter",
  "editor.defaultFormatter": "ms-python.black-formatter"
}
```

### 🌐 Branch Strategy
- ***main***: Stable, production-ready code
- ***dev***: Active development branch
- Feature branches should be based on dev

### 🤝 Community & Support
- Ask questions or start discussions in GitHub Discussions
- Use GitHub Issues for bugs and feature requests

### 🙏 Thank You
Your contributions make this project better. Whether it's a typo fix or a major feature, we appreciate your help!
