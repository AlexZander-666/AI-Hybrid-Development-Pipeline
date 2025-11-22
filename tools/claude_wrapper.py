#!/usr/bin/env python3
import subprocess
import sys
import json
import time
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone

# 引用现有工具链
import ai_toolkit

def main():
    parser = argparse.ArgumentParser(description="Wrapper for Claude Code CLI to ensure Protocol Compliance")
    parser.add_argument("task", nargs="+", help="The task for Claude Code")
    parser.add_argument("--feature", required=True, help="Feature strictly associated with this fix/test")
    args = parser.parse_args()

    task_str = " ".join(args.task)
    print(f"[PROTOCOL] Wrap-running Claude Code for: {task_str}")

    # 1. 执行 Claude Code (假设 claude 命令已安装)
    start_time = time.time()
    try:
        # 这里使用 pexpect 或 subprocess 交互，简化演示用 subprocess
        # 实际使用中建议捕获 stdout 作为审计日志
        result = subprocess.run(["claude", *args.task], check=True, text=True, capture_output=True)
        output_log = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERR] Claude Code failed: {e.stderr}")
        sys.exit(1)
    
    duration = time.time() - start_time

    # 2. 生成审计 Artifact (Mocking the model_adapter logic)
    # 我们需要模拟生成一个 Artifact，证明这次修改是由 Claude 完成的
    metadata = json.dumps({
        "tool": "claude-code-cli",
        "task_hash": hashlib.sha256(task_str.encode()).hexdigest(),
        "duration_sec": round(duration, 2),
        "log_snippet": output_log[:500] if output_log else "No output"
    })

    mk_args = argparse.Namespace(
        feature=args.feature,
        phase="test",  # Claude Code 主要用于 Test/Fix 阶段
        owner="human-operator-via-claude",
        generator="claude-code-cli",
        spec_hash="maintainance-mode", # 修复模式下可能不关联特定 Spec
        spec_file=None,
        trace_id=f"claude-{int(time.time())}",
        metadata=metadata
    )

    print("[PROTOCOL] Signing Audit Artifact...")
    ai_toolkit.cmd_make_artifact(mk_args)
    print("[SUCCESS] Claude Code session recorded and signed.")

if __name__ == "__main__":
    main()