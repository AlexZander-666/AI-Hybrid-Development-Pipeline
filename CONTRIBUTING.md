# Contributing to AI Hybrid Development Pipeline

Thank you for your interest in contributing! This document outlines the process and guidelines.

## 🤝 How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** when creating a new issue
3. **Include:**
   - Python version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs or error messages

### Suggesting Features

1. **Open a discussion** first to gauge interest
2. **Describe the use case** and why it's valuable
3. **Consider implementation** complexity and breaking changes

### Submitting Pull Requests

1. **Fork the repository** and create a branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards:
   - Use `black` for Python code formatting
   - Add docstrings to all functions
   - Include type hints where appropriate
   - Keep functions focused and testable

3. **Test your changes:**
   ```bash
   # Run all tools to ensure they work
   python tools/ai_toolkit.py --help
   python tools/model_adapter.py --help
   
   # Test signature generation
   bash scripts/setup_pipeline.sh
   ```

4. **Commit with clear messages:**
   ```bash
   git commit -m "feat: Add support for GPT-4 Turbo model"
   ```

   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation changes
   - `refactor:` - Code refactoring
   - `test:` - Test additions/changes
   - `chore:` - Build/tooling changes

5. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📋 Code Style Guidelines

### Python

- **Formatting:** Use `black` with default settings
- **Line length:** 100 characters (black default: 88, but we allow 100)
- **Imports:** Sort with `isort`
- **Type hints:** Required for all public functions
- **Docstrings:** Google-style docstrings

Example:
```python
def verify_signature(artifact_path: Path, public_key: str) -> bool:
    """Verify the RSA signature of an AI artifact.
    
    Args:
        artifact_path: Path to the JSON artifact file
        public_key: Base64-encoded RSA public key
        
    Returns:
        True if signature is valid, False otherwise
        
    Raises:
        FileNotFoundError: If artifact file doesn't exist
        SignatureError: If signature format is invalid
    """
    pass
```

### YAML

- Use 2-space indentation
- Quote strings with special characters
- Add comments explaining complex configurations

### Shell Scripts

- Use `#!/bin/bash` shebang
- Enable strict mode: `set -euo pipefail`
- Quote all variables: `"$variable"`
- Use meaningful variable names

## 🧪 Testing Guidelines

### Manual Testing

Before submitting a PR, test:

1. **Setup script:**
   ```bash
   bash scripts/setup_pipeline.sh
   ```

2. **Core workflow:**
   ```bash
   # Generate spec
   python tools/model_adapter.py call --model codex-high \
     --phase spec --feature test_feature \
     --prompt-file /dev/null --out docs/specs/test.spec.md \
     --owner "test@example.com"
   
   # Verify signature
   python tools/ai_toolkit.py verify-sig \
     .ai_artifacts/test_feature.model_call.json \
     --pubkey keys/dev_public.pem
   ```

3. **Policy enforcement:**
   ```bash
   # Should fail with unauthorized model
   python tools/model_adapter.py call --model gpt-5-turbo ...
   ```

### Future: Automated Tests

We're working on a comprehensive test suite. In the meantime:
- Manually test all affected functionality
- Check for regressions in existing features

## 📚 Documentation

- **Update README.md** if you change user-facing functionality
- **Add examples** for new features
- **Update protocol docs** if you change artifact schema
- **Comment complex code** explaining the "why" not just the "what"

## 🔐 Security Considerations

This project deals with cryptographic signatures and code generation. Please:

- **Never commit private keys** - They're already in `.gitignore`
- **Validate all inputs** - Especially file paths and shell commands
- **Use parameterized queries** - Avoid string concatenation for commands
- **Review dependencies** - Check new packages for known vulnerabilities
- **Report security issues privately** - Email maintainers before public disclosure

## 🏛️ Code Review Process

1. **Automated checks** run on all PRs:
   - Linting (future)
   - Signature verification
   - Policy compliance

2. **Manual review** by maintainers:
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - Breaking change assessment

3. **Approval required** before merge

## 🎯 Development Priorities

Current focus areas:
1. **Real AI API integration** - Move from mock to production
2. **Automated testing** - Unit and integration tests
3. **Performance optimization** - Faster signature verification
4. **Additional model support** - More providers and models

## 📝 Commit Sign-Off

By contributing, you agree that:
- Your contributions are your original work
- You have the right to submit them
- Your contributions are licensed under MIT (see LICENSE)

## 💬 Communication

- **GitHub Discussions** - Feature ideas and questions
- **GitHub Issues** - Bug reports and tasks
- **Pull Requests** - Code contributions

## 🙏 Recognition

Contributors are acknowledged in:
- README.md contributors section
- Release notes
- Git history

Thank you for making AI development more secure and traceable! 🚀
