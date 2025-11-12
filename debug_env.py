#!/usr/bin/env python3
"""
Debug script to verify environment variable loading for API key configuration
"""

import os
import sys
from pathlib import Path

def debug_environment():
    """Debug environment variable loading and API key configuration"""

    print("=== Environment Debug ===")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")

    # Find project root
    project_root = Path(__file__).parent
    print(f"Project root: {project_root}")

    # Check .env file existence
    env_file = project_root / ".env"
    print(f".env file exists: {env_file.exists()}")
    print(f".env file path: {env_file.absolute()}")

    if env_file.exists():
        print("\n=== .env File Contents ===")
        with open(env_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip() and not line.strip().startswith('#'):
                    print(f"Line {line_num}: {line.strip()}")

    print("\n=== Environment Variables ===")

    # Check for common API key variable names
    api_key_vars = [
        "ANTHROPIC_API_KEY",
        "CLAUDE_API_KEY",
        "API_KEY",
        "ANTHROPIC_KEY",
        "CLAUDE_KEY"
    ]

    for var in api_key_vars:
        value = os.getenv(var)
        if value:
            # Don't print the full key for security
            masked = value[:8] + "*" * (len(value) - 8) if len(value) > 8 else "*" * len(value)
            print(f"[OK] {var}: {masked}")
        else:
            print(f"[ERROR] {var}: Not found")

    # Check other important config variables
    other_vars = ["PYTHONPATH", "PATH", "VIRTUAL_ENV"]
    for var in other_vars:
        value = os.getenv(var)
        if value:
            print(f"  {var}: {value[:50]}{'...' if len(value) > 50 else ''}")
        else:
            print(f"  {var}: Not found")

    print("\n=== Try Loading .env ===")

    # Try different .env loading methods
    try:
        import dotenv
        print(f"python-dotenv version: {dotenv.__version__}")

        # Method 1: From project root
        dotenv.load_dotenv(env_file)
        print("[OK] dotenv.load_dotenv(project_root / '.env') succeeded")
    except Exception as e:
        print(f"[ERROR] dotenv.load_dotenv(project_root / '.env') failed: {e}")

    try:
        # Method 2: From current directory
        dotenv.load_dotenv()
        print("[OK] dotenv.load_dotenv() from current dir succeeded")
    except Exception as e:
        print(f"[ERROR] dotenv.load_dotenv() from current dir failed: {e}")

    # Check again after loading
    print("\n=== After Loading .env ===")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        masked = api_key[:8] + "*" * (len(api_key) - 8) if len(api_key) > 8 else "*" * len(api_key)
        print(f"[OK] ANTHROPIC_API_KEY after load: {masked}")

        # Basic validation
        if len(api_key) < 20:
            print("[WARNING] API key seems too short")
        elif not any(c.isalpha() for c in api_key):
            print("[WARNING] API key format may be incorrect")
    else:
        print("[ERROR] ANTHROPIC_API_KEY still not found after load attempts")

    print("\n=== Test Configuration Import ===")

    try:
        # Test if we can import config
        sys.path.insert(0, str(project_root))
        from src.config import Config
        print("[OK] Successfully imported config")
        print(f"  Session gap hours: {Config.SESSION_GAP_HOURS}")
        print(f"  Default commit limit: {Config.DEFAULT_COMMIT_LIMIT}")
        print(f"  Output directory: {Config.OUTPUT_DIR}")
    except Exception as e:
        print(f"[ERROR] Failed to import config: {e}")
        return False

    return True

if __name__ == "__main__":
    success = debug_environment()
    if not success:
        sys.exit(1)