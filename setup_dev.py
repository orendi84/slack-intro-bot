#!/usr/bin/env python3
"""
Development Environment Setup Script

Sets up the development environment for Slack Intro Bot with all necessary tools,
dependencies, and configurations.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python 3.7+ required, found {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def setup_virtual_environment():
    """Set up virtual environment"""
    if os.path.exists('venv'):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install project dependencies"""
    # Determine pip command based on platform
    pip_cmd = "venv/bin/pip" if platform.system() != "Windows" else "venv\\Scripts\\pip"
    
    commands = [
        (f"{pip_cmd} install --upgrade pip", "Upgrading pip"),
        (f"{pip_cmd} install -r requirements.txt", "Installing dependencies"),
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
    
    return success

def setup_pre_commit():
    """Set up pre-commit hooks"""
    pre_commit_config = """
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 22.12.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=120, --ignore=E501,W503]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.991
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
"""
    
    with open('.pre-commit-config.yaml', 'w') as f:
        f.write(pre_commit_config.strip())
    
    print("✅ Pre-commit configuration created")
    
    # Install pre-commit hooks
    hook_cmd = "venv/bin/pre-commit" if platform.system() != "Windows" else "venv\\Scripts\\pre-commit"
    return run_command(f"{hook_cmd} install", "Installing pre-commit hooks")

def create_env_template():
    """Create .env template file"""
    env_template = """# Slack Intro Bot Configuration
# Copy this file to .env and update with your values

# Welcome message template
WELCOME_MESSAGE_TEMPLATE=Aloha {first_name}!\\n\\nWelcome to Lenny's podcast community!\\n\\nHave a wonderful day!

# Slack configuration
SLACK_CHANNEL=intros
SLACK_SEARCH_LIMIT=100
SLACK_PROFILE_TIMEOUT=30
SLACK_FALLBACK_TIMEOUT=45
SLACK_SAFE_TIMEOUT=60

# Output configuration
OUTPUT_DIRECTORY=welcome_messages
OUTPUT_PERMISSIONS=0o600
DATE_FORMAT=%Y-%m-%d
FILENAME_TEMPLATE=daily_intros_{date}.md

# Logging configuration
LOG_LEVEL=INFO
ENABLE_EMOJI_LOGGING=true
LOG_FILE=

# Welcome message configuration
FALLBACK_NAME=there
MAX_NAME_LENGTH=50
"""
    
    if not os.path.exists('.env'):
        with open('.env.template', 'w') as f:
            f.write(env_template.strip())
        print("✅ .env.template created - copy to .env and customize")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = [
        'welcome_messages',
        'logs',
        'tests',
        '.github/workflows'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def run_initial_tests():
    """Run initial tests to verify setup"""
    print("🧪 Running initial tests...")
    
    # Activate virtual environment and run tests
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
        python_cmd = "venv\\Scripts\\python"
    else:
        activate_cmd = "source venv/bin/activate"
        python_cmd = "venv/bin/python"
    
    # Test configuration
    test_config_cmd = f"{python_cmd} -c \"from config import get_config; print('✅ Config system working')\""
    if not run_command(test_config_cmd, "Testing configuration system"):
        return False
    
    # Test imports
    test_imports_cmd = f"{python_cmd} -c \"import daily_intros, user_profile_search, mcp_adapter; print('✅ All modules import successfully')\""
    if not run_command(test_imports_cmd, "Testing module imports"):
        return False
    
    print("✅ Initial tests passed")
    return True

def print_next_steps():
    """Print next steps for development"""
    print("\n" + "="*60)
    print("🎉 Development Environment Setup Complete!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Copy .env.template to .env and customize your settings")
    print("2. Activate virtual environment:")
    
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("3. Run tests:")
    print("   python run_tests.py")
    print("4. Run with coverage:")
    print("   python run_tests.py coverage")
    print("5. Start developing!")
    
    print("\n🛠️  Available Commands:")
    print("   python run_tests.py          # Run all tests")
    print("   python run_tests.py coverage # Run with coverage")
    print("   python run_tests.py lint     # Run linting")
    print("   python run_tests.py all      # Run linting + tests")
    print("   python daily_intros.py       # Run main application")
    
    print("\n📚 Documentation:")
    print("   README.md                    # Human-readable guide")
    print("   PROJECT_OVERVIEW.md          # LLM-optimized docs")
    
    print("\n🔧 IDE Setup:")
    print("   - Install Python extension")
    print("   - Select virtual environment interpreter")
    print("   - Enable pre-commit hooks")

def main():
    """Main setup function"""
    print("🚀 Setting up Slack Intro Bot Development Environment")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Set up virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to set up virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Set up pre-commit hooks
    if not setup_pre_commit():
        print("⚠️  Pre-commit setup failed, but continuing...")
    
    # Create environment template
    create_env_template()
    
    # Run initial tests
    if not run_initial_tests():
        print("❌ Initial tests failed")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
