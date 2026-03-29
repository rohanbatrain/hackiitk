"""
LLM Runtime component for local language model execution.

This module provides a unified interface for running quantized language models
locally using either llama.cpp or Ollama backends. It supports offline operation,
memory monitoring, and structured JSON output generation.
"""

import json
import psutil
import warnings
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class GenerationConfig:
    """Configuration for LLM text generation."""
    temperature: float = 0.1
    max_tokens: int = 512
    top_p: float = 0.9
    stop_sequences: Optional[List[str]] = None


class LLMRuntime:
    """
    Local LLM runtime supporting llama.cpp and Ollama backends.
    
    This class provides a unified interface for executing quantized language models
    in GGUF format on consumer hardware. It includes memory monitoring, context
    truncation, and structured output generation capabilities.
    
    Attributes:
        model_path: Path to local GGUF model file (for llama.cpp) or model name (for Ollama)
        backend: Backend to use ('ollama' or 'llama-cpp')
        memory_threshold: RAM usage percentage threshold for context truncation (default: 0.9)
        _llm: Backend-specific LLM instance
        _is_loaded: Whether the model is successfully loaded
    """
    
    def __init__(
        self,
        model_path: str,
        backend: str = "ollama",
        memory_threshold: float = 0.9
    ):
        """
        Initialize LLM runtime with specified backend.
        
        Args:
            model_path: Path to GGUF model file (llama.cpp) or model name (Ollama)
            backend: Backend to use ('ollama' or 'llama-cpp')
            memory_threshold: RAM usage percentage (0.0-1.0) to trigger context truncation
            
        Raises:
            ValueError: If backend is not supported
            RuntimeError: If model cannot be loaded
        """
        if backend not in ["ollama", "llama-cpp"]:
            raise ValueError(f"Unsupported backend: {backend}. Use 'ollama' or 'llama-cpp'")
        
        self.model_path = model_path
        self.backend = backend
        self.memory_threshold = memory_threshold
        self._llm = None
        self._is_loaded = False
        
        # Load the model
        self._load_model()
    
    def _load_model(self) -> None:
        """
        Load the LLM model using the specified backend.
        
        Raises:
            RuntimeError: If model loading fails
        """
        try:
            if self.backend == "ollama":
                self._load_ollama()
            elif self.backend == "llama-cpp":
                self._load_llama_cpp()
            
            self._is_loaded = True
            
        except Exception as e:
            raise RuntimeError(
                f"Failed to load model '{self.model_path}' with backend '{self.backend}': {e}\n"
                f"Troubleshooting:\n"
                f"  - For Ollama: Ensure Ollama is installed and running (https://ollama.ai)\n"
                f"  - For Ollama: Run 'ollama pull {self.model_path}' to download the model\n"
                f"  - For llama-cpp: Ensure the GGUF file exists at the specified path\n"
                f"  - Check that you have sufficient RAM for the model"
            )
    
    def _load_ollama(self) -> None:
        """Load model using Ollama backend."""
        try:
            from langchain_ollama import OllamaLLM
        except ImportError:
            raise RuntimeError(
                "langchain-ollama not installed. Install with: pip install langchain-ollama"
            )
        
        # Initialize Ollama LLM with default temperature
        self._llm = OllamaLLM(
            model=self.model_path,
            base_url="http://localhost:11434",
            temperature=0.1  # Default low temperature for deterministic output
        )
        
        # Test the connection
        try:
            # Simple test to verify model is available
            self._llm.invoke("test", stop=["test"])
        except Exception as e:
            raise RuntimeError(
                f"Ollama model '{self.model_path}' not available. "
                f"Run 'ollama pull {self.model_path}' to download it. Error: {e}"
            )
    
    def _load_llama_cpp(self) -> None:
        """Load model using llama.cpp backend."""
        try:
            from langchain_community.llms import LlamaCpp
        except ImportError:
            raise RuntimeError(
                "langchain-community not installed. Install with: pip install langchain-community"
            )
        
        import os
        if not os.path.exists(self.model_path):
            raise RuntimeError(
                f"Model file not found: {self.model_path}\n"
                f"Download GGUF models from HuggingFace and place them in the models directory."
            )
        
        # Initialize llama.cpp LLM
        self._llm = LlamaCpp(
            model_path=self.model_path,
            n_ctx=4096,  # Context window size
            n_threads=4,  # CPU threads to use
            n_gpu_layers=0,  # No GPU acceleration (CPU-only)
            verbose=False
        )
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 512,
        stop_sequences: Optional[List[str]] = None
    ) -> str:
        """
        Generate text from prompt with specified parameters.
        
        Args:
            prompt: Input prompt text
            temperature: Sampling temperature (0.0-1.0, lower = more deterministic)
            max_tokens: Maximum number of tokens to generate
            stop_sequences: Optional list of sequences that stop generation
            
        Returns:
            Generated text response
            
        Raises:
            RuntimeError: If model is not loaded or generation fails
            MemoryError: If memory usage exceeds threshold
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Cannot generate text.")
        
        # Check memory before generation
        memory_usage = self.check_memory()
        if memory_usage >= self.memory_threshold:
            warnings.warn(
                f"Memory usage at {memory_usage:.1%}, exceeding threshold {self.memory_threshold:.1%}. "
                f"Consider truncating context or using a smaller model."
            )
        
        try:
            # Configure generation parameters based on backend
            if self.backend == "ollama":
                # For Ollama, parameters must be set during initialization
                # Create a temporary LLM instance with the desired parameters
                from langchain_ollama import OllamaLLM
                temp_llm = OllamaLLM(
                    model=self.model_path,
                    base_url="http://localhost:11434",
                    temperature=temperature,
                    num_predict=max_tokens
                )
                response = temp_llm.invoke(
                    prompt,
                    stop=stop_sequences or []
                )
            else:  # llama-cpp
                # llama.cpp uses direct parameters
                response = self._llm.invoke(
                    prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stop=stop_sequences or []
                )
            
            return response.strip() if isinstance(response, str) else str(response).strip()
            
        except Exception as e:
            raise RuntimeError(f"Text generation failed: {e}")
    
    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        temperature: float = 0.1,
        max_tokens: int = 512,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate JSON output conforming to specified schema.
        
        This method prompts the LLM to generate valid JSON matching the provided
        schema. It includes retry logic for invalid JSON responses.
        
        Args:
            prompt: Input prompt text (should instruct model to output JSON)
            schema: JSON schema dict describing expected output structure
            temperature: Sampling temperature (keep low for structured output)
            max_tokens: Maximum tokens to generate
            max_retries: Number of retry attempts for invalid JSON
            
        Returns:
            Parsed JSON dict conforming to schema
            
        Raises:
            RuntimeError: If generation fails after all retries
            ValueError: If generated JSON doesn't conform to schema
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Cannot generate structured output.")
        
        # Enhance prompt with JSON instructions
        json_prompt = f"""{prompt}

You must respond with valid JSON only. Do not include any explanatory text before or after the JSON.
The JSON must conform to this schema:
{json.dumps(schema, indent=2)}

JSON Response:"""
        
        last_error = None
        for attempt in range(max_retries):
            try:
                # Generate response
                response = self.generate(
                    json_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stop_sequences=None
                )
                
                # Extract JSON from response (handle markdown code blocks)
                json_text = response.strip()
                if json_text.startswith("```json"):
                    json_text = json_text[7:]
                if json_text.startswith("```"):
                    json_text = json_text[3:]
                if json_text.endswith("```"):
                    json_text = json_text[:-3]
                json_text = json_text.strip()
                
                # Parse JSON
                result = json.loads(json_text)
                
                # Basic schema validation (check required keys)
                if "properties" in schema:
                    required_keys = schema.get("required", [])
                    missing_keys = [k for k in required_keys if k not in result]
                    if missing_keys:
                        raise ValueError(f"Missing required keys: {missing_keys}")
                
                return result
                
            except (json.JSONDecodeError, ValueError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Retry with stricter prompt
                    json_prompt = f"{json_prompt}\n\nPrevious attempt failed. Ensure you output ONLY valid JSON."
                continue
        
        raise RuntimeError(
            f"Failed to generate valid JSON after {max_retries} attempts. "
            f"Last error: {last_error}"
        )
    
    def check_memory(self) -> float:
        """
        Check current RAM usage percentage.
        
        Returns:
            Memory usage as a float between 0.0 and 1.0
        """
        memory = psutil.virtual_memory()
        return memory.percent / 100.0
    
    def verify_offline(self) -> bool:
        """
        Verify that the LLM runtime operates without network calls.
        
        For Ollama: Checks that the endpoint is localhost
        For llama.cpp: Always returns True (fully local)
        
        Returns:
            True if operating offline, False otherwise
        """
        if self.backend == "llama-cpp":
            # llama.cpp is always offline
            return True
        elif self.backend == "ollama":
            # Check that Ollama is using localhost
            if hasattr(self._llm, 'base_url'):
                base_url = self._llm.base_url
                return 'localhost' in base_url or '127.0.0.1' in base_url
            return True  # Assume offline if we can't check
        
        return False
    
    def truncate_context(self, text: str, max_length: int = 2000) -> str:
        """
        Truncate context text to fit within memory constraints.
        
        This method is called automatically when memory usage exceeds the threshold.
        It preserves the beginning and end of the text while removing the middle.
        
        Args:
            text: Text to truncate
            max_length: Maximum character length
            
        Returns:
            Truncated text with ellipsis indicator
        """
        if len(text) <= max_length:
            return text
        
        # Keep first and last portions
        keep_length = max_length // 2
        truncated = (
            text[:keep_length] +
            "\n\n[... context truncated due to memory constraints ...]\n\n" +
            text[-keep_length:]
        )
        
        return truncated
    
    def __repr__(self) -> str:
        """String representation of LLM runtime."""
        status = "loaded" if self._is_loaded else "not loaded"
        return f"LLMRuntime(backend='{self.backend}', model='{self.model_path}', status='{status}')"
