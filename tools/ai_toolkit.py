#!/usr/bin/env python3
import sys
import os
import re
import ast
import yaml
import json
import hashlib
import shutil
import argparse
import tempfile
import time
import base64
import unicodedata  # P0 Fix: 用于 Spec 归一化
from pathlib import Path
from datetime import datetime, timezone

# --- 0. 环境与依赖检查 ---
if sys.version_info < (3, 10):
    print("[ERR] Python 3.10+ required.")
    sys.exit(1)

# P0 Fix: 稳健的 TOML 库检测
_TOML_AVAILABLE = False
_tomllib = None
try:
    import tomllib as _tomllib
    _TOML_AVAILABLE = True
except ImportError:
    try:
        import tomli as _tomllib
        _TOML_AVAILABLE = True
    except ImportError:
        pass

# Crypto 检测
try:
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    print("[WARN] 'cryptography' lib not found. Signing will be strictly limited.")
    CRYPTO_AVAILABLE = False

# --- 异常定义 ---
class PolicyViolation(Exception): pass
class SignatureError(Exception): pass

# --- 常量与初始化 ---
ARTIFACTS_DIR = Path(".ai_artifacts")
BACKUP_DIR = ARTIFACTS_DIR / "backups"
INCIDENT_DIR = ARTIFACTS_DIR / "incidents"
POLICY_PATH = Path("tools/policy.yaml")

# P1 Fix: 显式目录初始化
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
INCIDENT_DIR.mkdir(parents=True, exist_ok=True)

# --- Helper: Load Policy ---
def load_policy():
    if POLICY_PATH.exists():
        try:
            return yaml.safe_load(POLICY_PATH.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"[WARN] Malformed policy.yaml: {e}")
            return {}
    return {}

POLICY = load_policy()
POLICY_VERSION = POLICY.get('policy_version', 'unknown')

# --- Helper: Atomic Write ---
def atomic_write(path: Path, content: str):
    folder = path.parent
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=folder, delete=False) as tf:
        tf.write(content)
        temp_path = Path(tf.name)
    try:
        if path.exists():
            try:
                shutil.copymode(path, temp_path)
            except OSError: pass
        os.replace(temp_path, path)
    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        raise e

# --- Helper: Canonicalization ---
def canonicalize_json(data: dict) -> bytes:
    return json.dumps(data, separators=(',', ':'), sort_keys=True).encode('utf-8')

# P0 Fix: Spec 归一化函数
def canonicalize_spec(text: str) -> bytes:
    """
    归一化 Spec 内容以确保 Hash 一致性：
    1. 剥离 YAML Front Matter
    2. NFKC Unicode 归一化
    3. 统一换行符为 \n
    4. 去除每行末尾空格及文件首尾空白
    """
    # 剥离 Front Matter
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, flags=re.DOTALL)
    body = m.group(2) if m else text
    
    # 归一化
    body = unicodedata.normalize("NFKC", body)
    body = re.sub(r'\r\n?', '\n', body)
    body = '\n'.join(line.rstrip() for line in body.split('\n')).strip() + '\n'
    
    return body.encode('utf-8')

# --- Helper: Signing ---
def sign_payload(payload: bytes) -> dict:
    priv_key_path_or_value = os.environ.get('AI_ARTIFACT_SIGNING_KEY')
    key_id = os.environ.get('AI_ARTIFACT_KEY_ID', 'dev-local')
    is_ci = os.environ.get('CI', 'false').lower() == 'true'

    file_exists = False
    if priv_key_path_or_value:
        try:
            file_exists = Path(priv_key_path_or_value).exists()
        except Exception:
            file_exists = False

    has_valid_key_source = priv_key_path_or_value and (file_exists or priv_key_path_or_value.strip().startswith("-----BEGIN"))
    
    if is_ci and (not CRYPTO_AVAILABLE or not has_valid_key_source):
        print("[FATAL] CI environment detected but missing valid signing key or crypto lib!")
        sys.exit(1)

    key_bytes = None
    if priv_key_path_or_value:
        if priv_key_path_or_value.strip().startswith("-----BEGIN"):
            key_bytes = priv_key_path_or_value.encode('utf-8')
        elif file_exists:
            with open(priv_key_path_or_value, "rb") as kf:
                key_bytes = kf.read()

    if not CRYPTO_AVAILABLE or not key_bytes:
        return {
            "signature": "SIMULATED_SIG_" + hashlib.sha256(payload).hexdigest(),
            "signature_meta": {"key_id": "simulated", "algo": "NONE"}
        }

    try:
        private_key = serialization.load_pem_private_key(key_bytes, password=None)
        signature = private_key.sign(
            payload,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return {
            "signature": base64.b64encode(signature).decode('utf-8'),
            "signature_meta": {"key_id": key_id, "algo": "RS256"}
        }
    except Exception as e:
        raise SignatureError(f"Signing failed: {e}")

# --- Cmd: Make Artifact ---
def cmd_make_artifact(args):
    try:
        commit_hash = os.popen("git rev-parse HEAD").read().strip()
        if not commit_hash: commit_hash = "0000000000000000000000000000000000000000"
    except:
        commit_hash = "0000000000000000000000000000000000000000"

    artifact = {
        "feature": args.feature,
        "phase": args.phase,
        "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "policy_version": POLICY_VERSION,
        "owner": {"email": args.owner} if "@" in args.owner else {"github": args.owner},
        "spec_hash": args.spec_hash or "pending",
        "commit_hash": commit_hash,
        "generator": args.generator,
        "trace_id": args.trace_id or hashlib.md5(str(time.time()).encode()).hexdigest(),
        "metadata": json.loads(args.metadata) if args.metadata else {}
    }

    payload = canonicalize_json(artifact)
    sig_info = sign_payload(payload)
    artifact.update(sig_info)

    filename = f"{args.feature}.{args.phase}.json"
    if args.phase == "scan_warning":
        filename = f"{args.feature}.warning.{int(time.time())}.json"
        
    out_path = ARTIFACTS_DIR / filename
    atomic_write(out_path, json.dumps(artifact, indent=2))
    print(f"[INFO] Artifact signed & created: {out_path} [{sig_info['signature_meta']['algo']}]")

# --- Cmd: Verify Spec (P0 Fix: Canonical Hash) ---
def cmd_verify_spec(args):
    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"[ERR] Spec file {spec_path} not found")
        sys.exit(1)

    text = spec_path.read_text(encoding='utf-8')
    
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    front = {}
    if m:
        try:
            front = yaml.safe_load(m.group(1)) or {}
        except Exception as e:
            raise PolicyViolation(f"Spec front matter YAML parse error: {e}")

    declared = front.get("spec_hash")
    
    # P0 Fix: 使用归一化内容计算 Hash
    computed = hashlib.sha256(canonicalize_spec(text)).hexdigest()

    if not declared or declared == "pending":
        print(f"[FAIL] Spec {spec_path.name} has no finalized spec_hash.")
        sys.exit(1)

    if declared != computed:
        print(f"[FAIL] Spec hash mismatch for {spec_path.name}.")
        print(f"Declared: {declared}")
        print(f"Computed: {computed} (Canonicalized)")
        sys.exit(1)
    
    print(f"[PASS] Spec verified: {spec_path.name}")

# --- Cmd: Verify Signature ---
def cmd_verify_sig(args):
    path = Path(args.artifact)
    pub_key_path = args.pubkey or os.environ.get('AI_ARTIFACT_VERIFY_KEY')
    is_ci = os.environ.get('CI', 'false').lower() == 'true'
    
    if not path.exists():
        raise FileNotFoundError(f"Artifact {path} not found")
        
    if not pub_key_path or not Path(pub_key_path).exists():
        if is_ci:
            print("[FATAL] CI environment missing public key for verification!")
            sys.exit(1)
        print("[WARN] No public key provided. Skipping crypto verification.")
        return

    if not CRYPTO_AVAILABLE:
        sys.exit(1)

    data = json.loads(path.read_text(encoding='utf-8'))
    sig_b64 = data.pop('signature', None)
    sig_meta = data.pop('signature_meta', None)
    
    if not sig_b64 or not sig_meta:
        raise SignatureError("Artifact missing signature fields")
        
    if sig_meta.get('algo') == 'NONE':
        print("[FAIL] Artifact uses insecure simulated signature!")
        sys.exit(1)

    payload = canonicalize_json(data)
    signature = base64.b64decode(sig_b64)

    try:
        with open(pub_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
            
        public_key.verify(
            signature,
            payload,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        print(f"[PASS] Signature Verified: {path.name}")
    except InvalidSignature:
        print(f"[FAIL] Invalid Signature for {path.name}")
        sys.exit(1)

# --- Cmd: Check Deps (P0 Fix: Robust TOML Check) ---
def cmd_check_deps(args):
    target = Path(args.target)
    rules = POLICY.get('dependency_rules', {})
    allowed_pkgs = {k.lower(): v for k, v in rules.get('allowed_packages', {}).items()}
    
    try:
        tree = ast.parse(target.read_text(encoding='utf-8'))
    except SyntaxError: raise PolicyViolation("Syntax Error")
        
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names: imports.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0: imports.add(node.module.split('.')[0])
    
    stdlibs = getattr(sys, "stdlib_module_names", set())
    
    # P0 Fix: 使用全局 _TOML_AVAILABLE 和 _tomllib
    lock_violations = []
    poetry_lock = Path("poetry.lock")
    lock_names = set()
    
    if poetry_lock.exists():
        try:
            if _TOML_AVAILABLE and _tomllib:
                pl = _tomllib.loads(poetry_lock.read_text(encoding='utf-8'))
                for pkg in pl.get('package', []):
                    lock_names.add(pkg['name'].lower())
            else:
                # Regex Fallback
                lock_content = poetry_lock.read_text(encoding='utf-8')
                for line in lock_content.splitlines():
                    m = re.match(r'^name = "([^"]+)"', line)
                    if m: lock_names.add(m.group(1).lower())
        except Exception as e:
             print(f"[WARN] Failed to parse poetry.lock: {e}")

    if lock_names:
        for imp in imports:
            if imp in stdlibs: continue
            if (Path("src")/imp).exists(): continue
            
            imp_norm = imp.lower()
            imp_dash = imp_norm.replace('_', '-')
            
            if imp_norm not in lock_names and imp_dash not in lock_names:
                lock_violations.append(imp)

    policy_violations = []
    for imp in imports:
        if imp in stdlibs: continue
        if (Path("src") / imp).exists(): continue
        if imp.lower() not in allowed_pkgs:
            policy_violations.append(imp)

    if policy_violations or lock_violations:
        report = {
            "policy_violations": policy_violations,
            "lock_file_violations": lock_violations,
            "policy_version": POLICY_VERSION
        }
        atomic_write(ARTIFACTS_DIR / f"{target.stem}.deps_violation.json", json.dumps(report, indent=2))
        raise PolicyViolation(f"Dependency Check Failed. Policy: {policy_violations}, Lock: {lock_violations}")
    
    print(f"[PASS] Deps Clean.")

# --- Cmd: Scan Tests ---
def cmd_scan_tests(args):
    target = Path(args.target)
    rules = POLICY.get('security_rules', {})
    BANNED = set(rules.get('test_banned_modules', []))
    RESTRICTED = set(rules.get('test_restricted_modules', []))
    
    try:
        tree = ast.parse(target.read_text(encoding='utf-8'))
    except SyntaxError: raise PolicyViolation("Syntax Error")
    
    banned = []
    restricted = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                module_name = n.name.split('.')[0]
                if module_name in BANNED: banned.append(module_name)
                if module_name in RESTRICTED: restricted.append(module_name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module.split('.')[0]
                if module_name in BANNED: banned.append(module_name)
                if module_name in RESTRICTED: restricted.append(module_name)
        
        if isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name): name = func.id
            elif isinstance(func, ast.Attribute): name = func.attr
            
            calls = set(rules.get('test_banned_calls', []))
            if name in calls:
                banned.append(f"Call:{name}")

    if banned:
        # P1 Fix: 确保 Incident 目录存在
        INCIDENT_DIR.mkdir(parents=True, exist_ok=True)
        report = {"violations": banned, "file": str(target)}
        atomic_write(INCIDENT_DIR / f"banned_{int(time.time())}.json", json.dumps(report))
        raise PolicyViolation(f"BANNED modules/calls detected: {sorted(set(banned))}")
        
    if restricted:
        print(f"[WARN] Restricted modules detected: {sorted(set(restricted))}")
        return

# --- Main ---
def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    p_verify_spec = sub.add_parser("verify-spec")
    p_verify_spec.add_argument("spec")
    
    p_verify_sig = sub.add_parser("verify-sig")
    p_verify_sig.add_argument("artifact")
    p_verify_sig.add_argument("--pubkey")
    
    p_check_deps = sub.add_parser("check-deps")
    p_check_deps.add_argument("target")
    
    p_scan_tests = sub.add_parser("scan-tests")
    p_scan_tests.add_argument("target")
    p_scan_tests.add_argument("--feature")
    
    p_hash = sub.add_parser("hash")
    p_hash.add_argument("filepath")
    p_hash.add_argument("--write", action="store_true")
    
    p_mk = sub.add_parser("make-artifact")
    p_mk.add_argument("--feature", required=True)
    p_mk.add_argument("--phase", required=True)
    p_mk.add_argument("--owner", required=True)
    p_mk.add_argument("--generator", default="unknown")
    p_mk.add_argument("--spec-hash")
    p_mk.add_argument("--spec-file")
    p_mk.add_argument("--trace_id")
    p_mk.add_argument("--metadata")

    args, _ = parser.parse_known_args()
    
    try:
        if args.cmd == "make-artifact": cmd_make_artifact(args)
        elif args.cmd == "verify-sig": cmd_verify_sig(args)
        elif args.cmd == "verify-spec": cmd_verify_spec(args)
        elif args.cmd == "check-deps": cmd_check_deps(args)
        elif args.cmd == "scan-tests": cmd_scan_tests(args)
        elif args.cmd == "hash": 
            # Simple hash cmd implementation reusing canonical logic
            path = Path(args.filepath)
            if not path.exists(): sys.exit(1)
            h = hashlib.sha256(canonicalize_spec(path.read_text(encoding='utf-8'))).hexdigest()
            print(f"[INFO] SHA256: {h}")
            if args.write:
                # 简单的写回逻辑，实际生产应复用更复杂的 YAML 更新逻辑
                print("[INFO] Write logic not fully implemented in this shim.")
    except Exception as e:
        print(f"[ERR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()