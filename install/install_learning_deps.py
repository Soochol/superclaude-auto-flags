#!/usr/bin/env python3
"""
Dependency installer for SuperClaude learning system
"""

import subprocess
import sys
import os

def install_package(package_name):
    """Install a package using pip"""
    try:
        print(f"Installing {package_name}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e.stderr}")
        return False

def test_import(module_name):
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} import successful")
        return True
    except ImportError as e:
        print(f"❌ {module_name} import failed: {e}")
        return False

def main():
    print("Installing SuperClaude Learning System Dependencies")
    print("=" * 50)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Install required packages
    packages = ["numpy", "PyYAML"]
    success_count = 0
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\nInstallation Summary: {success_count}/{len(packages)} packages installed successfully")
    
    # Test imports
    print("\nTesting Learning System Module Imports")
    print("=" * 40)
    
    modules = [
        "learning_storage",
        "data_collector", 
        "learning_engine",
        "adaptive_recommender",
        "feedback_processor",
        "claude_sc_preprocessor"
    ]
    
    import_success_count = 0
    failed_modules = []
    
    for module in modules:
        if test_import(module):
            import_success_count += 1
        else:
            failed_modules.append(module)
    
    print(f"\nImport Test Summary: {import_success_count}/{len(modules)} modules imported successfully")
    
    if failed_modules:
        print(f"Failed modules: {', '.join(failed_modules)}")
        
        # Try to identify specific errors
        print("\nDetailed Error Analysis:")
        for module in failed_modules:
            try:
                __import__(module)
            except Exception as e:
                print(f"{module}: {type(e).__name__}: {e}")
    
    return len(failed_modules) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)