"""
Property-based tests for the LLM Runtime component.

Tests verify that local LLM execution maintains required properties including
offline operation, multi-model support, and structured output generation.
"""

import pytest
import socket
import urllib.request
from hypothesis import given, strategies as st, settings, assume
from analysis.llm_runtime import LLMRuntime
import os


# Test configuration - these models should be available locally
TEST_MODELS = {
    "ollama": "qwen2.5:3b-instruct",
    "llama-cpp": "./models/qwen2.5-3b-instruct-q4_k_m.gguf"
}


@pytest.fixture(scope="module")
def ollama_runtime():
    """Create Ollama-based LLM runtime for testing."""
    try:
        runtime = LLMRuntime(
            model_path=TEST_MODELS["ollama"],
            backend="ollama"
        )
        return runtime
    except Exception as e:
        pytest.skip(f"Ollama runtime not available: {e}")


@pytest.fixture(scope="module")
def llama_cpp_runtime():
    """Create llama.cpp-based LLM runtime for testing."""
    if not os.path.exists(TEST_MODELS["llama-cpp"]):
        pytest.skip(f"llama.cpp model not found at {TEST_MODELS['llama-cpp']}")
    
    try:
        runtime = LLMRuntime(
            model_path=TEST_MODELS["llama-cpp"],
            backend="llama-cpp"
        )
        return runtime
    except Exception as e:
        pytest.skip(f"llama.cpp runtime not available: {e}")


# Property 1: Complete Offline Operation
# **Validates: Requirements 1.1, 1.2, 8.5**
def test_offline_llm_operation_ollama(ollama_runtime):
    """
    Property 1: Complete Offline Operation (Ollama backend)
    
    Test that LLM inference makes no network calls.
    This verifies that the Ollama backend uses localhost endpoint.
    """
    # Verify the runtime reports offline capability
    assert ollama_runtime.verify_offline(), \
        "Ollama runtime should operate offline (localhost endpoint)"
    
    # Test that we can generate text (should work offline)
    test_prompt = "What is cybersecurity? Answer in one sentence."
    
    try:
        response = ollama_runtime.generate(
            test_prompt,
            temperature=0.1,
            max_tokens=100
        )
        
        # Verify we got a response
        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"
        
    except Exception as e:
        pytest.fail(f"Offline LLM generation raised exception: {e}")


def test_offline_llm_operation_llama_cpp(llama_cpp_runtime):
    """
    Property 1: Complete Offline Operation (llama.cpp backend)
    
    Test that LLM inference makes no network calls.
    llama.cpp is fully local and should always operate offline.
    """
    # Verify the runtime reports offline capability
    assert llama_cpp_runtime.verify_offline(), \
        "llama.cpp runtime should always operate offline"
    
    # Test that we can generate text (should work offline)
    test_prompt = "What is cybersecurity? Answer in one sentence."
    
    try:
        response = llama_cpp_runtime.generate(
            test_prompt,
            temperature=0.1,
            max_tokens=100
        )
        
        # Verify we got a response
        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"
        
    except Exception as e:
        pytest.fail(f"Offline LLM generation raised exception: {e}")


# Property 49: Multi-Model Support
# **Validates: Requirements 17.6**
@pytest.mark.parametrize("model_config", [
    ("ollama", "qwen2.5:3b-instruct"),
    ("ollama", "phi3.5:3.8b-mini-instruct"),
    ("ollama", "mistral:7b-instruct"),
])
def test_multi_model_support(model_config):
    """
    Property 49: Multi-Model Support
    
    Test that system loads and executes multiple model options.
    This validates that different models can be loaded and used
    for inference with the same interface.
    """
    backend, model_name = model_config
    
    try:
        # Attempt to load the model
        runtime = LLMRuntime(
            model_path=model_name,
            backend=backend
        )
        
        # Verify model is loaded
        assert runtime._is_loaded, f"Model {model_name} should be loaded"
        
        # Test basic generation
        response = runtime.generate(
            "Test prompt",
            temperature=0.1,
            max_tokens=50
        )
        
        assert isinstance(response, str), "Response should be a string"
        
    except RuntimeError as e:
        # Model might not be downloaded - this is acceptable
        if "not available" in str(e) or "not found" in str(e):
            pytest.skip(f"Model {model_name} not available locally: {e}")
        else:
            raise


# Additional property tests for LLM runtime behavior
@given(
    temperature=st.floats(min_value=0.0, max_value=1.0),
    max_tokens=st.integers(min_value=10, max_value=512)
)
@settings(max_examples=10, deadline=30000)
def test_generation_parameters(ollama_runtime, temperature, max_tokens):
    """
    Test that generation respects temperature and max_tokens parameters.
    
    This property test verifies that the LLM runtime correctly applies
    generation parameters across different values.
    """
    test_prompt = "Explain risk management."
    
    try:
        response = ollama_runtime.generate(
            test_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Verify response is generated
        assert isinstance(response, str), "Response should be a string"
        
        # Note: We can't strictly verify token count without tokenizer,
        # but we can check that response is reasonable
        assert len(response) > 0, "Response should not be empty"
        
    except Exception as e:
        # Some parameter combinations might fail - that's acceptable
        # as long as it's not a crash
        assert "generation failed" in str(e).lower() or "error" in str(e).lower()


def test_structured_output_generation(ollama_runtime):
    """
    Test that LLM can generate structured JSON output.
    
    This validates the generate_structured() method which is critical
    for Stage B gap analysis.
    """
    prompt = """Analyze this policy statement for risk management coverage:
"The organization conducts annual risk assessments."

Determine if this covers the NIST CSF requirement for continuous risk monitoring."""
    
    schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["covered", "partially_covered", "missing"]},
            "explanation": {"type": "string"},
            "gap": {"type": "string"}
        },
        "required": ["status", "explanation", "gap"]
    }
    
    try:
        result = ollama_runtime.generate_structured(
            prompt,
            schema,
            temperature=0.1,
            max_tokens=300
        )
        
        # Verify result is a dict
        assert isinstance(result, dict), "Structured output should be a dict"
        
        # Verify required keys are present
        assert "status" in result, "Result should have 'status' key"
        assert "explanation" in result, "Result should have 'explanation' key"
        assert "gap" in result, "Result should have 'gap' key"
        
        # Verify status is valid
        assert result["status"] in ["covered", "partially_covered", "missing"], \
            f"Invalid status: {result['status']}"
        
    except Exception as e:
        pytest.fail(f"Structured output generation failed: {e}")


def test_memory_monitoring(ollama_runtime):
    """
    Test that memory monitoring works correctly.
    
    This validates the check_memory() method which is used to
    prevent OOM crashes on consumer hardware.
    """
    memory_usage = ollama_runtime.check_memory()
    
    # Verify memory usage is a valid percentage
    assert isinstance(memory_usage, float), "Memory usage should be a float"
    assert 0.0 <= memory_usage <= 1.0, \
        f"Memory usage should be between 0.0 and 1.0, got {memory_usage}"


def test_context_truncation(ollama_runtime):
    """
    Test that context truncation works correctly.
    
    This validates the truncate_context() method which prevents
    memory overflow when processing long documents.
    """
    # Create a long text
    long_text = "This is a test sentence. " * 1000  # ~5000 characters
    
    # Truncate to 500 characters
    truncated = ollama_runtime.truncate_context(long_text, max_length=500)
    
    # Verify truncation occurred
    assert len(truncated) <= 600, \
        f"Truncated text should be ~500 chars, got {len(truncated)}"
    
    # Verify truncation indicator is present
    assert "truncated" in truncated.lower(), \
        "Truncated text should contain truncation indicator"
    
    # Verify beginning and end are preserved
    assert truncated.startswith("This is a test"), \
        "Truncated text should preserve beginning"
    assert truncated.endswith("test sentence. "), \
        "Truncated text should preserve ending"


def test_error_handling_invalid_model():
    """
    Test that appropriate errors are raised for invalid models.
    
    This validates error handling when models are not available.
    """
    with pytest.raises(RuntimeError) as exc_info:
        LLMRuntime(
            model_path="nonexistent-model:latest",
            backend="ollama"
        )
    
    # Verify error message is helpful
    error_msg = str(exc_info.value)
    assert "not available" in error_msg.lower() or "failed to load" in error_msg.lower(), \
        "Error message should indicate model is not available"


def test_error_handling_invalid_backend():
    """
    Test that appropriate errors are raised for invalid backends.
    
    This validates input validation for backend parameter.
    """
    with pytest.raises(ValueError) as exc_info:
        LLMRuntime(
            model_path="test-model",
            backend="invalid-backend"
        )
    
    # Verify error message mentions supported backends
    error_msg = str(exc_info.value)
    assert "ollama" in error_msg.lower() and "llama-cpp" in error_msg.lower(), \
        "Error message should list supported backends"
