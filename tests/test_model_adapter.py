"""
Unit tests for Model Adapter
"""
import json
import tempfile
from pathlib import Path
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.model_adapter_v2 import ModelAdapter, AIProviderError, PolicyViolation

class TestModelAdapter:
    """Test suite for ModelAdapter"""
    
    @pytest.fixture
    def temp_policy(self):
        """Create temporary policy file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
policy_version: "1.0.0"
model_rules:
  spec:
    - gpt-4
    - claude-3
  code:
    - gemini-pro
  test:
    - gpt-3.5-turbo
""")
            yield Path(f.name)
        os.unlink(f.name)
        
    @pytest.fixture
    def adapter(self, temp_policy):
        """Create adapter instance"""
        return ModelAdapter(policy_path=temp_policy)
        
    def test_load_policy(self, adapter):
        """Test policy loading"""
        assert adapter.policy is not None
        assert 'model_rules' in adapter.policy
        
    def test_verify_policy_allowed(self, adapter):
        """Test policy verification for allowed models"""
        assert adapter.verify_policy('spec', 'gpt-4') is True
        assert adapter.verify_policy('spec', 'GPT-4') is True  # Case insensitive
        assert adapter.verify_policy('spec', 'gpt-4-turbo') is True  # Prefix match
        
    def test_verify_policy_denied(self, adapter):
        """Test policy verification for denied models"""
        assert adapter.verify_policy('spec', 'gemini-pro') is False
        assert adapter.verify_policy('code', 'gpt-4') is False
        assert adapter.verify_policy('unknown', 'gpt-4') is False
        
    def test_mock_call(self, adapter):
        """Test mock call functionality"""
        content, metadata = adapter._mock_call('test-model', 'test prompt')
        
        assert 'test-model' in content
        assert metadata['provider'] == 'mock'
        assert metadata['tokens_in'] == 100
        assert metadata['tokens_out'] == 50
        
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_call_openai_mock(self, adapter):
        """Test OpenAI call with mocked response"""
        # Mock OpenAI client
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated content"
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 100
        mock_response.id = "test-id"
        
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        adapter.providers['openai'] = {
            'client': mock_openai,
            'models': ['gpt-4']
        }
        
        content, metadata = adapter._call_openai('gpt-4', 'test prompt')
        
        assert content == "Generated content"
        assert metadata['provider'] == 'openai'
        assert metadata['tokens_in'] == 50
        assert metadata['tokens_out'] == 100
        
    def test_call_openai_no_key(self, adapter):
        """Test OpenAI call without API key"""
        adapter.providers['openai'] = {'client': Mock(), 'models': []}
        
        with pytest.raises(AIProviderError, match="OPENAI_API_KEY not set"):
            adapter._call_openai('gpt-4', 'test')
            
    def test_call_model_routing(self, adapter):
        """Test model routing to correct provider"""
        # All calls should route to mock since no real providers are configured
        
        # OpenAI model
        content, metadata = adapter.call_model('gpt-4', 'test')
        assert 'Mock response' in content
        
        # Google model  
        content, metadata = adapter.call_model('gemini-pro', 'test')
        assert 'Mock response' in content
        
        # Anthropic model
        content, metadata = adapter.call_model('claude-3-opus', 'test')
        assert 'Mock response' in content
        
        # Unknown model
        content, metadata = adapter.call_model('unknown-model', 'test')
        assert 'Mock response' in content
        
    def test_provider_initialization(self):
        """Test provider initialization"""
        adapter = ModelAdapter()
        
        # Providers dict should exist even if empty
        assert isinstance(adapter.providers, dict)
