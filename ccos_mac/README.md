# CCOS (Claude Code Open Source)

An open-source alternative to Claude Code using Perplexity AI models, designed for macOS.

## Features

- Modern, interactive CLI interface
- Project structure analysis
- File navigation and search
- Semantic code understanding
- Powered by Perplexity AI models

## System Requirements

- macOS 10.15 (Catalina) or later
- Terminal app or iTerm2
- Internet connection
- Perplexity API key

## Complete Installation Guide

1. Install Homebrew (macOS package manager):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install Xcode Command Line Tools:
```bash
xcode-select --install
```

3. Install Python and Node.js:
```bash
brew install python
brew install node@18
```

4. Install Git:
```bash
brew install git
```

5. Configure Git (replace with your details):
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

6. Clone the repository:
```bash
git clone https://github.com/bzstable/pc-mac.git
cd pc-mac
```

7. Set up Python environment:
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

8. Install Node.js dependencies:
```bash
npm install -g chalk@^5.3.0 commander@^11.0.0 boxen@^7.1.0
```

9. Set up environment variables:
```bash
# For Zsh (default on modern macOS)
echo 'export PATH="/usr/local/opt/node@18/bin:$PATH"' >> ~/.zshrc
echo 'export PPLX_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc

# OR for Bash
echo 'export PATH="/usr/local/opt/node@18/bin:$PATH"' >> ~/.bashrc
echo 'export PPLX_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

1. Start CCOS in any project directory:
```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Run the application
python3 -m ccos
```

2. Available commands:
- `ls` - List files in current directory
- `tree` - Show directory structure
- `cd <dir>` - Change directory
- `pwd` - Print working directory
- `touch <file>` - Create empty file
- `mkdir <dir>` - Create directory
- `rm <name>` - Remove file/directory
- `help` - Show all commands
- `exit` - Exit the program

## Troubleshooting

1. If you see "command not found" errors:
   - Make sure you've sourced your shell configuration: `source ~/.zshrc` or `source ~/.bashrc`
   - Verify PATH variables: `echo $PATH`
   - Check installations: `python3 --version`, `node --version`, `git --version`

2. If you see Python package errors:
   - Make sure your virtual environment is activated
   - Try reinstalling packages: `pip install -r requirements.txt --force-reinstall`

3. If you see Node.js package errors:
   - Try reinstalling global packages: `npm install -g chalk commander boxen`

4. If you can't activate virtual environment:
   - Delete the venv directory and create it again: `rm -rf venv && python3 -m venv venv`

5. If you see "python@3.8 has been disabled because it is deprecated upstream" error:
   - This README has been updated to use the latest Python version
   - Use `brew install python` instead of `brew install python@3.8`
   - Remove the Python-specific PATH export line from your shell configuration

## Development

This project is under active development. Features are being added incrementally.

## License

MIT 