#!/usr/bin/env python3
"""
Project validation script for Raphael AI
Checks if all required files and configurations are in place
"""

import os
import json
import sys
from pathlib import Path

def check_file_exists(file_path, required=True):
    """Check if a file exists and return status"""
    exists = os.path.exists(file_path)
    status = "✅" if exists else ("❌" if required else "⚠️")
    print(f"{status} {file_path}")
    return exists

def check_project_structure():
    """Validate project structure"""
    print("🔍 Checking project structure...")
    
    required_files = [
        "firebase.json",
        "firestore.rules",
        "functions/main.py",
        "functions/requirements.txt",
        "functions/.env.example",
        "public/src/App.js",
        "public/src/firebase.js",
        "public/package.json",
        "README.md"
    ]
    
    optional_files = [
        "functions/.env",
        "DEPLOYMENT.md",
        "CONTRIBUTING.md"
    ]
    
    all_required_exist = True
    
    print("\nRequired files:")
    for file_path in required_files:
        if not check_file_exists(file_path, required=True):
            all_required_exist = False
    
    print("\nOptional files:")
    for file_path in optional_files:
        check_file_exists(file_path, required=False)
    
    return all_required_exist

def check_firebase_config():
    """Check Firebase configuration"""
    print("\n🔥 Checking Firebase configuration...")
    
    try:
        with open('firebase.json', 'r') as f:
            config = json.load(f)
        
        required_sections = ['hosting', 'functions', 'firestore', 'emulators']
        
        for section in required_sections:
            if section in config:
                print(f"✅ {section} configured")
            else:
                print(f"❌ {section} missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error reading firebase.json: {e}")
        return False

def check_dependencies():
    """Check if all dependencies are properly defined"""
    print("\n📦 Checking dependencies...")
    
    # Check Python requirements
    try:
        with open('functions/requirements.txt', 'r') as f:
            requirements = f.read()
        
        required_packages = [
            'Flask', 'Flask-CORS', 'python-dotenv', 
            'google-generativeai', 'firebase-admin', 
            'google-cloud-firestore', 'functions-framework'
        ]
        
        for package in required_packages:
            if package.lower() in requirements.lower():
                print(f"✅ {package}")
            else:
                print(f"❌ {package} missing")
                
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
    
    # Check React dependencies
    try:
        with open('public/package.json', 'r') as f:
            package_json = json.load(f)
        
        required_deps = ['react', 'react-dom', 'firebase']
        dependencies = package_json.get('dependencies', {})
        
        for dep in required_deps:
            if dep in dependencies:
                print(f"✅ {dep}")
            else:
                print(f"❌ {dep} missing")
                
    except Exception as e:
        print(f"❌ Error reading public/package.json: {e}")

def check_environment():
    """Check environment configuration"""
    print("\n🌍 Checking environment setup...")
    
    env_example_exists = os.path.exists('functions/.env.example')
    env_exists = os.path.exists('functions/.env')
    
    if env_example_exists:
        print("✅ .env.example template exists")
    else:
        print("❌ .env.example missing")
    
    if env_exists:
        print("✅ .env file exists (check your API keys)")
    else:
        print("⚠️  .env file not found (copy from .env.example)")

def main():
    """Main validation function"""
    print("🚀 Raphael AI Project Validation")
    print("=" * 40)
    
    os.chdir(Path(__file__).parent)
    
    checks = [
        check_project_structure(),
        check_firebase_config(),
        check_environment()
    ]
    
    check_dependencies()
    
    print("\n" + "=" * 40)
    
    if all(checks):
        print("🎉 Project validation successful!")
        print("✅ All required files and configurations are present")
        print("🚀 Ready for development and deployment")
        return 0
    else:
        print("❌ Project validation failed!")
        print("🔧 Please fix the issues above before proceeding")
        return 1

if __name__ == "__main__":
    sys.exit(main())
