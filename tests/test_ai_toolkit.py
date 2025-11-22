"""
Unit tests for AI Toolkit
"""
import json
import tempfile
from pathlib import Path
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import ai_toolkit

class TestAIToolkit:
    """Test suite for ai_toolkit module"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
            
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock environment variables"""
        monkeypatch.setenv("AI_ARTIFACT_SIGNING_KEY", "mock_key")
        monkeypatch.setenv("AI_ARTIFACT_KEY_ID", "test_key_id")
        
    def test_load_policy(self):
        """Test policy loading"""
        policy = ai_toolkit.load_policy()
        assert isinstance(policy, dict)
        
    def test_canonicalize_json(self):
        """Test JSON canonicalization"""
        data = {"b": 2, "a": 1, "c": {"d": 4, "e": 3}}
        canonical = ai_toolkit.canonicalize_json(data)
        
        # Should be deterministic
        assert canonical == b'{"a":1,"b":2,"c":{"d":4,"e":3}}'
        
    def test_canonicalize_spec(self):
        """Test spec canonicalization"""
        spec_text = """---
        spec_hash: pending
        ---
        
        # Test Spec  
        
        This is a test.  
        """
        
        canonical = ai_toolkit.canonicalize_spec(spec_text)
        
        # Should strip front matter and normalize
        assert b"spec_hash" not in canonical
        assert b"# Test Spec" in canonical
        
    def test_atomic_write(self, temp_dir):
        """Test atomic file writing"""
        test_file = temp_dir / "test.txt"
        content = "test content"
        
        ai_toolkit.atomic_write(test_file, content)
        
        assert test_file.exists()
        assert test_file.read_text() == content
        
    def test_sign_payload_mock(self, mock_env):
        """Test payload signing with mock"""
        payload = b"test payload"
        result = ai_toolkit.sign_payload(payload)
        
        assert "signature" in result
        assert "signature_meta" in result
        assert result["signature_meta"]["algo"] in ["RS256", "NONE"]
        
    def test_policy_violation(self):
        """Test PolicyViolation exception"""
        with pytest.raises(ai_toolkit.PolicyViolation):
            raise ai_toolkit.PolicyViolation("Test violation")
            
    def test_signature_error(self):
        """Test SignatureError exception"""
        with pytest.raises(ai_toolkit.SignatureError):
            raise ai_toolkit.SignatureError("Test error")
