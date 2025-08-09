#!/usr/bin/env python3
"""
Setup and Configuration Check for ATS System
Verifies installation and API key configuration
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    
    print("🔍 Checking Dependencies...")
    
    required_packages = [
        ('streamlit', 'streamlit'),
        ('pandas', 'pandas'),
        ('plotly', 'plotly'),
        ('PyPDF2', 'PyPDF2'),
        ('docx', 'python-docx'),
        ('sqlite3', 'sqlite3 (built-in)'),
    ]
    
    optional_packages = [
        ('autogen', 'pyautogen'),
        ('openai', 'openai'),
        ('anthropic', 'anthropic'),
        ('pdfplumber', 'pdfplumber'),
    ]
    
    missing_required = []
    missing_optional = []
    
    # Check required packages
    for package, pip_name in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_required.append(pip_name)
            print(f"  ❌ {package} (required)")
    
    # Check optional packages
    for package, pip_name in optional_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} (optional)")
        except ImportError:
            missing_optional.append(pip_name)
            print(f"  ⚠️  {package} (optional)")
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        print(f"Install with: pip install {' '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Missing optional packages: {', '.join(missing_optional)}")
        print(f"Install with: pip install {' '.join(missing_optional)}")
    
    return True


def check_api_configuration():
    """Check API key configuration"""
    
    print("\n🔑 Checking API Configuration...")
    
    # Check for .env file
    env_file = Path('.env')
    if env_file.exists():
        print("  ✅ .env file found")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("  ✅ .env file loaded")
        except ImportError:
            print("  ⚠️  python-dotenv not installed (install for .env support)")
    else:
        print("  ⚠️  .env file not found (will use environment variables)")
    
    # Check API keys
    api_keys = {
        'OpenAI': 'OPENAI_API_KEY',
        'Anthropic': 'ANTHROPIC_API_KEY',
        'Azure OpenAI': 'AZURE_OPENAI_API_KEY',
        'Google': 'GOOGLE_API_KEY'
    }
    
    found_keys = []
    for provider, env_var in api_keys.items():
        if os.getenv(env_var):
            found_keys.append(provider)
            print(f"  ✅ {provider} API key configured")
        else:
            print(f"  ⚪ {provider} API key not found")
    
    # Check Ollama
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    try:
        import requests
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if response.status_code == 200:
            found_keys.append("Ollama (Local)")
            print(f"  ✅ Ollama local LLM available at {ollama_url}")
    except:
        print(f"  ⚪ Ollama not available at {ollama_url}")
    
    if found_keys:
        print(f"\n🤖 LLM Mode Available with: {', '.join(found_keys)}")
        return "llm"
    else:
        print(f"\n🐍 Pure Python Mode (No API keys found)")
        return "python"


def check_file_structure():
    """Check if required directories exist"""
    
    print("\n📁 Checking File Structure...")
    
    required_dirs = [
        'src/agents',
        'src/database', 
        'src/rag',
        'streamlit_app',
        'data',
        'tests'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✅ {dir_path}/")
        else:
            missing_dirs.append(dir_path)
            print(f"  ❌ {dir_path}/ (missing)")
    
    if missing_dirs:
        print(f"\n❌ Missing directories: {', '.join(missing_dirs)}")
        print("Create with: mkdir -p " + " ".join(missing_dirs))
        return False
    
    return True


def test_system_functionality():
    """Test basic system functionality"""
    
    print("\n🧪 Testing System Functionality...")
    
    try:
        # Test configuration loading
        sys.path.append('src')
        from utils.config import get_config, is_llm_enabled
        
        config = get_config()
        print(f"  ✅ Configuration loaded")
        print(f"  📊 LLM Enabled: {is_llm_enabled()}")
        print(f"  🗄️  Database: {config.database_config.url}")
        
        # Test resume processing
        from agents.resume_processor import ResumeProcessingAgent
        from utils.config import get_autogen_config
        
        autogen_config = get_autogen_config()
        if autogen_config:
            config_list = [autogen_config]
            processor = ResumeProcessingAgent(config_list)
            print(f"  ✅ Resume processor initialized")
        else:
            print(f"  ⚠️  Resume processor: No LLM config (would use fallback)")
        
        # Test database
        from database.operations import DatabaseManager
        
        db = DatabaseManager("ats_system.db")  # Use actual database file
        session_id = db.create_session()
        print(f"  ✅ Database operations working")
        
        # Test visualization
        from agents.visualization_agent import VisualizationAgent
        
        viz = VisualizationAgent()
        print(f"  ✅ Visualization agent working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ System test failed: {e}")
        return False


def main():
    """Main setup check function"""
    
    print("🚀 ATS System Setup Check")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    if script_dir != Path.cwd():
        os.chdir(script_dir)
        print(f"📁 Working directory: {script_dir}")
    
    # Run checks
    deps_ok = check_dependencies()
    api_mode = check_api_configuration()
    structure_ok = check_file_structure()
    
    if deps_ok and structure_ok:
        system_ok = test_system_functionality()
    else:
        system_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Setup Summary")
    print("=" * 50)
    
    if deps_ok:
        print("✅ Dependencies: All required packages installed")
    else:
        print("❌ Dependencies: Missing required packages")
    
    print(f"🔑 API Mode: {api_mode.upper()}")
    
    if structure_ok:
        print("✅ File Structure: All directories present")
    else:
        print("❌ File Structure: Missing directories")
    
    if system_ok:
        print("✅ System Test: All components working")
    else:
        print("❌ System Test: Some components failed")
    
    # Final recommendations
    print("\n🎯 Next Steps:")
    
    if not deps_ok:
        print("1. Install missing packages: pip install -r requirements.txt")
    
    if api_mode == "python":
        print("2. [Optional] Add API key to .env for LLM features")
    
    if system_ok:
        print("3. Run the application: streamlit run streamlit_app/app.py")
    else:
        print("3. Fix system errors before running the application")
    
    print("\n📚 Documentation:")
    print("- README.md: Complete setup and usage guide")
    print("- .env.example: Configuration template")
    print("- docs/: Detailed documentation")


if __name__ == "__main__":
    main()
