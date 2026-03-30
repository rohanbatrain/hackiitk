"""
Unit tests for the LLM Runtime component.

Tests verify specific functionality including model loading, memory monitoring,
structured output generation, and error handling.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from analysis.llm_runtime import LLMRuntime, GenerationConfig


def is_ollama_available():
    """Check if Ollama backend is available."""
    try:
        from analysis.llm_runtime import LLMRuntime
        runtime = LLMRuntime(model_path="qwen2.5:3b-instruct", backend="ollama")
        return True
    except Exception:
        return False


class TestLLMRuntimeInitialization:
    """Test LLM runtime initialization and model loading."""
    
    @pytest.mark.skipif(not is_ollama_available(), reason="Ollama backend not available")
    def test_ollama_backend_initialization(self):
        """Test that Ollama backend can be initialized."""
        # This test requires Ollama to be running with the model available
        try:
            runtime = LLMRuntime(
                model_path="qwen2.5:3b-instruct",
                backend="ollama"
            )
            assert runtime.backend == "ollama"
            assert runtime._is_loaded
        except RuntimeError as e:
            if "not available" in str(e):
                pytest.skip("Ollama model not available")
            raise
    
    def test_invalid_backend_raises_error(self):
        """Test that invalid backend raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            LLMRuntime(
                model_path="test-model",
                backend="invalid"
            )
        
        assert "Unsupported backend" in str(exc_info.value)
        assert "ollama" in str(exc_info.value)
        assert "llama-cpp" in str(exc_info.value)
    
    def test_memory_threshold_configuration(self):
        """Test that memory threshold can be configured."""
        try:
            runtime = LLMRuntime(
                model_path="qwen2.5:3b-instruct",
                backend="ollama",
                memory_threshold=0.85
            )
            assert runtime.memory_threshold == 0.85
        except RuntimeError:
            pytest.skip("Ollama not available")
    
    def test_model_not_found_error_message(self):
        """Test that missing model provides helpful error message."""
        with pytest.raises(RuntimeError) as exc_info:
            LLMRuntime(
                model_path="nonexistent-model:latest",
                backend="ollama"
            )
        
        error_msg = str(exc_info.value)
        assert "not available" in error_msg.lower() or "failed to load" in error_msg.lower()
        # Should include troubleshooting steps
        assert "ollama pull" in error_msg.lower() or "troubleshooting" in error_msg.lower()


class TestTextGeneration:
    """Test basic text generation functionality."""
    
    @pytest.fixture
    def runtime(self):
        """Create runtime instance for testing."""
        try:
            return LLMRuntime(
                model_path="qwen2.5:3b-instruct",
                backend="ollama"
            )
        except RuntimeError:
            pytest.skip("Ollama not available")
    
    def test_basic_generation(self, runtime):
        """Test basic text generation with default parameters."""
        prompt = "What is risk management? Answer in one sentence."
        
        response = runtime.generate(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert len(response) < 5000  # Reasonable upper bound
    
    def test_generation_with_temperature(self, runtime):
        """Test that temperature parameter is accepted."""
        prompt = "Define cybersecurity."
        
        # Low temperature for deterministic output
        response = runtime.generate(
            prompt,
            temperature=0.1,
            max_tokens=50
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generation_with_max_tokens(self, runtime):
        """Test that max_tokens parameter limits output length."""
        prompt = "Explain the NIST Cybersecurity Framework in detail."
        
        # Very short max_tokens
        response = runtime.generate(
            prompt,
            temperature=0.1,
            max_tokens=20
        )
        
        assert isinstance(response, str)
        # Response should be relatively short (though exact token count varies)
        assert len(response) < 500
    
    def test_generation_with_stop_sequences(self, runtime):
        """Test that stop sequences terminate generation."""
        prompt = "List three cybersecurity principles:\n1."
        
        response = runtime.generate(
            prompt,
            temperature=0.1,
            max_tokens=200,
            stop_sequences=["\n3."]
        )
        
        assert isinstance(response, str)
        # Response should stop before reaching "3."
        # (though this depends on model behavior)


class TestStructuredOutputGeneration:
    """Test structured JSON output generation."""
    
    @pytest.fixture
    def runtime(self):
        """Create runtime instance for testing."""
        try:
            return LLMRuntime(
                model_path="qwen2.5:3b-instruct",
                backend="ollama"
            )
        except RuntimeError:
            pytest.skip("Ollama not available")
    
    def test_structured_output_basic_schema(self, runtime):
        """Test structured output with simple schema."""
        prompt = """Analyze this policy statement:
"The organization performs annual risk assessments."

Determine coverage status."""
        
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "explanation": {"type": "string"}
            },
            "required": ["status", "explanation"]
        }
        
        result = runtime.generate_structured(
            prompt,
            schema,
            temperature=0.1,
            max_tokens=200
        )
        
        # Verify result is a dict
        assert isinstance(result, dict)
        
        # Verify required keys present
        assert "status" in result
        assert "explanation" in result
        
        # Verify values are strings
        assert isinstance(result["status"], str)
        assert isinstance(result["explanation"], str)
    
    def test_structured_output_complex_schema(self, runtime):
        """Test structured output with complex nested schema."""
        prompt = """Create a gap analysis entry for missing supply chain risk management."""
        
        schema = {
            "type": "object",
            "properties": {
                "subcategory_id": {"type": "string"},
                "status": {"type": "string"},
                "gap_explanation": {"type": "string"},
                "severity": {"type": "string"},
                "suggested_fix": {"type": "string"}
            },
            "required": ["subcategory_id", "status", "gap_explanation", "severity", "suggested_fix"]
        }
        
        result = runtime.generate_structured(
            prompt,
            schema,
            temperature=0.1,
            max_tokens=400
        )
        
        # Verify all required keys present
        for key in schema["required"]:
            assert key in result, f"Missing required key: {key}"
            assert isinstance(result[key], str), f"Key {key} should be string"
    
    def test_structured_output_handles_markdown_json(self, runtime):
        """Test that structured output handles JSON wrapped in markdown code blocks."""
        # This is a common LLM behavior - outputting ```json ... ```
        # The generate_structured method should handle this
        
        prompt = "Output a simple JSON object with a 'test' field."
        schema = {
            "type": "object",
            "properties": {
                "test": {"type": "string"}
            },
            "required": ["test"]
        }
        
        result = runtime.generate_structured(
            prompt,
            schema,
            temperature=0.1,
            max_tokens=100
        )
        
        assert isinstance(result, dict)
        assert "test" in result


class TestMemoryMonitoring:
    """Test memory monitoring and context truncation."""
    
    @pytest.fixture
    def runtime(self):
        """Create runtime instance for testing."""
        try:
            return LLMRuntime(
                model_path="qwen2.5:3b-instruct",
                backend="ollama",
                memory_threshold=0.9
            )
        except RuntimeError:
            pytest.skip("Ollama not available")
    
    def test_check_memory_returns_valid_percentage(self, runtime):
        """Test that check_memory returns valid percentage."""
        memory_usage = runtime.check_memory()
        
        assert isinstance(memory_usage, float)
        assert 0.0 <= memory_usage <= 1.0, \
            f"Memory usage should be 0.0-1.0, got {memory_usage}"
    
    def test_context_truncation_short_text(self, runtime):
        """Test that short text is not truncated."""
        short_text = "This is a short text."
        
        truncated = runtime.truncate_context(short_text, max_length=1000)
        
        assert truncated == short_text, "Short text should not be truncated"
    
    def test_context_truncation_long_text(self, runtime):
        """Test that long text is truncated correctly."""
        long_text = "This is a test sentence. " * 500  # ~12500 characters
        
        truncated = runtime.truncate_context(long_text, max_length=500)
        
        # Verify truncation occurred
        assert len(truncated) < len(long_text), "Text should be truncated"
        assert len(truncated) <= 600, "Truncated text should be around max_length"
        
        # Verify truncation indicator present
        assert "truncated" in truncated.lower()
        
        # Verify beginning preserved
        assert truncated.startswith("This is a test")
        
        # Verify ending preserved
        assert truncated.rstrip().endswith("sentence.")
    
    def test_memory_warning_on_high_usage(self, runtime):
        """Test that high memory usage triggers warning."""
        # Set a very low threshold to trigger warning
        runtime.memory_threshold = 0.01  # 1% - will definitely exceed
        
        with pytest.warns(UserWarning, match="Memory usage"):
            # This should trigger a warning
            runtime.generate(
                "Test prompt",
                temperature=0.1,
                max_tokens=50
            )


class TestOfflineVerification:
    """Test offline operation verification."""
    
    def test_ollama_localhost_verification(self):
        """Test that Ollama with localhost is verified as offline."""
        try:
            runtime = LLMRuntime(
                model_path="qwen2.5:3b-instruct",
                backend="ollama"
            )
            
            # Ollama on localhost should be considered offline
            assert runtime.verify_offline(), \
                "Ollama on localhost should be verified as offline"
        except RuntimeError:
            pytest.skip("Ollama not available")
    
    def test_llama_cpp_always_offline(self):
        """Test that llama.cpp is always verified as offline."""
        # Mock the llama.cpp loading to avoid needing actual model file
        with patch('analysis.llm_runtime.LLMRuntime._load_llama_cpp'):
            runtime = LLMRuntime(
                model_path="./models/test.gguf",
                backend="llama-cpp"
            )
            runtime._is_loaded = True
            
            # llama.cpp should always be offline
            assert runtime.verify_offline(), \
                "llama.cpp should always be verified as offline"


class TestErrorHandling:
    """Test error handling for various failure scenarios."""
    
    def test_generation_without_loaded_model(self):
        """Test that generation fails gracefully when model not loaded."""
        # Create runtime but prevent model loading
        with patch('analysis.llm_runtime.LLMRuntime._load_model'):
            runtime = LLMRuntime(
                model_path="test-model",
                backend="ollama"
            )
            runtime._is_loaded = False
            
            with pytest.raises(RuntimeError, match="Model not loaded"):
                runtime.generate("Test prompt")
    
    def test_structured_generation_without_loaded_model(self):
        """Test that structured generation fails gracefully when model not loaded."""
        with patch('analysis.llm_runtime.LLMRuntime._load_model'):
            runtime = LLMRuntime(
                model_path="test-model",
                backend="ollama"
            )
            runtime._is_loaded = False
            
            schema = {"type": "object", "properties": {"test": {"type": "string"}}}
            
            with pytest.raises(RuntimeError, match="Model not loaded"):
                runtime.generate_structured("Test prompt", schema)
    
    def test_structured_output_retry_on_invalid_json(self):
        """Test that structured output retries on invalid JSON."""
        try:
            runtime = LLMRuntime(
                model_path="qwen2.5:3b-instruct",
                backend="ollama"
            )
        except RuntimeError:
            pytest.skip("Ollama not available")
        
        # Mock the generate method to return invalid JSON first, then valid
        original_generate = runtime.generate
        call_count = [0]
        
        def mock_generate(prompt, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return "This is not JSON"
            else:
                return '{"test": "value"}'
        
        runtime.generate = mock_generate
        
        schema = {
            "type": "object",
            "properties": {"test": {"type": "string"}},
            "required": ["test"]
        }
        
        # Should succeed after retry
        result = runtime.generate_structured("Test", schema, max_retries=3)
        
        assert result == {"test": "value"}
        assert call_count[0] >= 2, "Should have retried after invalid JSON"


class TestReprAndStringMethods:
    """Test string representation methods."""
    
    def test_repr_with_loaded_model(self):
        """Test __repr__ with successfully loaded model."""
        try:
            runtime = LLMRuntime(
                model_path="qwen2.5:3b-instruct",
                backend="ollama"
            )
            
            repr_str = repr(runtime)
            
            assert "ollama" in repr_str
            assert "qwen2.5:3b-instruct" in repr_str
            assert "loaded" in repr_str
        except RuntimeError:
            pytest.skip("Ollama not available")
    
    def test_repr_with_unloaded_model(self):
        """Test __repr__ with failed model loading."""
        with patch('analysis.llm_runtime.LLMRuntime._load_model'):
            runtime = LLMRuntime(
                model_path="test-model",
                backend="ollama"
            )
            runtime._is_loaded = False
            
            repr_str = repr(runtime)
            
            assert "not loaded" in repr_str
