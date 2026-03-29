# Troubleshooting Guide

This guide provides solutions to common issues encountered when using the Offline Policy Gap Analyzer.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Model Loading Failures](#model-loading-failures)
- [Memory Issues](#memory-issues)
- [Parsing Failures](#parsing-failures)
- [Analysis Errors](#analysis-errors)
- [Performance Issues](#performance-issues)
- [Configuration Problems](#configuration-problems)
- [FAQ](#faq)

## Installation Issues

### Python Version Compatibility

**Problem**: Installation fails with Python 3.14+

**Error Message**:
```
ERROR: Could not find a version that satisfies the requirement chromadb>=0.5.0
```

**Solution**:
```bash
# Use Python 3.11 or 3.12
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Explanation**: ChromaDB has known compatibility issues with Python 3.14+. Use Python 3.11 or 3.12.

### ChromaDB Installation Fails

**Problem**: ChromaDB installation fails with compilation errors

**Error Message**:
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Solution (Windows)**:
```bash
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/

# Or use conda
conda install -c conda-forge chromadb
```

**Solution (Linux/macOS)**:
```bash
# Install with specific version
pip install chromadb==0.5.0

# Or use conda
conda install -c conda-forge chromadb
```

### llama-cpp-python Compilation Errors

**Problem**: llama-cpp-python fails to compile

**Error Message**:
```
error: command 'gcc' failed with exit status 1
```

**Solution 1 (Use Pre-built Wheels)**:
```bash
# Install pre-built CPU version
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

**Solution 2 (Use Ollama Instead)**:
```bash
# Ollama doesn't require compilation
pip install ollama-python

# Install Ollama separately
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh
# Windows: Download from https://ollama.com/download
```

**Solution 3 (Install Build Tools)**:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS
xcode-select --install

# Windows
# Install Visual Studio Build Tools
```

### Dependency Conflicts

**Problem**: Conflicting dependency versions

**Error Message**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**Solution**:
```bash
# Create fresh virtual environment
python -m venv venv_fresh
source venv_fresh/bin/activate

# Install in order
pip install --upgrade pip
pip install -r requirements.txt
```

## Model Loading Failures

### Model Files Not Found

**Problem**: System cannot find model files

**Error Message**:
```
ModelNotFoundError: Model file not found at models/llm/qwen2.5-3b-instruct.gguf
```

**Solution**:
```bash
# Download models
python scripts/download_models.py --all

# Verify model files exist
ls -lh models/llm/
ls -lh models/embeddings/
ls -lh models/reranker/

# Check model integrity
python scripts/download_models.py --verify
```

**Manual Download**:
If automatic download fails, download models manually:

1. **Embedding Model**: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
2. **Reranker Model**: https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2
3. **LLM Models**: https://huggingface.co/models?search=gguf

Place files in the appropriate `models/` subdirectories.

### Ollama Connection Failed

**Problem**: Cannot connect to Ollama

**Error Message**:
```
RuntimeError: Failed to connect to Ollama at http://localhost:11434
```

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama (if not running)
ollama serve

# Pull required model
ollama pull qwen2.5:3b-instruct

# Verify model is available
ollama list
```

### Corrupted Model Files

**Problem**: Model files are corrupted or incomplete

**Error Message**:
```
RuntimeError: Failed to load model: invalid GGUF file
```

**Solution**:
```bash
# Remove corrupted files
rm -rf models/llm/*.gguf

# Re-download models
python scripts/download_models.py --all --force

# Verify checksums
python scripts/download_models.py --verify
```

## Memory Issues

### Out of Memory Errors

**Problem**: System runs out of memory during analysis

**Error Message**:
```
MemoryError: Cannot allocate memory for context
```

**Solution 1 (Use Smaller Model)**:
```bash
# Use 3B model instead of 7B
policy-analyzer --policy-path policy.pdf --model qwen2.5-3b
```

**Solution 2 (Reduce Configuration Parameters)**:
```yaml
# config.yaml
chunk_size: 256  # Reduced from 512
top_k: 3  # Reduced from 5
max_tokens: 256  # Reduced from 512
```

**Solution 3 (Close Other Applications)**:
```bash
# Check memory usage
free -h  # Linux
vm_stat  # macOS

# Close unnecessary applications
# Restart system if needed
```

**Solution 4 (Split Large Policies)**:
```bash
# Split policy into sections
# Analyze each section separately
policy-analyzer --policy-path section1.pdf
policy-analyzer --policy-path section2.pdf
```

### Context Truncation Warning

**Problem**: Context truncated due to memory limits

**Warning Message**:
```
WARNING: Memory usage at 92%. Truncating context to prevent crash.
```

**Solution**:
```bash
# This is expected behavior on memory-constrained systems
# To avoid truncation:

# 1. Use system with more RAM (16GB recommended)
# 2. Reduce chunk_size in configuration
# 3. Split large policies into smaller sections
# 4. Close other applications
```

### Slow Performance Due to Swapping

**Problem**: System is swapping to disk, causing slow performance

**Symptoms**:
- Analysis takes much longer than expected
- High disk activity
- System becomes unresponsive

**Solution**:
```bash
# Check swap usage
free -h  # Linux
vm_stat  # macOS

# If swap usage is high:
# 1. Close other applications
# 2. Use smaller model
# 3. Reduce configuration parameters
# 4. Add more RAM to system
```

## Parsing Failures

### OCR-Required PDF Rejected

**Problem**: PDF contains only scanned images

**Error Message**:
```
OCRRequiredError: This PDF contains only scanned images. OCR is not supported. Please provide a text-based PDF.
```

**Solution**:
```bash
# Option 1: Use external OCR tool
# - Adobe Acrobat Pro (commercial)
# - Tesseract OCR (open source)
# - Online OCR services

# Option 2: Request original digital document
# Contact policy author for text-based version

# Option 3: Manual transcription
# Copy text to DOCX or TXT file
```

### Complex Table Extraction Issues

**Problem**: Tables not extracted correctly from PDF

**Symptoms**:
- Missing table content in analysis
- Garbled table text
- Incorrect gap detection in table sections

**Solution**:
```bash
# Option 1: Convert to DOCX
# Use Microsoft Word or LibreOffice to convert PDF to DOCX
# DOCX preserves table structure better

# Option 2: Simplify tables
# Recreate complex tables in simpler format
# Use plain text instead of nested tables

# Option 3: Manual review
# Review extracted text in output logs
# Manually verify table content coverage
```

### Unsupported File Format

**Problem**: File format not supported

**Error Message**:
```
UnsupportedFormatError: File format '.odt' not supported. Supported formats: PDF, DOCX, TXT
```

**Solution**:
```bash
# Convert to supported format:

# ODT to DOCX
libreoffice --headless --convert-to docx file.odt

# RTF to DOCX
# Use Microsoft Word or LibreOffice

# HTML to PDF
# Use browser "Print to PDF" feature

# Then analyze converted file
policy-analyzer --policy-path converted_file.docx
```

### Document Too Large

**Problem**: Policy exceeds 100-page limit

**Error Message**:
```
ParsingError: Document exceeds maximum page limit of 100 pages
```

**Solution**:
```bash
# Split document into logical sections
# Example: ISMS policy split into:
# - isms_governance.pdf (pages 1-40)
# - isms_technical.pdf (pages 41-80)
# - isms_operational.pdf (pages 81-100)

# Analyze each section
policy-analyzer --policy-path isms_governance.pdf --domain isms
policy-analyzer --policy-path isms_technical.pdf --domain isms
policy-analyzer --policy-path isms_operational.pdf --domain isms

# Manually consolidate gap reports
```

## Analysis Errors

### Reference Catalog Not Built

**Problem**: Reference catalog not found

**Error Message**:
```
FileNotFoundError: Reference catalog not found at context/reference_catalog.json
```

**Solution**:
```bash
# Build reference catalog
python scripts/build_catalog.py

# Verify catalog exists
ls -lh context/reference_catalog.json

# If CIS guide PDF is missing
# Download from CIS website or use provided copy
```

### Vector Store Initialization Failed

**Problem**: Cannot initialize vector store

**Error Message**:
```
RuntimeError: Failed to initialize ChromaDB vector store
```

**Solution**:
```bash
# Check ChromaDB installation
python -c "import chromadb; print(chromadb.__version__)"

# Remove corrupted vector store
rm -rf .chroma/

# Reinstall ChromaDB
pip uninstall chromadb
pip install chromadb==0.5.0

# Retry analysis
policy-analyzer --policy-path policy.pdf
```

### LLM Generation Timeout

**Problem**: LLM generation takes too long or times out

**Error Message**:
```
TimeoutError: LLM generation exceeded maximum time limit
```

**Solution**:
```bash
# Reduce max_tokens in configuration
# config.yaml
max_tokens: 256  # Reduced from 512

# Use faster model
policy-analyzer --policy-path policy.pdf --model qwen2.5-3b

# Check system resources
top  # Linux/macOS
# Ensure CPU is not throttled due to thermal limits
```

### Retrieval Returns No Results

**Problem**: Hybrid retrieval returns no matching subcategories

**Symptoms**:
- Gap report shows all subcategories as "Missing"
- No evidence spans in output

**Solution**:
```bash
# Check if policy has sufficient content
wc -w policy.txt  # Should have at least 500 words

# Verify embeddings are generated
# Check logs for embedding generation messages

# Try different domain
policy-analyzer --policy-path policy.pdf --domain isms

# Manually review policy content
# Ensure policy uses cybersecurity terminology
```

## Performance Issues

### Analysis Takes Too Long

**Problem**: Analysis exceeds expected time (>10 minutes for 20-page policy)

**Symptoms**:
- Progress indicators move very slowly
- High CPU usage
- System becomes sluggish

**Solution**:
```bash
# Check system resources
top  # Linux/macOS

# Use faster model
policy-analyzer --policy-path policy.pdf --model qwen2.5-3b

# Reduce configuration parameters
# config.yaml
chunk_size: 256
top_k: 3
max_tokens: 256

# Close other applications
# Ensure CPU is not thermal throttling
```

### Embedding Generation Slow

**Problem**: Embedding generation takes longer than expected

**Expected**: ~100 chunks/minute
**Actual**: <50 chunks/minute

**Solution**:
```bash
# Check CPU usage
top  # Should show high CPU usage during embedding

# Ensure numpy is using optimized BLAS
python -c "import numpy; numpy.show_config()"

# Install optimized numpy (if needed)
pip uninstall numpy
pip install numpy[mkl]  # Intel MKL acceleration

# Use batch processing (already default)
# Verify in logs: "Processing batch of 32 chunks"
```

### LLM Generation Slow

**Problem**: LLM generates fewer than 10 tokens/second

**Solution**:
```bash
# Use smaller model
policy-analyzer --policy-path policy.pdf --model qwen2.5-3b

# Check if Ollama is using CPU correctly
ollama ps  # Should show model loaded

# Ensure no other processes using CPU
top

# Consider using llama.cpp with optimizations
# See docs/MODEL_SETUP.md for advanced configuration
```

## Configuration Problems

### Configuration File Not Found

**Problem**: Custom configuration file not loaded

**Error Message**:
```
FileNotFoundError: Configuration file not found: custom.yaml
```

**Solution**:
```bash
# Check file path
ls -lh custom.yaml

# Use absolute path
policy-analyzer --policy-path policy.pdf --config /full/path/to/custom.yaml

# Or use default configuration
policy-analyzer --policy-path policy.pdf
```

### Invalid Configuration Values

**Problem**: Configuration contains invalid values

**Error Message**:
```
ValueError: Invalid configuration: chunk_size must be between 128 and 1024
```

**Solution**:
```yaml
# Fix configuration values
# config.yaml

# Valid ranges:
chunk_size: 512  # 128-1024
overlap: 50  # 0-256
top_k: 5  # 1-20
temperature: 0.1  # 0.0-1.0
max_tokens: 512  # 128-2048
```

### Configuration Not Applied

**Problem**: Configuration changes not taking effect

**Solution**:
```bash
# Verify configuration file is being loaded
policy-analyzer --policy-path policy.pdf --config config.yaml --verbose

# Check logs for "Loaded configuration from: config.yaml"

# Ensure no typos in parameter names
# Use config.example.yaml as reference
```

## FAQ

### Q: How do I know if the system is running offline?

**A**: Check the logs for network activity warnings:
```bash
policy-analyzer --policy-path policy.pdf --verbose 2>&1 | grep -i network
```

If no network warnings appear, the system is operating offline.

You can also disable network to verify:
```bash
# Disable network
sudo ifconfig en0 down  # macOS
sudo ip link set eth0 down  # Linux

# Run analysis
policy-analyzer --policy-path policy.pdf

# Re-enable network
sudo ifconfig en0 up  # macOS
sudo ip link set eth0 up  # Linux
```

### Q: Why are some gaps marked as "Ambiguous"?

**A**: Ambiguous gaps occur when:
- Policy language is unclear or vague
- Coverage score falls between 0.3 and 0.5 (neither clearly covered nor missing)
- Multiple interpretations are possible

**Action**: Manually review ambiguous gaps and clarify policy language.

### Q: Can I use GPU acceleration?

**A**: Yes, but it requires additional setup:

```bash
# Install llama-cpp-python with CUDA support
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python

# Or use Ollama with GPU
# Ollama automatically detects and uses GPU if available

# Verify GPU is being used
nvidia-smi  # Should show model process
```

### Q: How do I update models?

**A**: Re-run the download script:

```bash
# Download latest models
python scripts/download_models.py --all --force

# Verify new models
python scripts/download_models.py --verify
```

### Q: Can I analyze multiple policies at once?

**A**: Yes, use a shell script:

```bash
#!/bin/bash
for policy in policies/*.pdf; do
    policy-analyzer --policy-path "$policy" --domain isms
done
```

### Q: How do I interpret the gap severity levels?

**A**: Severity levels are based on CSF subcategory priority:

- **Critical**: Core governance and risk management (GV.RM, GV.OV)
- **High**: Essential security controls (ID.RA, PR.DS, PR.AA)
- **Medium**: Important but not critical (PR.PS, DE.CM)
- **Low**: Supplementary controls (RC.RP, RC.CO)

### Q: What if my policy uses different terminology than NIST CSF?

**A**: The hybrid retrieval system handles terminology variations through:
- Semantic similarity (understands synonyms)
- Keyword matching (exact terms)
- Cross-encoder reranking (improves precision)

However, very different terminology may reduce accuracy. Consider:
- Aligning policy language with NIST CSF 2.0 terminology
- Manually reviewing gap reports for missed provisions
- Updating Reference Catalog keywords

### Q: How do I report a bug?

**A**: Submit an issue on GitHub with:
1. Description of the problem
2. Steps to reproduce
3. Error messages and logs
4. System configuration (OS, RAM, Python version)
5. Sample policy (if not sensitive)

## Getting Help

If you cannot resolve an issue using this guide:

1. **Check Documentation**:
   - [README.md](../README.md) - Quick start and overview
   - [LIMITATIONS.md](LIMITATIONS.md) - Known limitations
   - [DEPENDENCIES.md](DEPENDENCIES.md) - Dependency information

2. **Review Logs**:
   - Check `outputs/*/analysis.log` for detailed error messages
   - Use `--verbose` flag for more detailed output

3. **Search Issues**:
   - Check [GitHub Issues](https://github.com/your-repo/issues) for similar problems

4. **Ask for Help**:
   - Submit a new GitHub issue with detailed information
   - Include logs, configuration, and steps to reproduce

## Debugging Tips

### Enable Verbose Logging

```bash
policy-analyzer --policy-path policy.pdf --verbose
```

### Check System Resources

```bash
# Memory usage
free -h  # Linux
vm_stat  # macOS

# CPU usage
top

# Disk space
df -h

# Process information
ps aux | grep python
```

### Verify Installation

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "chromadb|langchain|sentence-transformers"

# Check model files
ls -lh models/llm/
ls -lh models/embeddings/
ls -lh models/reranker/

# Test imports
python -c "import chromadb; import langchain; import sentence_transformers; print('OK')"
```

### Test Components Individually

```bash
# Test document parser
python -c "from ingestion.document_parser import DocumentParser; parser = DocumentParser(); print('Parser OK')"

# Test embedding engine
python -c "from retrieval.embedding_engine import EmbeddingEngine; engine = EmbeddingEngine('models/embeddings/all-MiniLM-L6-v2'); print('Embeddings OK')"

# Test LLM runtime
python -c "from analysis.llm_runtime import LLMRuntime; llm = LLMRuntime('qwen2.5-3b-instruct'); print('LLM OK')"
```

## Still Having Issues?

If you've tried all troubleshooting steps and still encounter problems:

1. Create a minimal reproducible example
2. Collect all relevant logs and error messages
3. Document your system configuration
4. Submit a detailed issue report on GitHub

We're here to help!
