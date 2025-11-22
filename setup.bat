@echo off
REM Windows setup script for AI Hybrid Development Pipeline

echo Setting up environment variables...
set AI_ARTIFACT_SIGNING_KEY=keys\dev_private.pem
set AI_ARTIFACT_KEY_ID=dev-local-user
set AI_ARTIFACT_VERIFY_KEY=keys\dev_public.pem

echo Environment configured successfully!
echo.
echo You can now use the AI pipeline tools.
echo.
cmd /k
