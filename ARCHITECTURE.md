# Architecture Overview

## 🏗️ System Architecture

The AI Hybrid Development Pipeline is built on three core principles:

1. **Zero Trust** - All AI operations must be cryptographically signed
2. **Policy Enforcement** - YAML-driven rules control model usage
3. **Audit Trail** - Immutable records of all code generation

## 📐 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                     (CLI / CI/CD Pipeline)                       │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────┐
│                      Model Adapter                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Policy Check │→ │  AI Gateway  │→ │ Artifact Gen │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────┬───────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────┐
│                       AI Toolkit                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Signing    │  │ Verification │  │  Scanning    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────┬───────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────┐
│                    Artifact Storage                             │
│                 (.ai_artifacts/*.json)                          │
└────────────────────────────────────────────────────────────────┘
```

## 🔑 Core Components

### 1. Model Adapter (`tools/model_adapter.py`)

**Responsibilities:**
- Route requests to appropriate AI models
- Enforce policy compliance before API calls
- Generate signed audit artifacts
- Handle API errors and retries

**Flow:**
```python
User Request
    ↓
Policy Verification (policy.yaml)
    ↓
AI Model Call (OpenAI/Google/Anthropic)
    ↓
Response Processing
    ↓
Artifact Generation (via ai_toolkit)
    ↓
File Output + Signed Artifact
```

**Key Functions:**
- `verify_policy(phase, model)` - Check if model is allowed for phase
- `main()` - Parse arguments and orchestrate workflow

**Extension Points:**
- Add new providers by implementing API calls in `main()`
- Extend phases by adding new keys to `policy.yaml`

### 2. AI Toolkit (`tools/ai_toolkit.py`)

**Responsibilities:**
- Generate RSA signatures for artifacts
- Verify artifact signatures
- Validate spec integrity (hash matching)
- Scan code for policy violations

**Cryptographic Implementation:**

```python
# Signing (RSA-PSS)
signature = private_key.sign(
    payload,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Verification
public_key.verify(
    signature,
    payload,
    padding.PSS(...),
    hashes.SHA256()
)
```

**Key Functions:**
- `cmd_make_artifact()` - Create signed JSON artifacts
- `cmd_verify_sig()` - Verify RSA signatures
- `cmd_verify_spec()` - Validate spec hash consistency
- `cmd_check_deps()` - Check dependency compliance
- `cmd_scan_tests()` - Scan for banned modules/calls

**Security Features:**
- Canonical JSON serialization (deterministic hashing)
- Timestamp-based trace IDs
- Key ID tracking for key rotation

### 3. Claude Wrapper (`tools/claude_wrapper.py`)

**Responsibilities:**
- Wrap Claude Code CLI for Phase 3 refinements
- Generate fix artifacts
- Maintain feature association

**Flow:**
```
User Fix Request
    ↓
Call Claude Code CLI
    ↓
Capture stdout/stderr
    ↓
Generate Fix Artifact
    ↓
Sign and Store
```

### 4. Policy Engine (`tools/policy.yaml`)

**Structure:**
```yaml
policy_version: "1.3.0"

model_rules:
  spec: [codex-high, gpt-4]     # Design phase
  code: [gemini-exp-1121]       # Implementation phase
  fix: [claude-3-opus]          # Refinement phase

dependency_rules:
  allowed_packages:
    flask: ">=2.0.0"            # Version constraints
    pydantic: "*"               # Any version

security_rules:
  test_banned_modules:          # Never allowed in tests
    - subprocess
    - eval
  test_restricted_modules:      # Warnings only
    - requests
    - socket
```

**Enforcement Points:**
1. **Pre-call** - `model_adapter.py` checks before API
2. **Post-generation** - `ai_toolkit.py` scans generated code
3. **Pre-commit** - Git hooks validate all files

### 5. Artifact Schema

**JSON Structure:**
```json
{
  "feature": "string",
  "phase": "spec | code | fix | model_call | scan_warning",
  "timestamp": "ISO-8601",
  "policy_version": "semver",
  "owner": {"email": "string"},
  "spec_hash": "sha256-hex | pending",
  "commit_hash": "git-sha | HEAD",
  "generator": "model-name",
  "trace_id": "uuid4",
  "metadata": {
    "model": "string",
    "prompt_hash": "sha256-hex",
    "provider_request_id": "string",
    "model_version": "string",
    "tokens_in": "integer",
    "tokens_out": "integer",
    "latency_ms": "integer"
  },
  "signature": "base64-rsa-signature",
  "signature_meta": {
    "key_id": "string",
    "algo": "RS256"
  }
}
```

**Immutability:** Signature covers all fields except `signature` and `signature_meta`

## 🔄 Data Flow

### Phase 1: Specification Generation

```
requirements.txt → [Model Adapter] → Codex API
                                         ↓
                                    spec.md
                                         ↓
                                  [AI Toolkit]
                                         ↓
                            feature.model_call.json (signed)
```

### Phase 2: Code Generation

```
spec.md + spec_hash → [Model Adapter] → Gemini API
                                             ↓
                                        source.py
                                             ↓
                                      [AI Toolkit]
                                             ↓
                            feature.model_call.json (updated, re-signed)
```

### Phase 3: Code Refinement (Optional)

```
Fix request → [Claude Wrapper] → Claude Code CLI
                                       ↓
                                 Modified code
                                       ↓
                                [AI Toolkit]
                                       ↓
                        feature.fix.json (signed)
```

### Verification Pipeline (Git Hook / CI)

```
git push → [pre-push hook]
              ↓
    For each .json in .ai_artifacts:
        [AI Toolkit] verify-sig
              ↓
    For each spec in docs/specs:
        [AI Toolkit] verify-spec
              ↓
    For each .py in src:
        [AI Toolkit] check-deps
              ↓
        ✅ All pass → Allow push
        ❌ Any fail → Block push
```

## 🔐 Security Architecture

### Threat Model

**Protected Against:**
- ✅ Unauthorized model usage
- ✅ Tampering with generated code
- ✅ Policy violation introduction
- ✅ Dependency confusion attacks
- ✅ Unauthorized code execution in tests

**Not Protected Against:**
- ⚠️ Compromised private keys (use HSM in production)
- ⚠️ Malicious prompts (requires human review)
- ⚠️ Side-channel attacks (out of scope)

### Trust Boundaries

1. **Local Development:**
   - Trust: Developer's machine
   - Keys: Local filesystem (600 permissions)
   - Verification: Pre-push hooks

2. **CI/CD:**
   - Trust: GitHub Actions runner
   - Keys: GitHub Secrets
   - Verification: Workflow steps

3. **Production:**
   - Trust: Deployment system
   - Keys: HSM or cloud KMS
   - Verification: Automated + manual approval

### Key Management

**Development:**
```bash
keys/
├── dev_private.pem  # Local only, never committed
└── dev_public.pem   # Can be committed for CI
```

**Production:**
- Private key: AWS KMS / Azure Key Vault / GCP KMS
- Public key: Embedded in CI/CD or retrieved from vault
- Key rotation: Artifacts include `key_id` for versioning

## 📦 Dependency Management

**Core Dependencies:**
- `cryptography` - RSA signing (FIPS 140-2 compliant)
- `PyYAML` - Policy parsing
- `tomli` - Lock file parsing (Python <3.11)
- `requests` - HTTP client (future: real API calls)

**Optional Dependencies:**
- `openai` - OpenAI API client
- `google-generativeai` - Google Gemini client
- `anthropic` - Anthropic Claude client

**Dependency Validation:**
- Whitelist in `policy.yaml`
- Lock file checking (`poetry.lock` / `requirements.txt`)
- Import scanning via AST analysis

## 🧪 Testing Strategy

### Current State: Manual Testing

See `docs/guides/TEST_REPORT.md` for validation results.

### Future: Automated Testing

**Unit Tests:**
```python
tests/
├── test_ai_toolkit.py
│   ├── test_signature_generation
│   ├── test_signature_verification
│   ├── test_canonical_json
│   └── test_policy_loading
├── test_model_adapter.py
│   ├── test_policy_enforcement
│   ├── test_artifact_generation
│   └── test_error_handling
└── test_claude_wrapper.py
    └── test_cli_invocation
```

**Integration Tests:**
```python
tests/integration/
├── test_full_pipeline.py
├── test_git_hooks.py
└── test_ci_workflow.py
```

**Test Coverage Goal:** >90%

## 🚀 Performance Considerations

### Bottlenecks

1. **RSA Signing:** ~5ms per artifact (acceptable)
2. **AI API Calls:** 1-30s (network/model dependent)
3. **Git Hook Verification:** O(n) artifacts (optimizable)

### Optimization Strategies

- **Parallel Verification:** Process artifacts concurrently
- **Caching:** Cache policy.yaml parsing
- **Incremental Validation:** Only verify new/modified artifacts

## 🔄 Extension Points

### Adding New AI Providers

1. Edit `tools/model_adapter.py`:
   ```python
   elif args.model.startswith("your-provider"):
       # Your API integration here
       pass
   ```

2. Update `tools/policy.yaml`:
   ```yaml
   model_rules:
     code: [..., your-provider-model]
   ```

### Adding New Verification Rules

1. Add function to `tools/ai_toolkit.py`:
   ```python
   def cmd_your_check(args):
       # Your validation logic
       pass
   ```

2. Register in `main()`:
   ```python
   elif args.cmd == "your-check":
       cmd_your_check(args)
   ```

### Custom Artifact Fields

1. Update `docs/protocol/artifact_schema.json`
2. Modify `cmd_make_artifact()` to include new fields
3. Signature still covers entire payload (automatic)

## 📊 Monitoring & Observability

### Metrics to Track

- **Artifact generation rate** - Operations per hour
- **Signature verification failures** - Security incidents
- **Policy violations** - Trend analysis
- **Model usage** - Cost optimization
- **Token consumption** - Billing tracking

### Log Aggregation

Export artifacts to centralized logging:
```bash
# Example: Send to Elasticsearch
for artifact in .ai_artifacts/*.json; do
  curl -X POST localhost:9200/ai-artifacts/_doc \
    -H 'Content-Type: application/json' \
    -d @"$artifact"
done
```

## 🎯 Design Decisions

### Why RSA Instead of ECDSA?

- **Compatibility:** Broader support in tooling
- **Key length:** 2048-bit RSA ≈ 224-bit ECDSA (sufficient)
- **Standards:** FIPS 140-2 certified implementations available

### Why JSON for Artifacts?

- **Human-readable:** Easy debugging
- **Tooling:** Universal parser support
- **Signing:** Canonical JSON ensures deterministic hashing

### Why Separate Tools?

- **Unix Philosophy:** Do one thing well
- **Composability:** Chain tools in scripts
- **Testing:** Isolated unit tests
- **Reusability:** Use toolkit in other projects

## 📚 References

- [RFC 8017](https://tools.ietf.org/html/rfc8017) - RSA Cryptography Specification
- [RFC 8785](https://tools.ietf.org/html/rfc8785) - JSON Canonicalization Scheme
- [NIST FIPS 140-2](https://csrc.nist.gov/publications/detail/fips/140/2/final) - Cryptographic Module Validation

---

**Last Updated:** 2025-11-22  
**Architecture Version:** 1.0
