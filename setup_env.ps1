# PowerShell script to set environment variables for AI Pipeline

Write-Host "Setting up environment variables..." -ForegroundColor Yellow

# Set environment variables for current session
$env:AI_ARTIFACT_SIGNING_KEY = "keys\dev_private.pem"
$env:AI_ARTIFACT_KEY_ID = "dev-local-user"
$env:AI_ARTIFACT_VERIFY_KEY = "keys\dev_public.pem"

# Optional: Set API keys if you have them
# $env:OPENAI_API_KEY = "sk-your-key-here"
# $env:GOOGLE_API_KEY = "your-key-here"
# $env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"

Write-Host "`n✅ Environment variables set for current session!" -ForegroundColor Green
Write-Host "`nCurrent configuration:" -ForegroundColor Cyan
Write-Host "  AI_ARTIFACT_SIGNING_KEY: $env:AI_ARTIFACT_SIGNING_KEY"
Write-Host "  AI_ARTIFACT_KEY_ID: $env:AI_ARTIFACT_KEY_ID"
Write-Host "  AI_ARTIFACT_VERIFY_KEY: $env:AI_ARTIFACT_VERIFY_KEY"

Write-Host "`n📝 To add API keys, edit this file and uncomment the API key lines" -ForegroundColor Yellow
Write-Host "   File location: setup_env.ps1" -ForegroundColor Gray
