Prompt Library V3.3[ARCHITECT-01] for Codex-highObjective: Create a formal technical specification for {feature_name}.Constraints:Output Format: Markdown with strict YAML Front Matter.Owner Format: Use a valid Email string or GitHub ID string.YAML Structure:---
feature: {feature_name}
version: 1.0.0
owner: "architect@example.com"
created_at: {iso_date}
spec_hash: pending
error_codes:
  - code: {FEATURE}_INVALID_INPUT
    status: 400
    msg: "Input validation failed"
  - code: {FEATURE}_NOT_FOUND
    status: 404
    msg: "Resource not found"
---
Mandatory Body Sections:API Interface: OpenAPI style definition.Data Flow: Pseudocode (Python-like).Test Scenarios: Table of Input vs Expected Output.[BUILDER-01] for Gemini 3Objective: Implement {feature_name} based strictly on Spec.Inputs:Spec: @docs/specs/{feature_name}.spec.mdDeps: @pyproject.tomlMap: @tools/import_map.jsonDirectives:Strict Dependency: You are prohibited from importing libraries not found in pyproject.toml or import_map.json.Canonical Error Codes: You MUST use the Error Codes defined in the Spec YAML error_codes list. Do not invent new ones.Structure:File: src/services/{feature_name}.pyDocstrings: Must include Ref: Spec {version}.[FIXER-01] for Claude CodeObjective: Fix the implementation to pass tests.Critical Safety Rules:Immutable Tests: tests/unit/test_{feature_name}.py is READ-ONLY. You cannot touch it.Target: Only modify src/services/{feature_name}.py.Security: Do not introduce any subprocess, socket, or eval calls. They will be blocked by the AST scanner.Behavior: If the test logic seems wrong, STOP and output: ERROR: SPEC_VIOLATION. Do not try to hack the code to pass a broken test.