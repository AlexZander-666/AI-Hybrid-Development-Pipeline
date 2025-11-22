#!/bin/bash
set -e

echo "🚀 Initializing AI Hybrid Pipeline..."

# 1. 创建目录结构
echo "📂 Creating directory structure..."
mkdir -p tools
mkdir -p docs/specs
mkdir -p src
mkdir -p .ai_artifacts
mkdir -p keys

# 2. 生成签名密钥 (开发环境用)
# 注意：生产环境(CI)应使用 GitHub Secrets，不应将私钥提交到仓库
if [ ! -f keys/dev_private.pem ]; then
    echo "🔐 Generating RSA Signing Keys for Development..."
    openssl genrsa -out keys/dev_private.pem 2048
    openssl rsa -in keys/dev_private.pem -pubout -out keys/dev_public.pem
    chmod 600 keys/dev_private.pem
    echo "✅ Keys generated in keys/"
else
    echo "ℹ️  Keys already exist."
fi

# 3. 配置本地环境变量 (.env)
if [ ! -f .env ]; then
    echo "⚙️  Creating local .env config..."
    cat <<EOF > .env
export AI_ARTIFACT_SIGNING_KEY="keys/dev_private.pem"
export AI_ARTIFACT_KEY_ID="dev-local-user"
export AI_ARTIFACT_VERIFY_KEY="keys/dev_public.pem"
EOF
    echo "✅ .env created. Run 'source .env' to activate."
fi

# 4. 安装 Python 依赖
echo "📦 Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements_ai.txt
else
    echo "⚠️  pip3 not found. Please install requirements_ai.txt manually."
fi

# 5. 设置 Git Ignore (至关重要，防止私钥泄露)
if ! grep -q "keys/" .gitignore 2>/dev/null; then
    echo "keys/" >> .gitignore
    echo ".env" >> .gitignore
    echo ".ai_artifacts/*.warning.*.json" >> .gitignore
    echo "🛡️  Added keys/ and .env to .gitignore"
fi

# 6. 安装本地 Pre-push Hook (模拟 Gate)
# 将你上传的 pre_receive_hook 改造成本地 pre-push 检查
HOOK_PATH=".git/hooks/pre-push"
echo "⚓ Installing Git pre-push hook..."

cat <<'EOF' > $HOOK_PATH
#!/bin/bash
# Local Simulation of the AI Gate
echo "🔍 [AI GATE] Verifying Protocol Compliance before push..."

# 确保环境变量存在
if [ -f .env ]; then source .env; fi

# 1. 验证所有 Artifacts 的签名
echo "   -> Verifying Artifact Signatures..."
for art in $(find .ai_artifacts -name "*.json"); do
    python3 tools/ai_toolkit.py verify-sig "$art" --pubkey keys/dev_public.pem
    if [ $? -ne 0 ]; then
        echo "❌ Artifact Signature Verification Failed: $art"
        exit 1
    fi
done

# 2. 验证 Spec Hash 一致性
echo "   -> Verifying Spec Integrity..."
for spec in $(find docs/specs -name "*.spec.md"); do
    python3 tools/ai_toolkit.py verify-spec "$spec"
    if [ $? -ne 0 ]; then
        echo "❌ Spec Hash Mismatch: $spec"
        exit 1
    fi
done

echo "✅ [AI GATE] All checks passed. Push allowed."
exit 0
EOF

chmod +x $HOOK_PATH

echo "🎉 Installation Complete!"
echo "👉 Action Required: Move your tool scripts (ai_toolkit.py, etc.) into the 'tools/' directory."
echo "👉 Run 'source .env' to start developing."