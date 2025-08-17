#!/usr/bin/env python3
"""
TEF AI Practice Tool - Startup Script
This script provides a user-friendly way to start the FastAPI application
"""

import os
import sys
import uvicorn
from pathlib import Path
from config import settings

def check_dependencies():
    """Check if required Python packages are installed."""
    required_packages = [
        'fastapi',
        'google.genai',
        'sqlalchemy',
        'passlib',
        'python-jose',
        'python-multipart'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'google.genai':
                import google.genai
            elif package == 'python-jose':
                import jose
            elif package == 'python-multipart':
                import multipart
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_environment():
    """Check environment variables and provide helpful information."""
    print("\n🔧 Environment Check:")
    
    # Check Gemini API configuration
    if settings.google_api_key:
        print("✅ Gemini API Key is configured")
    else:
        print("⚠️  GOOGLE_API_KEY not set - using development mode")
        print("   Set this environment variable to use Gemini AI services")
    
    # Check security configuration
    if settings.secret_key and settings.secret_key != "your-secret-key-change-this-in-production":
        print("✅ SECRET_KEY is configured")
    else:
        print("⚠️  SECRET_KEY not set or using default - set a secure key in production")
    
    # Check database configuration
    if settings.database_url != "sqlite:///./tef_evaluator.db":
        print(f"✅ Database URL: {settings.database_url}")
    else:
        print("✅ Using default SQLite database: ./tef_evaluator.db")

def main():
    print("🚀 Starting TEF AI Practice Tool...")
    print("=" * 50)
    
    if not check_dependencies():
        sys.exit(1)
    
    check_environment()
    
    print("\n📁 Project Structure:")
    project_root = Path(__file__).parent
    print(f"   Root: {project_root}")
    
    # Check for key files
    key_files = ['main.py', 'models.py', 'auth.py', 'prompt.py', 'index.html']
    for file in key_files:
        if (project_root / file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")
    
    print("\n🌐 Server Information:")
    print(f"   URL: http://{settings.host}:{settings.port}")
    print(f"   API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"   ReDoc: http://{settings.host}:{settings.port}/redoc")
    
    print("\n🔐 Authentication:")
    print("   Default test user: testing / testing")
    print(f"   Register new users at: http://{settings.host}:{settings.port}")
    
    print("\n" + "=" * 50)
    print("Starting server...")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
