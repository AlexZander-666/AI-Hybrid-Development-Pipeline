# AI Hybrid Development Pipeline 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Military-grade AI development workflow with cryptographic audit trails**  
> A production-ready framework for secure, traceable, and policy-compliant AI-assisted code generation.

## 🌟 Overview

This project implements a **three-phase AI hybrid development pipeline** that enforces strict protocol compliance through cryptographic signing and policy verification:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Phase 1   │      │   Phase 2   │      │   Phase 3   │
│   Design    │─────▶│    Code     │─────▶│    Fix      │
│  (Codex)    │      │  (Gemini)   │      │  (Claude)   │
└─────────────┘      └─────────────┘      └─────────────┘
      │                     │                     │
      └─────────────────────┴─────────────────────┘
                            │
                   ┌────────▼────────┐
                   │  Audit Artifacts │
                   │  (RSA-256 Signed)│
                   └──────────────────┘
```

### Key Features

- ✅ **Cryptographic Audit Trail** - Every AI operation is signed with RSA-2048
- ✅ **Policy Enforcement** - YAML-based rules for models, dependencies, and security
- ✅ **Multi-Model Orchestration** - Route tasks to specialized AI models
- ✅ **Git Hook Integration** - Automatic verification before push
- ✅ **CI/CD Ready** - GitHub Actions workflow included
- ✅ **Zero Trust Architecture** - All code changes must have verifiable provenance

## 🎯 Use Cases

- **Enterprise AI Development** - Maintain full audit compliance for AI-generated code
- **Security-Critical Projects** - Enforce strict policies on AI model usage
- **Team Collaboration** - Track who generated what code with which model
- **Regulatory Compliance** - Generate immutable proof of code generation process

## 📦 Installation

### Prerequisites

- Python 3.10+
- Git
- OpenSSL (for key generation)
- Bash/PowerShell

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/AlexZander-666/AI-Hybrid-Development-Pipeline.git
cd ai-hybrid-pipeline

# 2. Run the setup script
bash scripts/setup_pipeline.sh

# 3. Install Python dependencies
pip install -r requirements_ai.txt

# 4. Activate environment
source .env  # Linux/Mac/Git Bash
# OR
# PowerShell: See docs/guides/README_SETUP.md for Windows instructions
```

### Configuration

1. **Generate signing keys** (automated by setup script):
   ```bash
   openssl genrsa -out keys/dev_private.pem 2048
   openssl rsa -in keys/dev_private.pem -pubout -out keys/dev_public.pem
   ```

2. **Configure API keys** (optional, for production use):
   ```bash
   export OPENAI_API_KEY="sk-..."
   export GOOGLE_API_KEY="AIza..."
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

3. **Customize policies** - Edit `tools/policy.yaml` to define:
   - Allowed AI models per phase
   - Permitted dependencies
   - Security restrictions

## 🚀 Usage

### Phase 1: Generate Specification

```bash
python tools/model_adapter.py call \
  --model codex-high \
  --phase spec \
  --feature user_authentication \
  --prompt-file requirements.txt \
  --out docs/specs/user_authentication.spec.md \
  --owner "architect@company.com"
```

**Output:** 
- `docs/specs/user_authentication.spec.md` - Specification document
- `.ai_artifacts/user_authentication.model_call.json` - Signed audit record

### Phase 2: Generate Code

```bash
# Extract spec hash
SPEC_HASH=$(python tools/ai_toolkit.py hash docs/specs/user_authentication.spec.md | awk '{print $3}')

# Generate code
python tools/model_adapter.py call \
  --model gemini-exp-1121 \
  --phase code \
  --feature user_authentication \
  --prompt-file docs/specs/user_authentication.spec.md \
  --out src/auth.py \
  --owner "developer@company.com"
```

**Output:**
- `src/auth.py` - Generated code
- `.ai_artifacts/user_authentication.model_call.json` - Updated audit record

### Phase 3: Refinement (Optional)

```bash
python tools/claude_wrapper.py \
  --feature user_authentication \
  "Add input validation and error handling"
```

**Output:**
- Modified code with tracked changes
- Additional audit artifacts

### Verification

```bash
# Verify artifact signature
python tools/ai_toolkit.py verify-sig \
  .ai_artifacts/user_authentication.model_call.json \
  --pubkey keys/dev_public.pem

# Check dependency compliance
python tools/ai_toolkit.py check-deps src/auth.py

# Scan for security issues
python tools/ai_toolkit.py scan-tests tests/test_auth.py
```

## 📂 Project Structure

```
.
├── .ai_artifacts/          # Signed audit records (JSON)
│   ├── backups/           # Historical artifacts
│   └── incidents/         # Policy violation reports
├── .github/workflows/      # CI/CD pipelines
│   └── ai_gate.yml        # GitHub Actions validation
├── docs/
│   ├── guides/            # User documentation
│   ├── protocol/          # Protocol specifications
│   └── specs/             # Generated specifications
├── scripts/               # Setup and utility scripts
│   ├── setup_pipeline.sh  # Installation script
│   ├── pre_receive_hook.sh # Git server hook example
│   └── claude_agent.sh    # Claude integration helper
├── src/                   # Generated source code
├── tools/                 # Core AI pipeline tools
│   ├── ai_toolkit.py      # Cryptography & verification
│   ├── model_adapter.py   # AI model gateway
│   ├── claude_wrapper.py  # Claude Code CLI wrapper
│   ├── policy.yaml        # Policy configuration
│   └── import_map.json    # Dependency whitelist
├── keys/                  # RSA key pairs (git-ignored)
├── .env                   # Environment variables (git-ignored)
├── .gitignore             # Git ignore rules
└── requirements_ai.txt    # Python dependencies
```

## 🔐 Security Model

### Cryptographic Signing

All AI operations generate **signed artifacts** using RSA-2048 with PSS padding:

```json
{
  "feature": "user_auth",
  "phase": "model_call",
  "timestamp": "2025-11-22T12:00:00Z",
  "generator": "gemini-exp-1121",
  "owner": {"email": "dev@company.com"},
  "signature": "jTtIjBtC6luVfjEw...",
  "signature_meta": {
    "key_id": "prod-ci-key",
    "algo": "RS256"
  }
}
```

### Policy Enforcement

The `policy.yaml` file defines strict rules:

```yaml
model_rules:
  spec: [codex-high, gpt-4]
  code: [gemini-exp-1121, claude-3-sonnet]
  fix: [claude-3-opus]

dependency_rules:
  allowed_packages:
    flask: ">=2.0.0"
    pydantic: ">=2.0.0"

security_rules:
  test_banned_modules: [subprocess, eval, exec]
```

### Git Hook Verification

The pre-push hook automatically verifies:
1. All artifact signatures are valid
2. Spec hashes match declared values
3. Dependencies comply with policy

## 🤝 CI/CD Integration

### GitHub Actions

The included workflow (`.github/workflows/ai_gate.yml`) performs:

- ✅ Signature verification using public key from Secrets
- ✅ Policy compliance checks
- ✅ Dependency scanning
- ✅ Artifact integrity validation

**Setup:**
1. Add `SIGNING_PUBLIC_KEY` to repository secrets
2. Push code to trigger the workflow
3. Workflow fails if any verification step fails

### Self-Hosted Runners

For maximum security, use self-hosted runners with:
- Hardware Security Modules (HSM) for key storage
- Network-isolated build environments
- Audit log forwarding to SIEM

## 📖 Documentation

- **[Installation Guide](docs/guides/README_SETUP.md)** - Detailed setup instructions
- **[Testing Report](docs/guides/TEST_REPORT.md)** - Validation test results
- **[Protocol Specification](docs/protocol/backend_protocol_v3.5.md)** - Technical protocol details
- **[Prompt Library](docs/protocol/prompts_library_v3.3.md)** - Reusable AI prompts
- **[Artifact Schema](docs/protocol/artifact_schema.json)** - JSON schema for audit records

## 🛠️ Development

### Mock Mode vs Production

**Current State:** The `model_adapter.py` operates in **mock mode** by default:
- Generates placeholder code
- Creates valid signed artifacts
- Useful for testing the pipeline without API costs

**Production Mode:** To enable real AI code generation:

1. Edit `tools/model_adapter.py` (lines 53-58)
2. Add real API calls:
   ```python
   import openai
   response = openai.ChatCompletion.create(
       model=args.model,
       messages=[{"role": "user", "content": prompt}]
   )
   response_content = response.choices[0].message.content
   ```

3. Configure API keys in `.env`

### Extending the Pipeline

- **Add new phases** - Update `policy.yaml` with new phase rules
- **Custom models** - Register models in `model_rules` section
- **Additional checks** - Extend `ai_toolkit.py` with new verification commands

## 🐛 Troubleshooting

### Signature Verification Fails

```bash
# Regenerate keys
bash scripts/setup_pipeline.sh

# Ensure environment is activated
source .env
```

### Git Hook Not Executing

```bash
# Set executable permission
chmod +x .git/hooks/pre-push
```

### Policy Violations

Check `policy.yaml` and ensure:
- Model is allowed for the specified phase
- All dependencies are whitelisted
- No banned modules are imported

## 📊 Metrics & Monitoring

Track AI usage with artifacts:
- **Token consumption** - `metadata.tokens_in` + `metadata.tokens_out`
- **Latency** - `metadata.latency_ms`
- **Model versions** - `metadata.model_version`
- **Provider IDs** - `metadata.provider_request_id`

Aggregate `.ai_artifacts/*.json` files for analytics.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Follow the existing code style
4. Add tests for new functionality
5. Submit a pull request

**Note:** All contributions must comply with the audit protocol.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI Codex** - Specification generation
- **Google Gemini** - Code generation
- **Anthropic Claude** - Code refinement
- **cryptography** library - RSA signing implementation

## 📧 Support

- **Issues:** [GitHub Issues](https://github.com/AlexZander-666/AI-Hybrid-Development-Pipeline/issues)
- **Discussions:** [GitHub Discussions](https://github.com/AlexZander-666/AI-Hybrid-Development-Pipeline/discussions)

---

**Built with ❤️ for secure AI development**

⭐ Star this repo if you find it useful!
