AI 混合开发流水线 (The Hybrid Pipeline)1. 设计阶段 (Architect) - Codex-high目标: 生成不可动摇的真理 (Spec)。操作:python tools/model_adapter.py call --model codex-high --phase spec --feature user_auth --prompt-file prompts/design_auth.txt --out docs/specs/user_auth.spec.md
关键点: 必须生成 spec_hash。2. 实现阶段 (Builder) - Gemini 3 / Antigravity目标: 一次性生成完整代码。操作:# 将 Spec Hash 传入以绑定关系
SPEC_HASH=$(python tools/ai_toolkit.py hash docs/specs/user_auth.spec.md | awk '{print $3}')

python tools/model_adapter.py call \
  --model gemini-exp-1121 \
  --phase code \
  --feature user_auth \
  --spec-hash $SPEC_HASH \
  --out src/services/user_auth.py
关键点: Gemini 必须读取 import_map.json，严禁引入未授权包。3. 调试与CI阶段 (Fixer) - Claude Code目标: 修复测试与合规性问题。操作:不要直接用 claude！使用 Wrapper：python tools/claude_wrapper.py --feature user_auth "Fix the dependency error in user_auth.py and pass unit tests"
关键点: Wrapper 会自动生成签名文件，确保持续集成通过。4. 提交 (The Gate)执行 git push。pre_receive_hook 会验证：Spec 和 Code 的 Hash 是否匹配。Claude 的修复记录是否有签名。代码中是否包含违禁依赖。