"""
Project Kwacha - Initial Setup Script
Creates directory structure and initializes project
Week 1: Day 1-2
"""

import os
from pathlib import Path

def create_directory_structure():
    """
    Create all necessary directories for the project
    """
    print("=" * 60)
    print("PROJECT KWACHA - DIRECTORY SETUP")
    print("=" * 60)
    print("\n🗂️  Creating directory structure...\n")
    
    # Define directory structure
    directories = [
        # Data directories
        'data/raw',
        'data/processed',
        'data/synthetic',
        
        # Model directories
        'models/business_generator/checkpoints',
        'models/business_generator/config',
        'models/economic_forecaster/lstm',
        'models/economic_forecaster/xgboost',
        
        # Source code directories
        'src/data_collection',
        'src/data_processing',
        'src/training',
        'src/api/routes',
        'src/api/models',
        'src/frontend',
        
        # Notebooks
        'notebooks',
        
        # Tests
        'tests',
        
        # Documentation
        'docs',
        
        # Logs
        'logs',
        
        # Scripts
        'scripts',
    ]
    
    created = 0
    existed = 0
    
    for directory in directories:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"  ⏭️  {directory} (already exists)")
            existed += 1
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {directory}")
            created += 1
            
            # Create .gitkeep in data and model directories
            if directory.startswith(('data/', 'models/')):
                gitkeep = dir_path / '.gitkeep'
                gitkeep.touch()
    
    print(f"\n📊 Summary:")
    print(f"   • Created: {created} directories")
    print(f"   • Already existed: {existed} directories")
    print(f"   • Total: {len(directories)} directories")
    
def create_init_files():
    """
    Create __init__.py files to make directories Python packages
    """
    print("\n" + "=" * 60)
    print("CREATING PYTHON PACKAGE FILES")
    print("=" * 60)
    print("\n📦 Creating __init__.py files...\n")
    
    # Directories that should be Python packages
    package_dirs = [
        'src',
        'src/data_collection',
        'src/data_processing',
        'src/training',
        'src/api',
        'src/api/routes',
        'src/api/models',
        'src/frontend',
        'tests',
    ]
    
    created = 0
    
    for directory in package_dirs:
        init_file = Path(directory) / '__init__.py'
        if not init_file.exists():
            init_file.touch()
            print(f"  ✅ {directory}/__init__.py")
            created += 1
        else:
            print(f"  ⏭️  {directory}/__init__.py (already exists)")
    
    print(f"\n📊 Created {created} __init__.py files")

def create_env_template():
    """
    Create .env.example if it doesn't exist
    """
    print("\n" + "=" * 60)
    print("ENVIRONMENT TEMPLATE")
    print("=" * 60)
    
    env_example = Path('.env.example')
    
    if env_example.exists():
        print("\n✅ .env.example already exists")
    else:
        print("\n⚠️  .env.example not found")
        print("   Please download it from the project materials")

def create_gitignore():
    """
    Create .gitignore if it doesn't exist
    """
    print("\n" + "=" * 60)
    print("GIT IGNORE FILE")
    print("=" * 60)
    
    gitignore = Path('.gitignore')
    
    if gitignore.exists():
        print("\n✅ .gitignore already exists")
    else:
        print("\n⚠️  .gitignore not found")
        print("   Please download it from the project materials")

def check_requirements():
    """
    Check if requirements are installed
    """
    print("\n" + "=" * 60)
    print("CHECKING REQUIREMENTS")
    print("=" * 60)
    print("\n🔍 Checking installed packages...\n")
    
    required_packages = [
        'numpy',
        'pandas',
        'scikit-learn',
        'wbdata',
        'yfinance',
        'matplotlib',
        'jupyter',
        'python-dotenv'
    ]
    
    installed = []
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
            installed.append(package)
        except ImportError:
            print(f"  ❌ {package} (not installed)")
            missing.append(package)
    
    print(f"\n📊 Summary:")
    print(f"   • Installed: {len(installed)}/{len(required_packages)}")
    print(f"   • Missing: {len(missing)}")
    
    if missing:
        print("\n⚠️  Install missing packages:")
        print(f"   pip install {' '.join(missing)}")

def main():
    """
    Run complete setup
    """
    print("\n" + "🚀" * 30)
    print("PROJECT KWACHA - INITIAL SETUP")
    print("🚀" * 30 + "\n")
    
    # Create directories
    create_directory_structure()
    
    # Create __init__.py files
    create_init_files()
    
    # Check for .env.example
    create_env_template()
    
    # Check for .gitignore
    create_gitignore()
    
    # Check requirements
    check_requirements()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n✅ Project structure is ready!")
    
    print("\n📋 Next steps:")
    print("   1. Copy .env.example to .env (if not done)")
    print("   2. Copy .gitignore (if not done)")
    print("   3. Run: python src/data_collection/worldbank_collector.py")
    print("   4. Run: python src/data_collection/commodity_collector.py")
    
    print("\n💡 Quick commands:")
    print("   • Start Jupyter: jupyter notebook")
    print("   • View data: ls -lh data/raw/")
    print("   • Check git status: git status")
    
    print("\n")

if __name__ == "__main__":
    main()
