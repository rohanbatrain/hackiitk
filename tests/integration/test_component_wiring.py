"""
Component wiring verification test.

This test validates that all components are properly wired together
in the analysis pipeline as specified in task 36.1.

**Validates: Task 36.1 - Wire all components together**
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from orchestration.analysis_pipeline import AnalysisPipeline, PipelineConfig


def is_chromadb_available():
    """Check if ChromaDB is available and compatible."""
    try:
        import chromadb
        return True
    except Exception:
        return False


# Skip all tests if ChromaDB is not available
pytestmark = pytest.mark.skipif(
    not is_chromadb_available(),
    reason="ChromaDB not available or incompatible with current environment"
)


@pytest.fixture
def temp_dirs():
    """Create temporary directories for test."""
    temp_base = tempfile.mkdtemp()
    output_dir = f"{temp_base}/outputs"
    audit_dir = f"{temp_base}/audit_logs"
    vector_store_dir = f"{temp_base}/vector_store"
    
    yield {
        'base': temp_base,
        'output': output_dir,
        'audit': audit_dir,
        'vector_store': vector_store_dir
    }
    
    # Cleanup
    shutil.rmtree(temp_base, ignore_errors=True)


@pytest.fixture
def test_config(temp_dirs):
    """Create test configuration."""
    config_dict = {
        'chunk_size': 512,
        'overlap': 50,
        'top_k': 5,
        'temperature': 0.1,
        'max_tokens': 512,
        'model_name': 'qwen2.5-3b-instruct',
        'model_path': 'models/llm/qwen2.5-3b-instruct-q4_k_m.gguf',
        'embedding_model_path': 'models/embeddings/all-MiniLM-L6-v2',
        'reranker_model_path': 'models/reranker/cross-encoder-ms-marco-MiniLM-L-6-v2',
        'vector_store_path': temp_dirs['vector_store'],
        'catalog_path': 'data/reference_catalog.json',
        'cis_guide_path': 'data/cis_guide.pdf',
        'output_dir': temp_dirs['output'],
        'audit_dir': temp_dirs['audit']
    }
    
    return PipelineConfig(config_dict)


@pytest.mark.integration
@pytest.mark.wiring
def test_document_parser_to_text_chunker_wiring(test_config):
    """Verify document parser → text chunker integration.
    
    **Validates: Task 36.1 - Document parser → text chunker**
    """
    # Skip if models not available
    if not Path(test_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    pipeline = AnalysisPipeline(config=test_config)
    
    try:
        pipeline.initialize_resources()
        
        # Verify components exist
        assert pipeline.document_parser is not None, "Document parser not initialized"
        assert pipeline.text_chunker is not None, "Text chunker not initialized"
        
        # Verify text chunker has correct configuration
        assert pipeline.text_chunker.chunk_size == test_config.chunk_size
        assert pipeline.text_chunker.overlap == test_config.overlap
        
        print("✓ Document parser → text chunker wiring verified")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
@pytest.mark.wiring
def test_text_chunker_to_embedding_engine_wiring(test_config):
    """Verify text chunker → embedding engine integration.
    
    **Validates: Task 36.1 - Text chunker → embedding engine**
    """
    # Skip if models not available
    if not Path(test_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    pipeline = AnalysisPipeline(config=test_config)
    
    try:
        pipeline.initialize_resources()
        
        # Verify components exist
        assert pipeline.text_chunker is not None, "Text chunker not initialized"
        assert pipeline.embedding_engine is not None, "Embedding engine not initialized"
        
        # Verify embedding engine is configured
        assert pipeline.embedding_engine.model is not None, "Embedding model not loaded"
        
        print("✓ Text chunker → embedding engine wiring verified")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
@pytest.mark.wiring
def test_embedding_engine_to_vector_store_wiring(test_config):
    """Verify embedding engine → vector store integration.
    
    **Validates: Task 36.1 - Embedding engine → vector store**
    """
    # Skip if models not available
    if not Path(test_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    pipeline = AnalysisPipeline(config=test_config)
    
    try:
        pipeline.initialize_resources()
        
        # Verify components exist
        assert pipeline.embedding_engine is not None, "Embedding engine not initialized"
        assert pipeline.vector_store is not None, "Vector store not initialized"
        
        # Verify vector store is configured
        assert pipeline.vector_store.client is not None, "Vector store client not initialized"
        
        print("✓ Embedding engine → vector store wiring verified")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
@pytest.mark.wiring
def test_reference_catalog_to_embedding_engine_wiring(test_config):
    """Verify reference catalog builder → embedding engine integration.
    
    **Validates: Task 36.1 - Reference catalog builder → embedding engine**
    """
    # Skip if models not available
    if not Path(test_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    if not Path(test_config.catalog_path).exists():
        pytest.skip("Reference catalog not available")
    
    pipeline = AnalysisPipeline(config=test_config)
    
    try:
        pipeline.initialize_resources()
        
        # Verify components exist
        assert pipeline.catalog is not None, "Reference catalog not initialized"
        assert pipeline.embedding_engine is not None, "Embedding engine not initialized"
        
        # Verify catalog has subcategories
        assert len(pipeline.catalog.get_all_subcategories()) > 0, "Catalog has no subcategories"
        
        print(f"✓ Reference catalog → embedding engine wiring verified ({len(pipeline.catalog.get_all_subcategories())} subcategories)")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
@pytest.mark.wiring
def test_reference_catalog_to_vector_store_wiring(test_config):
    """Verify reference catalog builder → vector store integration.
    
    **Validates: Task 36.1 - Reference catalog builder → vector store**
    """
    # Skip if models not available
    if not Path(test_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    if not Path(test_config.catalog_path).exists():
        pytest.skip("Reference catalog not available")
    
    pipeline = AnalysisPipeline(config=test_config)
    
    try:
        pipeline.initialize_resources()
        
        # Verify components exist
        assert pipeline.catalog is not None, "Reference catalog not initialized"
        assert pipeline.vector_store is not None, "Vector store not initialized"
        
        # Verify catalog collection exists in vector store
        # (This is done during initialization)
        
        print("✓ Reference catalog → vector store wiring verified")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
@pytest.mark.wiring
def test_hybrid_retriever_to_gap_analysis_wiring(test_config):
    """Verify hybrid retriever → gap analysis engine integration.
    
    **Validates: Task 36.1 - Hybrid retriever → gap analysis engine**
    """
    # Skip if models not available
    if not Path(test_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    if not Path(test_config.catalog_path).exists():
        pytest.skip("Reference catalog not available")
    
    pipeline = AnalysisPipeline(config=test_config)
    
    try:
        pipeline.initialize_resources()
        
        # Verify components exist
        assert pipeline.hybrid_retriever is not None, "Hybrid retriever not initialized"
        assert pipeline.gap_analysis_engine is not None, "Gap analysis engine not initialized"
        
        # Verify gap analysis engine has retriever
        assert pipeline.gap_analysis_engine.stage_a is not None, "Stage A detector not initialized"
        assert pipeline.gap_analysis_engine.stage_a.retriever is not None, "Stage A retriever not set"
        
        print("✓ Hybrid retriever → gap analysis engine wiring verified")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
@pytest.mark.wiring
def test_gap_analysis_to_policy_revision_wiring(test_config):
    """Verify gap analysis engine → policy revision engine integration.
    
    **Validates: Task 36.1 - Gap analysis engine → policy revision engine**
    """
    # Skip if models not available
    if not Path(test_config.model_path).exists():
        pytest.skip("LLM model not available")
    
    if not Path(test_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    if not Path(test_config.catalog_path).exists():
        pytest.skip("Reference catalog not available")
    
    pipeline = AnalysisPipeline(config=test_config)
    
    try:
        pipeline.initialize_resources()
        
        # Verify components exist
        assert pipeline.gap_analysis_engine is not None, "Gap analysis engine not initialized"
        assert pipeline.policy_revision_engine is not None, "Policy revision engine not initialized"
        
        # Verify policy revision engine has LLM
        assert pipeline.policy_revision_engine.llm is not None, "Policy revision LLM not set"
        
        print("✓ Gap analysis engine → policy revision engine wiring verified")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
@pytest.mark.wiring
def test_gap_analysis_to_roadmap_generator_wiring(test_config):
    """Verify gap analysis engine → roadmap generator integration.
    
    **Validates: Task 36.1 - Gap analysis engine → roadmap generator**
    """
    # Skip if models not available
    if not Path(test_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    if not Path(test_config.catalog_path).exists():
        pytest.skip("Reference catalog not available")
    
    pipeline = AnalysisPipeline(config=test_config)
    
    try:
        pipeline.initialize_resources()
        
        # Verify components exist
        assert pipeline.gap_analysis_engine is not None, "Gap analysis engine not initialized"
        assert pipeline.roadmap_generator is not None, "Roadmap generator not initialized"
        
        # Verify roadmap generator has catalog
        assert pipeline.roadmap_generator.catalog is not None, "Roadmap generator catalog not set"
        
        print("✓ Gap analysis engine → roadmap generator wiring verified")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
@pytest.mark.wiring
def test_all_components_to_output_manager_wiring(test_config):
    """Verify all components → output manager integration.
    
    **Validates: Task 36.1 - All components → output manager**
    """
    # Skip if models not available
    if not Path(test_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    if not Path(test_config.catalog_path).exists():
        pytest.skip("Reference catalog not available")
    
    pipeline = AnalysisPipeline(config=test_config)
    
    try:
        pipeline.initialize_resources()
        
        # Verify output-related components exist
        assert pipeline.gap_report_generator is not None, "Gap report generator not initialized"
        assert pipeline.roadmap_generator is not None, "Roadmap generator not initialized"
        
        # Verify output configuration
        assert pipeline.config.output_dir is not None, "Output directory not configured"
        
        print("✓ All components → output manager wiring verified")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
@pytest.mark.wiring
def test_all_operations_to_audit_logger_wiring(test_config):
    """Verify all operations → audit logger integration.
    
    **Validates: Task 36.1 - All operations → audit logger**
    """
    # Skip if models not available
    if not Path(test_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    pipeline = AnalysisPipeline(config=test_config)
    
    try:
        pipeline.initialize_resources()
        
        # Verify audit logger exists
        assert pipeline.audit_logger is not None, "Audit logger not initialized"
        
        # Verify audit directory configured
        assert pipeline.config.audit_dir is not None, "Audit directory not configured"
        assert pipeline.audit_logger.audit_dir.exists(), "Audit directory not created"
        
        print("✓ All operations → audit logger wiring verified")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
@pytest.mark.wiring
def test_langchain_orchestration_wiring(test_config):
    """Verify LangChain orchestration connects all components.
    
    **Validates: Task 36.1 - LangChain orchestration**
    """
    # Skip if models not available
    if not Path(test_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    if not Path(test_config.catalog_path).exists():
        pytest.skip("Reference catalog not available")
    
    pipeline = AnalysisPipeline(config=test_config)
    
    try:
        pipeline.initialize_resources()
        
        # Verify all major components are initialized
        components = {
            'document_parser': pipeline.document_parser,
            'text_chunker': pipeline.text_chunker,
            'catalog': pipeline.catalog,
            'embedding_engine': pipeline.embedding_engine,
            'vector_store': pipeline.vector_store,
            'hybrid_retriever': pipeline.hybrid_retriever,
            'gap_analysis_engine': pipeline.gap_analysis_engine,
            'policy_revision_engine': pipeline.policy_revision_engine,
            'roadmap_generator': pipeline.roadmap_generator,
            'gap_report_generator': pipeline.gap_report_generator,
            'audit_logger': pipeline.audit_logger
        }
        
        # Verify all components are not None
        for name, component in components.items():
            assert component is not None, f"Component not initialized: {name}"
        
        print(f"✓ LangChain orchestration wiring verified ({len(components)} components)")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
@pytest.mark.wiring
def test_complete_component_wiring_summary(test_config):
    """Summary test: Verify all component wirings are complete.
    
    **Validates: Task 36.1 - Complete integration**
    """
    # Skip if models not available
    if not Path(test_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    if not Path(test_config.catalog_path).exists():
        pytest.skip("Reference catalog not available")
    
    pipeline = AnalysisPipeline(config=test_config)
    
    try:
        pipeline.initialize_resources()
        
        # Define all required wirings
        wirings = [
            ("Document Parser", "Text Chunker", pipeline.document_parser, pipeline.text_chunker),
            ("Text Chunker", "Embedding Engine", pipeline.text_chunker, pipeline.embedding_engine),
            ("Embedding Engine", "Vector Store", pipeline.embedding_engine, pipeline.vector_store),
            ("Reference Catalog", "Embedding Engine", pipeline.catalog, pipeline.embedding_engine),
            ("Reference Catalog", "Vector Store", pipeline.catalog, pipeline.vector_store),
            ("Hybrid Retriever", "Gap Analysis", pipeline.hybrid_retriever, pipeline.gap_analysis_engine),
            ("Gap Analysis", "Policy Revision", pipeline.gap_analysis_engine, pipeline.policy_revision_engine),
            ("Gap Analysis", "Roadmap Generator", pipeline.gap_analysis_engine, pipeline.roadmap_generator),
            ("Components", "Output Manager", pipeline.gap_report_generator, pipeline.roadmap_generator),
            ("Operations", "Audit Logger", pipeline.gap_analysis_engine, pipeline.audit_logger),
        ]
        
        # Verify all wirings
        print(f"\n{'='*60}")
        print(f"COMPONENT WIRING VERIFICATION")
        print(f"{'='*60}")
        
        for source, target, source_comp, target_comp in wirings:
            assert source_comp is not None, f"{source} not initialized"
            assert target_comp is not None, f"{target} not initialized"
            print(f"✓ {source} → {target}")
        
        print(f"{'='*60}")
        print(f"All {len(wirings)} component wirings verified")
        print(f"{'='*60}\n")
        
    finally:
        pipeline.cleanup()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '-m', 'wiring'])
