# AI 混合开发流水线 - 安装完成 ✅

## 📁 项目结构

```
后端终极工作流/
├── .ai_artifacts/          # AI 生成的审计文件（自动签名）
│   ├── backups/           # 备份存储
│   └── incidents/         # 违规事件记录
├── .github/workflows/      # CI/CD 配置
│   └── ai_gate.yml        # GitHub Actions 流水线
├── docs/specs/            # 规格文档（Codex 生成）
├── keys/                  # RSA 签名密钥对 ⚠️ 已加入 .gitignore
│   ├── dev_private.pem    # 私钥（绝不提交到仓库）
│   └── dev_public.pem     # 公钥（CI 使用）
├── src/                   # 源代码目录
├── tools/                 # AI 工具链核心
│   ├── ai_toolkit.py      # 核心工具库
│   ├── model_adapter.py   # 模型调用网关
│   ├── claude_wrapper.py  # Claude 操作封装器
│   ├── policy.yaml        # 策略配置文件
│   └── import_map.json    # 依赖白名单
├── .env                   # 环境变量（已加入 .gitignore）
└── .git/hooks/pre-push    # Git 推送前验证钩子
```

## ✅ 已完成的初始化步骤

1. ✅ 创建了标准 Protocol 目录结构
2. ✅ 生成了 RSA 签名密钥对（2048 位）
3. ✅ 配置了 `.env` 环境变量文件
4. ✅ 安装了 Python 依赖：
   - `cryptography>=41.0.0`
   - `PyYAML>=6.0`
   - `tomli>=2.0.0`
   - `requests>=2.31.0`
5. ✅ 设置了 `.gitignore`（保护密钥和敏感文件）
6. ✅ 安装了 Git pre-push hook（本地验证）
7. ✅ 迁移了所有核心文件到正确位置
8. ✅ 初始化了 Git 仓库

## 🚀 快速开始

### 1. 激活环境

在开始开发之前，每次都需要激活环境变量：

```bash
# Linux/Mac/Git Bash
source .env

# Windows PowerShell
foreach ($line in Get-Content .env) {
    if ($line -match '^export\s+([^=]+)="([^"]+)"') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}
```

### 2. 验证工具链

测试核心工具是否正常工作：

```bash
# 测试 AI Toolkit
python tools/ai_toolkit.py --help

# 测试 Model Adapter
python tools/model_adapter.py --help

# 测试 Claude Wrapper
python tools/claude_wrapper.py --help
```

### 3. 运行第一个完整流程

#### Phase 1: 设计（Spec）

生成规格文档（目前是模拟模式）：

```bash
python tools/model_adapter.py call \
  --model codex-high \
  --phase spec \
  --feature login_system \
  --prompt-file /dev/null \
  --out docs/specs/login_system.spec.md \
  --owner "architect@company.com"
```

#### Phase 2: 编码（Code）

提取 Spec Hash 并生成代码：

```bash
# 提取 Hash
SPEC_HASH=$(python tools/ai_toolkit.py hash docs/specs/login_system.spec.md | awk '{print $3}')

# 生成代码
python tools/model_adapter.py call \
  --model gemini-exp-1121 \
  --phase code \
  --feature login_system \
  --spec-hash $SPEC_HASH \
  --out src/login_system.py \
  --owner "builder@company.com"
```

#### Phase 3: 修复（Fix）

使用 Claude Wrapper 进行微调：

```bash
python tools/claude_wrapper.py --feature login_system "Fix typo in login logic"
```

#### Phase 4: 提交（Push）

```bash
git add .
git commit -m "Feat: Add login system with full AI audit trail"
git push origin main
```

**注意：** Git pre-push hook 会自动验证所有签名和 Hash。任何未经审计的修改都会被拒绝。

## 🔐 安全说明

⚠️ **重要：** 以下文件已被 `.gitignore` 保护，绝不应提交到仓库：

- `keys/` - RSA 密钥对
- `.env` - 环境变量配置
- `.ai_artifacts/*.warning.*.json` - 警告文件

生产环境的私钥应存储在 GitHub Secrets 中，使用 `SIGNING_PRIVATE_KEY` 密钥名称。

## 📋 Policy 配置

编辑 `tools/policy.yaml` 可以自定义：

- **依赖规则：** 允许/禁止的包列表
- **安全规则：** 禁止/限制的模块和函数调用
- **测试规则：** 测试代码的特殊限制

## 🔄 下一步

### 接入真实 AI API

目前 `model_adapter.py` 是模拟模式。要接入真实 API：

1. 编辑 `tools/model_adapter.py`
2. 在 `verify_policy` 通过后，添加真实的 API 调用：
   - OpenAI API（用于 Codex）
   - Google Gemini API（用于代码生成）
   - Anthropic Claude API（用于修复）

3. 设置 API 密钥：
   ```bash
   export OPENAI_API_KEY="your_key"
   export GOOGLE_API_KEY="your_key"
   export ANTHROPIC_API_KEY="your_key"
   ```

### 配置 CI/CD

1. 在 GitHub 仓库中设置 Secrets：
   - `SIGNING_PRIVATE_KEY` - 私钥内容
   - `SIGNING_PUBLIC_KEY` - 公钥内容

2. 推送代码到 GitHub，触发 `.github/workflows/ai_gate.yml` 流水线

## 📚 参考文档

- `backend_protocol_v3.5.md` - 协议规范
- `prompts_library_v3.3.md` - Prompt 库
- `artifact_schema.json` - Artifact 数据结构

## ❓ 故障排除

### Python 找不到模块

```bash
pip install -r requirements_ai.txt
```

### Git Hook 不执行

```bash
chmod +x .git/hooks/pre-push
```

### 签名验证失败

确保环境变量已加载：
```bash
source .env
echo $AI_ARTIFACT_SIGNING_KEY  # 应显示 keys/dev_private.pem
```

---

**状态：** ✅ 环境已就绪，可以开始开发！
