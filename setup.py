#!/usr/bin/env python3
"""
Cross-platform setup script for AI Hybrid Development Pipeline
Replaces bash-only setup_pipeline.sh for Windows compatibility
"""
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Optional

class PipelineSetup:
    """Cross-platform pipeline setup utility"""
    
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.is_ci = os.environ.get("CI", "false").lower() == "true"
        self.root_dir = Path.cwd()
        
    def create_directories(self):
        """Create required directory structure"""
        directories = [
            "tools",
            "docs/specs", 
            "src",
            ".ai_artifacts",
            ".ai_artifacts/backups",
            ".ai_artifacts/incidents",
            "keys",
            "tests"
        ]
        
        print("📂 Creating directory structure...")
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        print("✅ Directories created")
        
    def generate_keys(self):
        """Generate RSA key pair for development"""
        private_key = Path("keys/dev_private.pem")
        public_key = Path("keys/dev_public.pem")
        
        if private_key.exists():
            print("ℹ️  Keys already exist")
            return
            
        print("🔐 Generating RSA signing keys...")
        
        try:
            # Try using cryptography library first (cross-platform)
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            
            # Generate private key
            private = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Write private key
            private_pem = private.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            private_key.write_bytes(private_pem)
            
            # Write public key
            public = private.public_key()
            public_pem = public.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            public_key.write_bytes(public_pem)
            
            # Set permissions (Unix-like systems only)
            if not self.is_windows:
                os.chmod(private_key, 0o600)
                
            print("✅ Keys generated using cryptography library")
            
        except ImportError:
            # Fallback to OpenSSL if available
            if shutil.which("openssl"):
                subprocess.run([
                    "openssl", "genrsa", "-out", str(private_key), "2048"
                ], check=True)
                subprocess.run([
                    "openssl", "rsa", "-in", str(private_key), 
                    "-pubout", "-out", str(public_key)
                ], check=True)
                
                if not self.is_windows:
                    os.chmod(private_key, 0o600)
                    
                print("✅ Keys generated using OpenSSL")
            else:
                print("⚠️  Cannot generate keys: Install cryptography package or OpenSSL")
                
    def create_env_file(self):
        """Create .env configuration file"""
        env_file = Path(".env")
        
        if env_file.exists():
            print("ℹ️  .env file already exists")
            return
            
        print("⚙️  Creating .env configuration...")
        
        # Windows vs Unix path handling
        if self.is_windows:
            env_content = f"""# Windows Environment Variables
set AI_ARTIFACT_SIGNING_KEY=keys\\dev_private.pem
set AI_ARTIFACT_KEY_ID=dev-local-user  
set AI_ARTIFACT_VERIFY_KEY=keys\\dev_public.pem
"""
        else:
            env_content = """# Unix Environment Variables
export AI_ARTIFACT_SIGNING_KEY="keys/dev_private.pem"
export AI_ARTIFACT_KEY_ID="dev-local-user"
export AI_ARTIFACT_VERIFY_KEY="keys/dev_public.pem"
"""
        
        env_file.write_text(env_content)
        print("✅ .env file created")
        
    def update_gitignore(self):
        """Ensure sensitive files are gitignored"""
        gitignore = Path(".gitignore")
        entries = [
            "keys/",
            "*.pem",
            ".env",
            ".env.local",
            ".ai_artifacts/*.warning.*.json"
        ]
        
        existing = gitignore.read_text() if gitignore.exists() else ""
        
        for entry in entries:
            if entry not in existing:
                existing += f"\n{entry}"
                
        gitignore.write_text(existing.strip() + "\n")
        print("🛡️  Updated .gitignore")
        
    def install_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing Python dependencies...")
        
        # Check Python version
        if sys.version_info < (3, 10):
            print("❌ Python 3.10+ required")
            sys.exit(1)
            
        # Install packages
        packages = [
            "cryptography>=41.0.0",
            "PyYAML>=6.0",
            "requests>=2.31.0"
        ]
        
        # Add tomli for Python < 3.11
        if sys.version_info < (3, 11):
            packages.append("tomli>=2.0.0")
            
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade"
            ] + packages, check=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError:
            print("⚠️  Failed to install dependencies automatically")
            print("   Run: pip install " + " ".join(packages))
            
    def setup_git_hooks(self):
        """Install Git hooks for protocol enforcement"""
        hook_path = Path(".git/hooks/pre-push")
        
        if not Path(".git").exists():
            print("⚠️  Not a git repository, skipping hooks")
            return
            
        print("⚓ Installing Git pre-push hook...")
        
        # Create Python-based hook for cross-platform compatibility
        hook_content = """#!/usr/bin/env python3
import sys
import os
import subprocess
from pathlib import Path

print("🔍 [AI GATE] Verifying protocol compliance...")

# Load environment
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.replace("export ", "").replace("set ", "").strip()
                value = value.strip().strip('"')
                os.environ[key] = value

# Verify artifacts
artifacts = list(Path(".ai_artifacts").glob("*.json"))
for art in artifacts:
    result = subprocess.run([
        sys.executable, "tools/ai_toolkit.py", "verify-sig", 
        str(art), "--pubkey", "keys/dev_public.pem"
    ])
    if result.returncode != 0:
        print(f"❌ Signature verification failed: {art}")
        sys.exit(1)

# Verify specs
specs = list(Path("docs/specs").glob("*.spec.md"))
for spec in specs:
    result = subprocess.run([
        sys.executable, "tools/ai_toolkit.py", "verify-spec", str(spec)
    ])
    if result.returncode != 0:
        print(f"❌ Spec verification failed: {spec}")
        sys.exit(1)

print("✅ [AI GATE] All checks passed")
"""
        
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_path.write_text(hook_content)
        
        # Make executable on Unix-like systems
        if not self.is_windows:
            os.chmod(hook_path, 0o755)
            
        print("✅ Git hooks installed")
        
    def run(self):
        """Execute complete setup"""
        print("\n🚀 Initializing AI Hybrid Development Pipeline")
        print(f"   Platform: {platform.system()}")
        print(f"   Python: {sys.version.split()[0]}\n")
        
        self.create_directories()
        self.generate_keys()
        self.create_env_file()
        self.update_gitignore()
        self.install_dependencies()
        self.setup_git_hooks()
        
        print("\n🎉 Setup complete!")
        print("\n📌 Next steps:")
        if self.is_windows:
            print("   1. Run: setup.bat (to load environment variables)")
            print("   2. Install AI provider SDKs: pip install openai google-generativeai anthropic")
        else:
            print("   1. Run: source .env")
            print("   2. Install AI provider SDKs: pip install openai google-generativeai anthropic")
        print("   3. Configure API keys for your AI providers")
        print("   4. Start developing with protocol compliance!\n")

if __name__ == "__main__":
    setup = PipelineSetup()
    setup.run()
