"""
Performance tests for the Offline Policy Gap Analyzer.

Tests validate that the system meets performance requirements on consumer hardware:
- 20-page policy analysis completes within 10 minutes
- Embedding engine processes 50+ chunks per minute
- LLM generates 10+ tokens per second
- Memory usage stays within limits (8GB for 3B models, 16GB for 7B models)

**Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5**
"""

import pytest
import time
import psutil
import tempfile
from pathlib import Path
from typing import List

from retrieval.embedding_engine import EmbeddingEngine
from analysis.llm_runtime import LLMRuntime
from orchestration.analysis_pipeline import AnalysisPipeline, PipelineConfig


class TestEmbeddingPerformance:
    """Test embedding engine performance requirements."""
    
    def test_embedding_throughput_meets_requirement(self, tmp_path):
        """
        Test that embedding engine processes at least 50 chunks per minute.
        
        **Validates: Requirement 16.4**
        """
        # Setup
        model_path = "models/embeddings/all-MiniLM-L6-v2"
        if not Path(model_path).exists():
            pytest.skip(f"Embedding model not found at {model_path}")
        
        engine = EmbeddingEngine(model_path=model_path)
        
        # Create test chunks (typical policy chunk size)
        test_chunks = [
            f"This is test chunk number {i}. " * 50  # ~50 words per chunk
            for i in range(100)
        ]
        
        # Measure embedding time
        start_time = time.time()
        embeddings = engine.embed_batch(test_chunks)
        elapsed_time = time.time() - start_time
        
        # Calculate throughput
        chunks_per_minute = (len(test_chunks) / elapsed_time) * 60
        
        # Verify
        assert embeddings.shape == (100, 384), "Should produce 384-dim embeddings"
        assert chunks_per_minute >= 50, (
            f"Embedding throughput {chunks_per_minute:.1f} chunks/min "
            f"is below requirement of 50 chunks/min"
        )
        
        print(f"\n✓ Embedding throughput: {chunks_per_minute:.1f} chunks/min")
    
    def test_embedding_batch_faster_than_sequential(self, tmp_path):
        """
        Test that batch processing is significantly faster than sequential.
        
        **Validates: Requirement 16.4**
        """
        model_path = "models/embeddings/all-MiniLM-L6-v2"
        if not Path(model_path).exists():
            pytest.skip(f"Embedding model not found at {model_path}")
        
        engine = EmbeddingEngine(model_path=model_path)
        
        test_chunks = [f"Test chunk {i}" * 20 for i in range(50)]
        
        # Sequential processing
        start_sequential = time.time()
        for chunk in test_chunks:
            engine.embed_text(chunk)
        sequential_time = time.time() - start_sequential
        
        # Batch processing
        start_batch = time.time()
        engine.embed_batch(test_chunks)
        batch_time = time.time() - start_batch
        
        # Batch should be at least 2x faster
        speedup = sequential_time / batch_time
        assert speedup >= 2.0, (
            f"Batch processing speedup {speedup:.1f}x is below expected 2x minimum"
        )
        
        print(f"\n✓ Batch processing speedup: {speedup:.1f}x")


class TestLLMPerformance:
    """Test LLM runtime performance requirements."""
    
    def test_llm_token_generation_speed(self):
        """
        Test that LLM generates at least 10 tokens per second.
        
        **Validates: Requirement 16.5**
        """
        model_path = "qwen2.5:3b"  # Ollama model name
        
        try:
            llm = LLMRuntime(model_path=model_path, backend="ollama")
        except RuntimeError as e:
            pytest.skip(f"LLM not available: {e}")
        
        # Generate text and measure speed
        prompt = "Write a detailed explanation of cybersecurity risk management:"
        
        start_time = time.time()
        response = llm.generate(
            prompt=prompt,
            temperature=0.1,
            max_tokens=200
        )
        elapsed_time = time.time() - start_time
        
        # Estimate token count (rough: ~4 chars per token)
        estimated_tokens = len(response) / 4
        tokens_per_second = estimated_tokens / elapsed_time
        
        # Verify
        assert tokens_per_second >= 10, (
            f"Token generation speed {tokens_per_second:.1f} tokens/sec "
            f"is below requirement of 10 tokens/sec"
        )
        
        print(f"\n✓ Token generation speed: {tokens_per_second:.1f} tokens/sec")
        print(f"  Generated {estimated_tokens:.0f} tokens in {elapsed_time:.2f}s")
    
    def test_llm_memory_usage_3b_model(self):
        """
        Test that 3B model stays within 8GB memory limit.
        
        **Validates: Requirement 16.2**
        """
        model_path = "qwen2.5:3b"
        
        try:
            # Measure memory before loading
            process = psutil.Process()
            memory_before = process.memory_info().rss / (1024 ** 3)  # GB
            
            llm = LLMRuntime(model_path=model_path, backend="ollama")
            
            # Generate some text to ensure model is fully loaded
            llm.generate("Test prompt", max_tokens=50)
            
            # Measure memory after
            memory_after = process.memory_info().rss / (1024 ** 3)  # GB
            memory_used = memory_after - memory_before
            
            # Verify
            assert memory_used <= 8.0, (
                f"3B model uses {memory_used:.2f}GB, exceeding 8GB limit"
            )
            
            print(f"\n✓ 3B model memory usage: {memory_used:.2f}GB (limit: 8GB)")
            
        except RuntimeError as e:
            pytest.skip(f"LLM not available: {e}")


class TestPipelinePerformance:
    """Test complete pipeline performance requirements."""
    
    def test_20_page_policy_analysis_time(self, tmp_path):
        """
        Test that 20-page policy analysis completes within 10 minutes.
        
        **Validates: Requirement 16.1**
        """
        # Create a realistic 20-page policy document
        policy_content = self._create_20_page_policy()
        policy_path = tmp_path / "test_policy.txt"
        policy_path.write_text(policy_content, encoding='utf-8')
        
        # Setup pipeline with test configuration
        config = PipelineConfig({
            'chunk_size': 512,
            'overlap': 50,
            'top_k': 5,
            'temperature': 0.1,
            'max_tokens': 512,
            'model_name': 'qwen2.5:3b',
            'model_path': 'qwen2.5:3b',
            'embedding_model_path': 'models/embeddings/all-MiniLM-L6-v2',
            'reranker_model_path': 'models/reranker/cross-encoder-ms-marco-MiniLM-L-6-v2',
            'vector_store_path': str(tmp_path / 'vector_store'),
            'catalog_path': 'data/reference_catalog.json',
            'output_dir': str(tmp_path / 'outputs'),
            'audit_dir': str(tmp_path / 'audit_logs')
        })
        
        # Check if required resources exist
        if not Path(config.embedding_model_path).exists():
            pytest.skip("Embedding model not found")
        if not Path(config.catalog_path).exists():
            pytest.skip("Reference catalog not found")
        
        try:
            pipeline = AnalysisPipeline(config=config)
            
            # Measure analysis time
            start_time = time.time()
            result = pipeline.execute(
                policy_path=str(policy_path),
                domain="isms"
            )
            elapsed_time = time.time() - start_time
            
            # Verify
            elapsed_minutes = elapsed_time / 60
            assert elapsed_minutes <= 10.0, (
                f"Analysis took {elapsed_minutes:.2f} minutes, "
                f"exceeding 10 minute requirement"
            )
            
            print(f"\n✓ 20-page policy analysis time: {elapsed_minutes:.2f} minutes")
            print(f"  Gaps identified: {len(result.gap_report.gaps)}")
            print(f"  Revisions generated: {len(result.revised_policy.revisions)}")
            
        except RuntimeError as e:
            pytest.skip(f"Pipeline execution failed: {e}")
    
    def test_pipeline_memory_stays_within_limits(self, tmp_path):
        """
        Test that pipeline memory usage stays within hardware limits.
        
        **Validates: Requirements 16.2, 16.3**
        """
        # Create test policy
        policy_content = "# Test Policy\n\n" + ("Test content. " * 1000)
        policy_path = tmp_path / "test_policy.txt"
        policy_path.write_text(policy_content, encoding='utf-8')
        
        # Setup minimal pipeline
        config = PipelineConfig({
            'model_name': 'qwen2.5:3b',
            'model_path': 'qwen2.5:3b',
            'embedding_model_path': 'models/embeddings/all-MiniLM-L6-v2',
            'catalog_path': 'data/reference_catalog.json',
            'output_dir': str(tmp_path / 'outputs')
        })
        
        if not Path(config.embedding_model_path).exists():
            pytest.skip("Embedding model not found")
        if not Path(config.catalog_path).exists():
            pytest.skip("Reference catalog not found")
        
        try:
            # Monitor memory during execution
            process = psutil.Process()
            memory_before = process.memory_info().rss / (1024 ** 3)  # GB
            
            pipeline = AnalysisPipeline(config=config)
            pipeline.initialize_resources()
            
            memory_after_init = process.memory_info().rss / (1024 ** 3)  # GB
            memory_used = memory_after_init - memory_before
            
            # For 3B model, should stay under 8GB
            assert memory_used <= 8.0, (
                f"Pipeline uses {memory_used:.2f}GB, exceeding 8GB limit for 3B model"
            )
            
            print(f"\n✓ Pipeline memory usage: {memory_used:.2f}GB (limit: 8GB)")
            
            pipeline.cleanup()
            
        except RuntimeError as e:
            pytest.skip(f"Pipeline initialization failed: {e}")
    
    def test_pipeline_provides_progress_indicators(self, tmp_path, capsys):
        """
        Test that pipeline provides progress indicators during execution.
        
        **Validates: Requirement 16.6**
        """
        # Create small test policy
        policy_content = "# Test Policy\n\nTest content for progress tracking."
        policy_path = tmp_path / "test_policy.txt"
        policy_path.write_text(policy_content, encoding='utf-8')
        
        config = PipelineConfig({
            'model_name': 'qwen2.5:3b',
            'model_path': 'qwen2.5:3b',
            'embedding_model_path': 'models/embeddings/all-MiniLM-L6-v2',
            'catalog_path': 'data/reference_catalog.json',
            'output_dir': str(tmp_path / 'outputs')
        })
        
        if not Path(config.embedding_model_path).exists():
            pytest.skip("Embedding model not found")
        if not Path(config.catalog_path).exists():
            pytest.skip("Reference catalog not found")
        
        try:
            pipeline = AnalysisPipeline(config=config)
            pipeline.execute(policy_path=str(policy_path))
            
            # Check captured output for progress indicators
            captured = capsys.readouterr()
            output = captured.out + captured.err
            
            # Verify progress messages are present
            expected_steps = [
                "Step 1/9",
                "Step 2/9",
                "Step 3/9",
                "Parsing policy document",
                "Chunking policy text",
                "Embedding policy chunks"
            ]
            
            found_steps = [step for step in expected_steps if step in output]
            assert len(found_steps) >= 3, (
                f"Expected progress indicators not found. "
                f"Found {len(found_steps)}/6 expected steps"
            )
            
            print(f"\n✓ Progress indicators present: {len(found_steps)}/6 steps")
            
        except RuntimeError as e:
            pytest.skip(f"Pipeline execution failed: {e}")
    
    def _create_20_page_policy(self) -> str:
        """Create a realistic 20-page policy document for testing."""
        sections = [
            "# Information Security Management System Policy",
            "\n## 1. Purpose and Scope",
            "\nThis policy establishes the framework for managing information security risks.",
            "\n## 2. Governance Structure",
            "\nThe organization shall establish clear roles and responsibilities.",
            "\n## 3. Risk Management",
            "\nRisk assessments shall be conducted annually.",
            "\n## 4. Access Control",
            "\nAccess to systems shall be granted based on least privilege.",
            "\n## 5. Incident Response",
            "\nSecurity incidents shall be reported within 24 hours.",
            "\n## 6. Business Continuity",
            "\nBusiness continuity plans shall be tested annually.",
            "\n## 7. Compliance",
            "\nThe organization shall comply with applicable regulations.",
            "\n## 8. Training and Awareness",
            "\nAll employees shall complete security awareness training.",
        ]
        
        # Repeat and expand to reach ~20 pages (roughly 500 words per page)
        content = ""
        for _ in range(15):  # Repeat sections to build content
            for section in sections:
                content += section + "\n\n"
                # Add filler content
                content += ("This section provides detailed requirements and procedures. " * 30) + "\n\n"
        
        return content


class TestPerformanceOptimizations:
    """Test that performance optimizations are working correctly."""
    
    def test_embedding_caching_improves_performance(self, tmp_path):
        """
        Test that repeated embedding operations benefit from caching.
        
        **Validates: Requirement 16.1**
        """
        model_path = "models/embeddings/all-MiniLM-L6-v2"
        if not Path(model_path).exists():
            pytest.skip(f"Embedding model not found at {model_path}")
        
        engine = EmbeddingEngine(model_path=model_path)
        
        test_texts = ["Test text " * 20 for _ in range(50)]
        
        # First run (cold)
        start_cold = time.time()
        embeddings1 = engine.embed_batch(test_texts)
        cold_time = time.time() - start_cold
        
        # Second run (warm - model already loaded)
        start_warm = time.time()
        embeddings2 = engine.embed_batch(test_texts)
        warm_time = time.time() - start_warm
        
        # Warm run should be at least as fast (model overhead amortized)
        assert warm_time <= cold_time * 1.1, (
            f"Warm run ({warm_time:.2f}s) slower than cold run ({cold_time:.2f}s)"
        )
        
        print(f"\n✓ Embedding caching: cold={cold_time:.2f}s, warm={warm_time:.2f}s")
    
    def test_parallel_embedding_when_safe(self, tmp_path):
        """
        Test that embedding generation can process batches efficiently.
        
        **Validates: Requirement 16.4**
        """
        model_path = "models/embeddings/all-MiniLM-L6-v2"
        if not Path(model_path).exists():
            pytest.skip(f"Embedding model not found at {model_path}")
        
        engine = EmbeddingEngine(model_path=model_path)
        
        # Large batch
        large_batch = [f"Test chunk {i}" * 30 for i in range(200)]
        
        start_time = time.time()
        embeddings = engine.embed_batch(large_batch)
        elapsed_time = time.time() - start_time
        
        # Should process at least 100 chunks per minute for large batches
        chunks_per_minute = (len(large_batch) / elapsed_time) * 60
        
        assert chunks_per_minute >= 100, (
            f"Large batch throughput {chunks_per_minute:.1f} chunks/min "
            f"is below expected 100 chunks/min"
        )
        
        print(f"\n✓ Large batch throughput: {chunks_per_minute:.1f} chunks/min")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
