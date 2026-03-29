# LLM Runtime Component

## Overview

The LLM Runtime component provides a unified interface for executing quantized language models locally using either llama.cpp or Ollama backends. It supports offline operation, memory monitoring, context truncation, and structured JSON output generation.

## Features

- **Multi-Backend Support**: Works with both Ollama and llama.cpp
- **Offline Operation**: All inference happens locally without network calls
- **Memory Monitoring**: Tracks RAM usage and prevents OOM crashes
- **Context Truncation**: Automatically truncates context at 90% RAM threshold
- **Structured Output**: Generates JSON conforming to specified schemas
- **Low Temperature**: Defaults to 0.1 for deterministic, factual outputs

## Supported Models

The system supports multiple quantized models in GGUF format:

### Recommended Models

1. **Qwen2.5-3B-Instruct** (Default)
   - Size: ~2GB (4-bit quantization)
   - RAM Required: 8GB
   - Context Window: 32k tokens
   - Best for: General policy analysis

2. **Phi-3.5-mini-instruct**
   - Size: ~2.3GB (4-bit quantization)
   - RAM Required: 8GB
   - Context Window: 128k tokens
   - Best for: Long document analysis

3. **Mistral-7B-Instruct**
   - Size: ~4GB (4-bit quantization)
   - RAM Required: 16GB
   - Context Window: 32k tokens
   - Best for: Complex reasoning tasks

4. **Qwen3-8B-Instruct**
   - Size: ~4.5GB (4-bit quantization)
   - RAM Required: 16GB
   - Context Window: 131k tokens
   - Best for: Very long policies

## Installation

### Option 1: Ollama (Recommended)

1. Install Ollama from https://ollama.ai

2. Pull a model:
```bash
ollama pull qwen2.5:3b-instruct
```

3. Verify installation:
```bash
ollama list
```

### Option 2: llama.cpp

1. Install llama-cpp-python:
```bash
pip install llama-cpp-python
```

2. Download GGUF model files from HuggingFace:
```bash
# Example: Download Qwen2.5-3B-Instruct
wget https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf
mv qwen2.5-3b-instruct-q4_k_m.gguf ./models/
```

## Usage

### Basic Text Generation

```python
from analysis.llm_runtime import LLMRuntime

# Initialize with Ollama
runtime = LLMRuntime(
    model_path="qwen2.5:3b-instruct",
    backend="ollama"
)

# Generate text
response = runtime.generate(
    prompt="What is risk management?",
    temperature=0.1,
    max_tokens=200
)

print(response)
```

### Structured JSON Output

```python
# Define output schema
schema = {
    "type": "object",
    "properties": {
        "status": {"type": "string"},
        "explanation": {"type": "string"},
        "severity": {"type": "string"}
    },
    "required": ["status", "explanation", "severity"]
}

# Generate structured output
result = runtime.generate_structured(
    prompt="Analyze this policy for risk management coverage...",
    schema=schema,
    temperature=0.1,
    max_tokens=300
)

print(result)
# Output: {"status": "partially_covered", "explanation": "...", "severity": "high"}
```

### Memory Monitoring

```python
# Check current memory usage
memory_usage = runtime.check_memory()
print(f"Memory usage: {memory_usage:.1%}")

# Truncate context if needed
long_text = "..." * 10000
truncated = runtime.truncate_context(long_text, max_length=2000)
```

### Offline Verification

```python
# Verify offline operation
is_offline = runtime.verify_offline()
assert is_offline, "Runtime should operate offline"
```

## Configuration

The LLM runtime can be configured via `config.yaml`:

```yaml
llm:
  temperature: 0.1      # Low for deterministic outputs
  max_tokens: 512       # Maximum generation length
  model_name: "qwen2.5:3b-instruct"
  backend: "ollama"     # "ollama" or "llama-cpp"
```

## Memory Requirements

| Model Size | Quantization | RAM Required | Recommended Use |
|------------|--------------|--------------|-----------------|
| 3B params  | 4-bit (Q4)   | 8GB          | Consumer laptops |
| 7B params  | 4-bit (Q4)   | 16GB         | Workstations |
| 8B params  | 4-bit (Q4)   | 16GB         | Long documents |

## Performance

On consumer hardware (M1 MacBook Air, 8GB RAM):

- **Qwen2.5-3B**: ~15-20 tokens/second
- **Phi-3.5-mini**: ~12-18 tokens/second
- **Mistral-7B**: ~8-12 tokens/second (requires 16GB RAM)

## Error Handling

The runtime includes comprehensive error handling:

```python
try:
    runtime = LLMRuntime(
        model_path="nonexistent-model",
        backend="ollama"
    )
except RuntimeError as e:
    print(f"Model loading failed: {e}")
    # Error includes troubleshooting steps
```

Common errors:

1. **Model not found**: Run `ollama pull <model-name>`
2. **Ollama not running**: Start Ollama service
3. **Out of memory**: Use smaller model or increase RAM
4. **Invalid JSON**: Retry with stricter schema prompt

## Testing

Run tests without models:
```bash
pytest tests/unit/test_llm_runtime.py::TestErrorHandling -v
```

Run tests with Ollama (requires model):
```bash
ollama pull qwen2.5:3b-instruct
pytest tests/unit/test_llm_runtime.py -v
```

Run property tests:
```bash
pytest tests/property/test_llm_runtime.py -v
```

## Integration with Gap Analysis

The LLM runtime is used in Stage B of the gap analysis pipeline:

```python
from analysis.llm_runtime import LLMRuntime
from analysis.gap_analysis_engine import GapAnalysisEngine

# Initialize runtime
llm = LLMRuntime(
    model_path="qwen2.5:3b-instruct",
    backend="ollama"
)

# Use in gap analysis
engine = GapAnalysisEngine(
    retriever=retriever,
    llm=llm,
    catalog=catalog
)

# Stage B uses structured output for gap details
gap_report = engine.analyze(policy_chunks)
```

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Memory Issues

```python
# Monitor memory during generation
runtime.memory_threshold = 0.85  # Lower threshold

# Use context truncation
prompt = runtime.truncate_context(long_prompt, max_length=1500)
```

### Slow Generation

- Use smaller model (3B instead of 7B)
- Reduce max_tokens parameter
- Close other applications to free RAM

## Future Enhancements

Planned improvements:

1. **Streaming Output**: Support for token-by-token streaming
2. **Batch Processing**: Process multiple prompts in parallel
3. **Model Caching**: Cache loaded models for faster initialization
4. **GPU Support**: Optional GPU acceleration for faster inference
5. **Quantization Options**: Support for 8-bit and 2-bit quantization

## References

- [Ollama Documentation](https://ollama.ai/docs)
- [llama.cpp GitHub](https://github.com/ggerganov/llama.cpp)
- [LangChain LLM Integration](https://python.langchain.com/docs/integrations/llms/)
- [GGUF Format Specification](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)
