"""
Setup script for MediAI - Medical Information Chatbot
Handles environment setup and dependency installation
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(number, text):
    """Print a formatted step"""
    print(f"\n[Step {number}] {text}")


def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print_step(1, "Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True


def install_dependencies():
    """Install required packages"""
    print_step(2, "Installing dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def setup_env_file():
    """Create .env file if it doesn't exist"""
    print_step(3, "Setting up .env file...")
    
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("\nYou need an OpenAI API key:")
    print("1. Go to https://platform.openai.com/api_keys")
    print("2. Create a new secret key")
    print("3. Copy the key (don't share it!)")
    
    api_key = input("\nEnter your OpenAI API key (or press Enter to skip): ").strip()
    
    if api_key:
        with open(env_file, 'w') as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print("✅ .env file created")
        return True
    else:
        print("⚠️  Skipped. You'll need to add OPENAI_API_KEY to .env later")
        return True


def create_directories():
    """Create necessary directories"""
    print_step(4, "Creating data directories...")
    
    base_dir = Path(__file__).parent
    dirs_to_create = [
        base_dir / "data",
        base_dir / "data" / "chats",
        base_dir / "data" / "embeddings",
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {dir_path.relative_to(base_dir)}")
    
    return True


def display_next_steps():
    """Display next steps"""
    print_header("Setup Complete! 🎉")
    
    print("\nNext steps:")
    print("1. Add your OpenAI API key to .env (if you skipped it)")
    print("2. Run: streamlit run app.py")
    print("3. Browser will open to http://localhost:8501")
    print("4. Start by clicking '➕ New Chat'")
    
    print("\nDocumentation:")
    print("- README.md - Full documentation")
    print("- QUICKSTART.md - Quick start guide")
    print("- CONFIG.md - Configuration options")
    
    print("\nAPI Key Setup:")
    print("- Create account: https://platform.openai.com/")
    print("- Get API key: https://platform.openai.com/api_keys")
    print("- Add to .env file: OPENAI_API_KEY=sk-...")
    
    print("\nTest it out:")
    print("- Type: 'What is diabetes?'")
    print("- Upload a PDF and ask about it")
    print("- Try a blocked question to see safety features")
    
    print("\n" + "=" * 60)
    print("  Questions? See README.md for troubleshooting")
    print("=" * 60 + "\n")


def main():
    """Main setup routine"""
    print_header("MediAI Setup")
    print("Medical Information Chatbot Setup")
    
    # Check Python
    if not check_python_version():
        print("\n❌ Setup failed")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed")
        return False
    
    # Setup .env
    if not setup_env_file():
        print("\n❌ Setup failed")
        return False
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed")
        return False
    
    # Success!
    display_next_steps()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
