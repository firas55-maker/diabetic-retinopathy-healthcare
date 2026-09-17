#!/usr/bin/env python3
"""
Startup Configuration Check for Healthcare Chat Widget
Verifies that GEMINI_API_KEY is properly configured before running the app
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_gemini_configuration():
    """Check if Gemini API key is properly configured"""

    # Load environment variables
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)

    gemini_key = os.getenv('GEMINI_API_KEY', '').strip()

    print("\n" + "="*80)
    print("🚀 HEALTHCARE CHAT WIDGET - CONFIGURATION CHECK")
    print("="*80)

    # Check if .env exists
    if not env_file.exists():
        print("\n❌ ERROR: .env file not found!")
        print(f"   Expected location: {env_file}")
        return False

    print(f"\n✓ .env file found at: {env_file}")

    # Check if API key is set to placeholder
    if not gemini_key or gemini_key == 'your_actual_gemini_api_key_here':
        print("\n⚠️  WARNING: GEMINI_API_KEY not configured!")
        print("\n" + "-"*80)
        print("IMPORTANT: Before testing the chat widget, you MUST:")
        print("-"*80)
        print("\n1. Get your FREE Gemini API key:")
        print("   → Visit: https://aistudio.google.com/app/apikey")
        print("   → Sign in with your Google account")
        print("   → Click 'Create API Key' button")
        print("   → Copy the generated API key")
        print("\n2. Update your .env file:")
        print(f"   → Open: {env_file}")
        print("   → Find: GEMINI_API_KEY=your_actual_gemini_api_key_here")
        print("   → Replace with: GEMINI_API_KEY=<YOUR_ACTUAL_KEY>")
        print("   → Save the file")
        print("\n3. Restart the backend server:")
        print("   → Stop the current backend process (Ctrl+C)")
        print("   → Run: python -m uvicorn backend.main:app --reload")
        print("\n" + "-"*80)
        print("\n📝 NOTE: The chat widget will display a configuration error")
        print("   until you set a valid API key.")
        print("\n" + "="*80 + "\n")
        return False

    print(f"\n✓ GEMINI_API_KEY is configured")
    print(f"  Key preview: {gemini_key[:10]}...{gemini_key[-5:]}")

    # Check knowledge base
    knowledge_file = Path(__file__).parent / 'backend' / 'knowledge' / 'diabetes_education.txt'
    if knowledge_file.exists():
        file_size = knowledge_file.stat().st_size
        print(f"\n✓ Knowledge base found: {file_size:,} bytes")
    else:
        print(f"\n⚠️  Knowledge base not found at: {knowledge_file}")
        print("   The chat widget will still work but without knowledge base context")

    print("\n" + "="*80)
    print("✅ Configuration looks good! Ready to start the backend.")
    print("="*80 + "\n")
    return True

if __name__ == '__main__':
    check_gemini_configuration()
