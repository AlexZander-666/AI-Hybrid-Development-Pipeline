# Project Structure

This document provides a complete overview of the project's directory structure and file organization.

## 📂 Directory Tree

```
ai-hybrid-pipeline/
│
├── .ai_artifacts/              # Signed audit artifacts (JSON)
│   ├── backups/               # Historical artifact backups
│   └── incidents/             # Security violation reports
│
├── .github/                   # GitHub configuration
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   │   ├── bug_report.md      # Bug report template
│   │   └── feature_request.md # Feature request template
│   ├── workflows/             # GitHub Actions
│   │   └── ai_gate.yml        # CI/CD pipeline
│   └── PULL_REQUEST_TEMPLATE.md # PR template
│
├── docs/                      # Documentation
│   ├── guides/                # User guides
│   │   ├── README_SETUP.md    # Installation guide
│   │   └── TEST_REPORT.md     # Test validation report
│   ├── protocol/              # Protocol specifications
│   │   ├── artifact_schema.json      # Artifact JSON schema
│   │   ├── backend_protocol_v3.5.md  # Protocol specification
│   │   └── prompts_library_v3.3.md   # Reusable prompts
│   └── specs/                 # Generated specifications (empty by default)
│
├── keys/                      # RSA key pairs (git-ignored)
│   ├── dev_private.pem        # Private signing key (local only)
│   └── dev_public.pem         # Public verification key
│
├── scripts/                   # Setup and utility scripts
│   ├── setup_pipeline.sh      # One-click installation
│   ├── pre_receive_hook.sh    # Git server hook example
│   └── claude_agent.sh        # Claude integration helper
│
├── src/                       # Generated source code (empty by default)
│
├── tools/                     # Core AI pipeline tools
│   ├── ai_toolkit.py          # Cryptography & verification
│   ├── model_adapter.py       # AI model gateway
│   ├── claude_wrapper.py      # Claude Code CLI wrapper
│   ├── policy.yaml            # Policy configuration
│   └── import_map.json        # Dependency whitelist
│
├── .env                       # Environment variables (git-ignored)
├── .gitignore                 # Git ignore rules
├── ARCHITECTURE.md            # Architecture documentation
├── CHANGELOG.md               # Version history
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # MIT License
├── README.md                  # Main documentation
├── PROJECT_STRUCTURE.md       # This file
└── requirements_ai.txt        # Python dependencies
```

## 📄 File Descriptions

### Root Directory

| File | Purpose | Commitable |
|------|---------|------------|
| `.env` | Local environment variables (keys, settings) | ❌ No |
| `.gitignore` | Specifies files to exclude from Git | ✅ Yes |
| `ARCHITECTURE.md` | Technical architecture deep-dive | ✅ Yes |
| `CHANGELOG.md` | Version history and release notes | ✅ Yes |
| `CONTRIBUTING.md` | Guidelines for contributors | ✅ Yes |
| `LICENSE` | MIT License text | ✅ Yes |
| `README.md` | Main project documentation | ✅ Yes |
| `PROJECT_STRUCTURE.md` | This file | ✅ Yes |
| `requirements_ai.txt` | Python dependencies | ✅ Yes |

### `.ai_artifacts/`

**Purpose:** Store signed JSON audit records for all AI operations.

| Item | Description | Commitable |
|------|-------------|------------|
| `*.model_call.json` | AI model invocation records | ✅ Yes |
| `*.spec.json` | Specification generation records | ✅ Yes |
| `*.fix.json` | Code refinement records | ✅ Yes |
| `*.warning.*.json` | Temporary warning files | ❌ No |
| `backups/` | Historical snapshots | ✅ Yes |
| `incidents/` | Security violation logs | ✅ Yes |

**Example Artifact:**
```json
{
  "feature": "login_system",
  "phase": "model_call",
  "timestamp": "2025-11-22T12:00:00Z",
  "generator": "gemini-exp-1121",
  "signature": "base64-encoded-rsa-signature",
  "signature_meta": {"key_id": "prod-key-01", "algo": "RS256"}
}
```

### `.github/`

**Purpose:** GitHub-specific configuration and automation.

| File | Purpose |
|------|---------|
| `workflows/ai_gate.yml` | CI/CD pipeline that verifies signatures and policies |
| `ISSUE_TEMPLATE/bug_report.md` | Template for bug reports |
| `ISSUE_TEMPLATE/feature_request.md` | Template for feature requests |
| `PULL_REQUEST_TEMPLATE.md` | Template for pull requests |

### `docs/`

**Purpose:** All project documentation.

#### `docs/guides/`
- `README_SETUP.md` - Complete installation and configuration guide
- `TEST_REPORT.md` - Test validation results and metrics

#### `docs/protocol/`
- `artifact_schema.json` - JSON Schema for artifact validation
- `backend_protocol_v3.5.md` - Technical protocol specification
- `prompts_library_v3.3.md` - Collection of reusable AI prompts

#### `docs/specs/`
- Empty by default
- Populated with AI-generated specification documents
- Format: `{feature_name}.spec.md`

### `keys/`

**Purpose:** RSA key pairs for signing and verification.

| File | Description | Commitable |
|------|-------------|------------|
| `dev_private.pem` | 2048-bit RSA private key | ❌ **NEVER** |
| `dev_public.pem` | 2048-bit RSA public key | ✅ Optional |

**Security Warning:** Private keys must NEVER be committed. Use GitHub Secrets for CI/CD.

### `scripts/`

**Purpose:** Automation scripts for setup and maintenance.

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup_pipeline.sh` | One-click installation | `bash scripts/setup_pipeline.sh` |
| `pre_receive_hook.sh` | Git server hook example | Copy to `.git/hooks/` |
| `claude_agent.sh` | Claude CLI integration helper | Called by `claude_wrapper.py` |

### `src/`

**Purpose:** AI-generated source code.

- Empty by default
- Populated by `model_adapter.py` during Phase 2
- All code should have corresponding artifacts in `.ai_artifacts/`

### `tools/`

**Purpose:** Core AI pipeline implementation.

| Tool | Purpose | Key Functions |
|------|---------|---------------|
| `ai_toolkit.py` | Cryptography & verification | `verify-sig`, `verify-spec`, `check-deps`, `scan-tests`, `hash`, `make-artifact` |
| `model_adapter.py` | AI model gateway | Policy enforcement, API calls, artifact generation |
| `claude_wrapper.py` | Claude Code wrapper | Wraps Claude CLI, generates fix artifacts |
| `policy.yaml` | Policy rules | Model permissions, dependency rules, security rules |
| `import_map.json` | Dependency whitelist | Maps import names to allowed packages |

## 🔐 Security-Sensitive Files

**Git-Ignored (NEVER commit):**
- `keys/` - All key files
- `.env` - Environment variables
- `*.pem` - Any PEM files
- `__pycache__/` - Python cache
- `.ai_artifacts/*.warning.*.json` - Ephemeral warnings

**Commitable but Sensitive:**
- `keys/dev_public.pem` - Public keys are safe but optional
- `.ai_artifacts/*.json` - Audit records are safe (already signed)

## 📊 File Size Guidelines

| Category | Typical Size | Max Recommended |
|----------|--------------|-----------------|
| Artifacts (`.json`) | 1-2 KB | 10 KB |
| Specs (`.spec.md`) | 5-50 KB | 500 KB |
| Source Code (`.py`) | 10-500 KB | 5 MB |
| Keys (`.pem`) | ~1.7 KB (private), ~450 B (public) | N/A |

## 🗑️ Cleanup Recommendations

### Before Committing

```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Remove temporary artifacts
rm .ai_artifacts/*.warning.*.json

# Verify no keys are staged
git status | grep -E "keys/|\.pem|\.env"
```

### Before Production Deployment

```bash
# Remove development keys
rm keys/dev_*.pem

# Clear test artifacts
rm -rf .ai_artifacts/backups/*
rm -rf .ai_artifacts/incidents/*

# Remove test code
rm -rf src/test_*.py
rm -rf docs/specs/test_*.spec.md
```

## 📈 Growth Patterns

As your project grows:

```
Initial (Empty):
├── .ai_artifacts/     (0 files)
├── docs/specs/        (0 files)
└── src/               (0 files)

After 10 features:
├── .ai_artifacts/     (30-50 files)  # ~3-5 artifacts per feature
├── docs/specs/        (10 files)      # 1 spec per feature
└── src/               (10-30 files)   # 1-3 source files per feature

After 100 features:
├── .ai_artifacts/     (300-500 files)
├── docs/specs/        (100 files)
└── src/               (100-300 files)
```

Consider archiving old artifacts to `backups/` periodically.

## 🔄 Maintenance Tasks

### Weekly
- Review `.ai_artifacts/incidents/` for violations
- Rotate logs if using external logging

### Monthly
- Archive old artifacts to `backups/`
- Review and update `policy.yaml`
- Check for dependency updates

### Quarterly
- Rotate signing keys (update `key_id` in artifacts)
- Audit all committed files
- Review and update documentation

## 🚀 Quick Navigation

| Need to... | Go to... |
|------------|----------|
| Install the pipeline | `scripts/setup_pipeline.sh` |
| Configure policies | `tools/policy.yaml` |
| Generate code | `tools/model_adapter.py` |
| Verify signatures | `tools/ai_toolkit.py` |
| Understand architecture | `ARCHITECTURE.md` |
| Contribute | `CONTRIBUTING.md` |
| Report issues | `.github/ISSUE_TEMPLATE/` |
| View test results | `docs/guides/TEST_REPORT.md` |

---

**Last Updated:** 2025-11-22  
**Structure Version:** 1.0
