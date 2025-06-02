#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def view_api_key():
    """View current API key from .env or environment."""
    # Try .env file first
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("GROQ_API_KEY="):
                    key = line.strip().split("=", 1)[1]
                    # Mask the key for security
                    if len(key) > 8:
                        masked = key[:4] + "*" * (len(key) - 8) + key[-4:]
                    else:
                        masked = "*" * len(key)
                    print(f"Current API key (.env): {masked}")
                    return
    
    # Check environment variable
    env_key = os.environ.get("GROQ_API_KEY")
    if env_key:
        if len(env_key) > 8:
            masked = env_key[:4] + "*" * (len(env_key) - 8) + env_key[-4:]
        else:
            masked = "*" * len(env_key)
        print(f"Current API key (environment): {masked}")
    else:
        print("No API key found!")

def set_api_key(new_key):
    """Set new API key in .env file."""
    env_file = Path(".env")
    
    # Read existing content
    other_vars = []
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if not line.startswith("GROQ_API_KEY="):
                    other_vars.append(line.rstrip())
    
    # Write new content
    with open(env_file, 'w') as f:
        f.write(f"GROQ_API_KEY={new_key}\n")
        for var in other_vars:
            if var.strip():  # Only write non-empty lines
                f.write(f"{var}\n")
    
    print(f"✅ API key updated in .env file")

def remove_api_key():
    """Remove API key from .env file."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("No .env file found!")
        return
    
    # Read and filter content
    other_vars = []
    found = False
    with open(env_file) as f:
        for line in f:
            if line.startswith("GROQ_API_KEY="):
                found = True
            else:
                other_vars.append(line.rstrip())
    
    if found:
        # Write back without API key
        with open(env_file, 'w') as f:
            for var in other_vars:
                if var.strip():
                    f.write(f"{var}\n")
        print("✅ API key removed from .env file")
    else:
        print("No API key found in .env file!")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_api_key.py view     - View current API key (masked)")
        print("  python manage_api_key.py set KEY  - Set new API key")
        print("  python manage_api_key.py remove   - Remove API key")
        return
    
    command = sys.argv[1].lower()
    
    if command == "view":
        view_api_key()
    elif command == "set":
        if len(sys.argv) < 3:
            print("Please provide the new API key!")
            print("Usage: python manage_api_key.py set YOUR_NEW_KEY")
        else:
            set_api_key(sys.argv[2])
    elif command == "remove":
        remove_api_key()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()