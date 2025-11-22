#!/usr/bin/env python3
"""
Installation verification script
Tests all components of the AI Hybrid Development Pipeline
"""
import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("🐍 Python Version Check:")
    version = sys.version_info
    if version >= (3, 10):
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (3.10+ required)")
        return False
    return True

def check_dependencies():
    """Check required dependencies"""
    print("\n📦 Dependencies Check:")
    dependencies = [
        ("cryptography", "Cryptography library"),
        ("yaml", "PyYAML"),
        ("requests", "Requests library"),
    ]
    
    all_good = True
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"  ✅ {display_name}")
        except ImportError:
            print(f"  ❌ {display_name} not installed")
            all_good = False
    
    # Check for tomli on Python < 3.11
    if sys.version_info < (3, 11):
        try:
            import tomli
            print(f"  ✅ tomli (for Python < 3.11)")
        except ImportError:
            print(f"  ❌ tomli not installed (required for Python < 3.11)")
            all_good = False
    
    return all_good

def check_ai_sdks():
    """Check AI provider SDKs"""
    print("\n🤖 AI SDKs Check:")
    sdks = [
        ("openai", "OpenAI SDK"),
        ("google.generativeai", "Google Gemini SDK"),
        ("anthropic", "Anthropic Claude SDK"),
    ]
    
    for module_name, display_name in sdks:
        try:
            if module_name == "google.generativeai":
                import google.generativeai
            else:
                __import__(module_name)
            print(f"  ✅ {display_name}")
        except ImportError:
            print(f"  ⚠️  {display_name} not installed (optional)")
    
    return True

def check_directories():
    """Check required directories"""
    print("\n📁 Directory Structure Check:")
    directories = [
        "tools",
        "docs/specs",
        "src",
        ".ai_artifacts",
        "keys",
        "tests",
    ]
    
    all_good = True
    for dir_path in directories:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} missing")
            all_good = False
    
    return all_good

def check_keys():
    """Check RSA keys"""
    print("\n🔑 RSA Keys Check:")
    keys = [
        ("keys/dev_private.pem", "Private key"),
        ("keys/dev_public.pem", "Public key"),
    ]
    
    all_good = True
    for key_path, display_name in keys:
        path = Path(key_path)
        if path.exists():
            print(f"  ✅ {display_name}")
        else:
            print(f"  ❌ {display_name} missing")
            all_good = False
    
    return all_good

def check_tools():
    """Check tool scripts"""
    print("\n🔧 Tools Check:")
    tools = [
        "tools/ai_toolkit.py",
        "tools/model_adapter.py",
        "tools/model_adapter_v2.py",
        "tools/claude_wrapper.py",
        "tools/policy.yaml",
    ]
    
    all_good = True
    for tool_path in tools:
        path = Path(tool_path)
        if path.exists():
            print(f"  ✅ {tool_path}")
        else:
            print(f"  ⚠️  {tool_path} missing")
    
    return True

def check_api_keys():
    """Check API keys configuration"""
    print("\n🔐 API Keys Configuration:")
    keys_to_check = [
        ("OPENAI_API_KEY", "OpenAI"),
        ("GOOGLE_API_KEY", "Google Gemini"),
        ("ANTHROPIC_API_KEY", "Anthropic Claude"),
        ("AI_ARTIFACT_SIGNING_KEY", "Artifact Signing"),
    ]
    
    for env_var, display_name in keys_to_check:
        value = os.environ.get(env_var)
        if value:
            # Hide actual key values for security
            if "API_KEY" in env_var:
                masked = value[:8] + "..." if len(value) > 8 else "***"
                print(f"  ✅ {display_name}: {masked}")
            else:
                print(f"  ✅ {display_name}: {value}")
        else:
            if "API_KEY" in env_var and env_var != "AI_ARTIFACT_SIGNING_KEY":
                print(f"  ⚠️  {display_name}: Not set (optional)")
            else:
                print(f"  ❌ {display_name}: Not set")
    
    return True

def main():
    """Run all checks"""
    print("=" * 50)
    print("🚀 AI Hybrid Development Pipeline - Installation Check")
    print("=" * 50)
    
    results = [
        check_python_version(),
        check_dependencies(),
        check_ai_sdks(),
        check_directories(),
        check_keys(),
        check_tools(),
        check_api_keys(),
    ]
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ All checks passed! System is ready.")
    else:
        print("⚠️  Some issues detected. Please review above.")
    
    print("\n📝 Next Steps:")
    print("1. Configure your API keys in .env file")
    print("2. Test with: python tools/model_adapter_v2.py --help")
    print("3. Start developing with AI-powered features!")
    print("=" * 50)

if __name__ == "__main__":
    main()
