#!/usr/bin/env python3
"""
Enhanced Model Adapter with Real AI Provider Integration
Supports OpenAI, Google Gemini, and Anthropic Claude
"""
import sys
import os
import json
import time
import hashlib
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import yaml
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIProviderError(Exception):
    """Custom exception for AI provider errors"""
    pass

class PolicyViolation(Exception):
    """Policy check failed"""
    pass

class ModelAdapter:
    """Universal adapter for multiple AI providers"""
    
    def __init__(self, policy_path: Path = Path("tools/policy.yaml")):
        self.policy_path = policy_path
        self.policy = self._load_policy()
        self.providers = self._initialize_providers()
        
    def _load_policy(self) -> Dict[str, Any]:
        """Load policy configuration"""
        if self.policy_path.exists():
            try:
                return yaml.safe_load(self.policy_path.read_text())
            except Exception as e:
                logger.warning(f"Failed to load policy: {e}")
                return {}
        return {}
        
    def _initialize_providers(self) -> Dict[str, Any]:
        """Initialize available AI providers"""
        providers = {}
        
        # OpenAI
        try:
            import openai
            providers['openai'] = {
                'client': openai,
                'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
            }
            logger.info("OpenAI provider initialized")
        except ImportError:
            logger.debug("OpenAI SDK not available")
            
        # Google Gemini
        try:
            import google.generativeai as genai
            providers['google'] = {
                'client': genai,
                'models': ['gemini-pro', 'gemini-pro-vision']
            }
            logger.info("Google Gemini provider initialized")
        except ImportError:
            logger.debug("Google Generative AI SDK not available")
            
        # Anthropic Claude
        try:
            import anthropic
            providers['anthropic'] = {
                'client': anthropic,
                'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-2.1']
            }
            logger.info("Anthropic provider initialized")
        except ImportError:
            logger.debug("Anthropic SDK not available")
            
        return providers
        
    def verify_policy(self, phase: str, model: str) -> bool:
        """Check if model is allowed for phase"""
        rules = self.policy.get('model_rules', {})
        allowed = set(rules.get(phase, []))
        
        if not allowed:
            return False
            
        # Normalize model name
        model_lower = model.lower()
        
        # Check exact match or vendor prefix
        for allowed_model in allowed:
            allowed_lower = allowed_model.lower()
            if (model_lower == allowed_lower or 
                model_lower.startswith(allowed_lower + "-") or
                model_lower.startswith(allowed_lower + "/")):
                return True
                
        return False
        
    def _call_openai(self, model: str, prompt: str, **kwargs) -> Tuple[str, Dict]:
        """Call OpenAI API"""
        if 'openai' not in self.providers:
            raise AIProviderError("OpenAI SDK not installed")
            
        client = self.providers['openai']['client']
        
        # Configure API key
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise AIProviderError("OPENAI_API_KEY not set")
            
        client.api_key = api_key
        
        try:
            start_time = time.time()
            
            response = client.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2048)
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            content = response.choices[0].message.content
            metadata = {
                'model': model,
                'provider': 'openai',
                'tokens_in': response.usage.prompt_tokens,
                'tokens_out': response.usage.completion_tokens,
                'latency_ms': latency_ms,
                'provider_request_id': response.id,
                'model_version': model
            }
            
            return content, metadata
            
        except Exception as e:
            raise AIProviderError(f"OpenAI API error: {e}")
            
    def _call_google(self, model: str, prompt: str, **kwargs) -> Tuple[str, Dict]:
        """Call Google Gemini API"""
        if 'google' not in self.providers:
            raise AIProviderError("Google Generative AI SDK not installed")
            
        genai = self.providers['google']['client']
        
        # Configure API key
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise AIProviderError("GOOGLE_API_KEY not set")
            
        genai.configure(api_key=api_key)
        
        try:
            start_time = time.time()
            
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(
                prompt,
                generation_config={
                    'temperature': kwargs.get('temperature', 0.7),
                    'max_output_tokens': kwargs.get('max_tokens', 2048)
                }
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            content = response.text
            metadata = {
                'model': model,
                'provider': 'google',
                'tokens_in': response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else -1,
                'tokens_out': response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else -1,
                'latency_ms': latency_ms,
                'provider_request_id': f"gemini-{int(time.time())}",
                'model_version': model
            }
            
            return content, metadata
            
        except Exception as e:
            raise AIProviderError(f"Google Gemini API error: {e}")
            
    def _call_anthropic(self, model: str, prompt: str, **kwargs) -> Tuple[str, Dict]:
        """Call Anthropic Claude API"""
        if 'anthropic' not in self.providers:
            raise AIProviderError("Anthropic SDK not installed")
            
        anthropic = self.providers['anthropic']['client']
        
        # Configure API key
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise AIProviderError("ANTHROPIC_API_KEY not set")
            
        client = anthropic.Anthropic(api_key=api_key)
        
        try:
            start_time = time.time()
            
            response = client.messages.create(
                model=model,
                max_tokens=kwargs.get('max_tokens', 2048),
                temperature=kwargs.get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            content = response.content[0].text
            metadata = {
                'model': model,
                'provider': 'anthropic',
                'tokens_in': response.usage.input_tokens if hasattr(response, 'usage') else -1,
                'tokens_out': response.usage.output_tokens if hasattr(response, 'usage') else -1,
                'latency_ms': latency_ms,
                'provider_request_id': response.id,
                'model_version': model
            }
            
            return content, metadata
            
        except Exception as e:
            raise AIProviderError(f"Anthropic API error: {e}")
            
    def call_model(self, model: str, prompt: str, **kwargs) -> Tuple[str, Dict]:
        """Route to appropriate provider based on model name"""
        
        # Determine provider from model name
        if model.startswith(('gpt-', 'o1-', 'o3-')):
            return self._call_openai(model, prompt, **kwargs)
        elif model.startswith('gemini-'):
            return self._call_google(model, prompt, **kwargs)
        elif model.startswith('claude-'):
            return self._call_anthropic(model, prompt, **kwargs)
        else:
            # Fallback to mock for unknown models
            logger.warning(f"Unknown model {model}, using mock response")
            return self._mock_call(model, prompt, **kwargs)
            
    def _mock_call(self, model: str, prompt: str, **kwargs) -> Tuple[str, Dict]:
        """Mock implementation for testing"""
        content = f"# Mock response from {model}\n# Prompt: {prompt[:100]}...\n\nprint('Hello World')"
        metadata = {
            'model': model,
            'provider': 'mock',
            'tokens_in': 100,
            'tokens_out': 50,
            'latency_ms': 200,
            'provider_request_id': f"mock-{int(time.time())}",
            'model_version': 'mock-v1'
        }
        return content, metadata

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Model Adapter with Real Provider Support")
    parser.add_argument("action", choices=["call"], help="Action to perform")
    parser.add_argument("--model", required=True, help="Model identifier")
    parser.add_argument("--prompt-file", required=True, help="Path to prompt file")
    parser.add_argument("--out", required=True, help="Output file path")
    parser.add_argument("--feature", required=True, help="Feature name")
    parser.add_argument("--phase", required=True, help="Development phase")
    parser.add_argument("--owner", default="system", help="Owner identifier")
    parser.add_argument("--temperature", type=float, default=0.7, help="Model temperature")
    parser.add_argument("--max-tokens", type=int, default=2048, help="Max output tokens")
    
    args = parser.parse_args()
    
    try:
        # Initialize adapter
        adapter = ModelAdapter()
        
        # Policy check
        if not adapter.verify_policy(args.phase, args.model):
            logger.error(f"Model {args.model} not allowed for phase {args.phase}")
            sys.exit(1)
            
        # Read prompt
        prompt_path = Path(args.prompt_file)
        if not prompt_path.exists():
            logger.error(f"Prompt file not found: {prompt_path}")
            sys.exit(1)
            
        prompt = prompt_path.read_text(encoding='utf-8')
        
        # Call model
        logger.info(f"Calling {args.model} for phase {args.phase}")
        content, metadata = adapter.call_model(
            args.model, 
            prompt,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )
        
        # Write output
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding='utf-8')
        logger.info(f"Output written to {out_path}")
        
        # Generate audit artifact
        metadata['prompt_hash'] = hashlib.sha256(prompt.encode()).hexdigest()
        
        # Import ai_toolkit dynamically
        try:
            spec = importlib.util.spec_from_file_location("ai_toolkit", "tools/ai_toolkit.py")
            ai_toolkit = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ai_toolkit)
            
            # Create artifact
            artifact_args = argparse.Namespace(
                feature=args.feature,
                phase="model_call",
                owner=args.owner,
                generator=args.model,
                spec_hash="pending",
                spec_file=None,
                trace_id=None,
                metadata=json.dumps(metadata)
            )
            
            ai_toolkit.cmd_make_artifact(artifact_args)
            logger.info("Audit artifact created")
            
        except Exception as e:
            logger.error(f"Failed to create artifact: {e}")
            # Don't fail the entire operation if artifact creation fails
            
    except PolicyViolation as e:
        logger.error(f"Policy violation: {e}")
        sys.exit(2)
    except AIProviderError as e:
        logger.error(f"AI provider error: {e}")
        sys.exit(3)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
