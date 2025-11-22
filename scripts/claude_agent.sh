#!/bin/bash
set -euo pipefail

# Fix C: 使用 Model Adapter 替代直接调用
# 集成了 Fix F: 自动化审计

EXIT_SUCCESS=0
EXIT_ERROR=1
EXIT_POLICY=2
EXIT_HUMAN=3

# Dirty Check
if [ -n "$(git status --porcelain)" ]; then
  echo "[ERR] Dirty working directory. Commit changes first."
  exit $EXIT_POLICY
fi

COMMAND=$1
shift

case $COMMAND in
  generate-tests)
    FEATURE=""
    OUT_FILE=""
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            --feature) FEATURE="$2"; shift ;;
            --out) OUT_FILE="$2"; shift ;;
            *) shift ;;
        esac
    done
    
    if [[ -z "$FEATURE" ]]; then exit $EXIT_ERROR; fi

    # 1. Generate via Model Adapter (New)
    # 创建临时 prompt 文件
    PROMPT_FILE=".tmp_prompt_${FEATURE}.txt"
    echo "Generate unit tests for feature ${FEATURE}..." > "$PROMPT_FILE"
    
    echo "[AGENT] Delegating to Model Adapter..."
    python3 tools/model_adapter.py call \
        --action call \
        --model "claude-3.5-sonnet" \
        --prompt-file "$PROMPT_FILE" \
        --out "$OUT_FILE" \
        --feature "$FEATURE" \
        --phase "test" \
        --owner "claude-agent"

    rm "$PROMPT_FILE"

    # 2. Security Scan (New Policy Driven)
    echo "[SEC] Running AST Security Scan..."
    # Scan tests 可能会生成 warning artifact，但 exit code 为 0
    python3 tools/ai_toolkit.py scan-tests "$OUT_FILE" --feature "$FEATURE"
    ;;

  run-loop)
    # ... (Loop logic needs similar updates to use model_adapter) ...
    echo "[INFO] Run loop placeholder - adapt to use model_adapter similarly."
    ;;
esac