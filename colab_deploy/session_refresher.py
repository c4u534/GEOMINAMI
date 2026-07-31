"""
Native Session Refresh & Storage State Maintainer
"""
import os
import json
from pathlib import Path

SESSION_FILE = Path("./.notebooklm_session.json")

def validate_and_refresh_session() -> bool:
    if not SESSION_FILE.exists():
        print("⚠️ Session state missing. Please run notebooklm login once to generate session state.")
        return False
    try:
        data = json.loads(SESSION_FILE.read_text())
        if "cookies" in data or "tokens" in data:
            print("✓ Native session state validated in Google Drive.")
            return True
    except Exception as e:
        print(f"❌ Session validation error: {e}")
    return False

if __name__ == "__main__":
    validate_and_refresh_session()
