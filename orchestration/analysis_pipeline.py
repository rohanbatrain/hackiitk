"""
Analysis Pipeline - LangChain orchestration for complete workflow.

This module implements the AnalysisPipeline class that orchestrates all components
of the Offline Policy Gap Analyzer using LangChain abstractions. The pipeline
manages the complete workflow from document parsing through final output generation.

**Validates: Requirements 7.9, 8.8**
"""

import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from models.domain import (
    ParsedDocument,
    TextChunk,
    GapAnalysisReport,
    RevisedPolicy,
    ImplementationRoadmap
)

# Component imports
from ingestion.document_parser import DocumentParser
from ingestion.text_chunker import TextChunker
from reference_builder.reference_catalog import ReferenceCatalog
from retrieval.embedding_engine import EmbeddingEngine
from retrieval.vector_store import VectorStore
from retrieval.sparse_retriever import SparseRetriever
from retrieval.reranker import Reranker
from retrieval.hybrid_retriever import HybridRetriever
from analysis.llm_runtime import LLMRuntime
from analysis.stage_a_detector import StageADetector
from analysis.stage_b_reasoner import StageBReasoner
from analysis.gap_analysis_engine import GapAnalysisEngine
from revision.policy_revision_engine import PolicyRevisionEngine
from reporting.roadmap_generator import RoadmapGenerator
from reporting.gap_report_generator import GapReportGenerator
from reporting.audit_logger import AuditLogger
from utils.config_loader import ConfigLoader
from utils.logger import setup_logging
from utils.error_handler import (
    RetryableError,
    retry_with_backoff,
    ErrorHandler,
    GracefulDegradation
)
from utils.progress import StepProgress, ProgressIndicator


logger = logging.getLogger(__name__)


class PipelineConfig:
    """Configuration for analysis pipeline.
    
    Attributes:
        chunk_size: Maximum tokens per chunk
        overlap: Token overlap between chunks
        top_k: Number of retrieval results
        temperature: LLM temperature
        max_tokens: Maximum LLM generation tokens
        model_name: LLM model name
        model_path: Path to LLM model file
        embedding_model_path: Path to embedding model
        vector_store_path: Path to vector store persistence
        catalog_path: Path to reference catalog JSON
        cis_guide_path: Path to CIS guide PDF
        output_dir: Base output directory
        audit_dir: Audit log directory
    """
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """Initialize pipeline configuration.
        
        Args:
            config_dict: Optional configuration dictionary
        """
        config = config_dict or {}
        
        # Chunking parameters
        self.chunk_size = config.get('chunk_size', 512)
        self.overlap = config.get('overlap', 50)
        
        # Retrieval parameters
        self.top_k = config.get('top_k', 5)
        
        # LLM parameters
        self.temperature = config.get('temperature', 0.1)
        self.max_tokens = config.get('max_tokens', 512)
        self.model_name = config.get('model_name', 'qwen2.5:3b-instruct')
        self.model_path = config.get('model_path', 'qwen2.5:3b-instruct')
        
        # Model paths
        self.embedding_model_path = config.get('embedding_model_path', 'models/embeddings/all-MiniLM-L6-v2')
        self.reranker_model_path = config.get('reranker_model_path', 'cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        # Storage paths
        self.vector_store_path = config.get('vector_store_path', 'vector_store/chroma_db')
        self.catalog_path = config.get('catalog_path', 'data/reference_catalog.json')
        self.cis_guide_path = config.get('cis_guide_path', 'data/cis_guide.pdf')
        
        # Output paths
        self.output_dir = config.get('output_dir', 'outputs')
        self.audit_dir = config.get('audit_dir', 'audit_logs')
        
        # Domain and severity
        self.severity_thresholds = config.get('severity_thresholds', {})
        self.csf_function_priority = config.get('csf_function_priority', [])


class AnalysisResult:
    """Result of complete analysis pipeline.
    
    Attributes:
        gap_report: Gap analysis report
        revised_policy: Revised policy document
        roadmap: Implementation roadmap
        output_directory: Directory containing all outputs
        duration_seconds: Total analysis duration
    """
    
    def __init__(
        self,
        gap_report: GapAnalysisReport,
        revised_policy: RevisedPolicy,
        roadmap: ImplementationRoadmap,
        output_directory: str,
        duration_seconds: float
    ):
        self.gap_report = gap_report
        self.revised_policy = revised_policy
        self.roadmap = roadmap
        self.output_directory = output_directory
        self.duration_seconds = duration_seconds


class AnalysisPipeline:
    """Orchestrates complete policy gap analysis workflow.
    
    The pipeline coordinates all components using LangChain abstractions:
    1. Parse document
    2. Load/build reference catalog
    3. Chunk and embed policy text
    4. Retrieve relevant CSF subcategories
    5. Execute Stage A analysis (deterministic)
    6. Execute Stage B analysis (LLM reasoning)
    7. Generate gap report
    8. Generate revised policy
    9. Generate implementation roadmap
    10. Write outputs and audit log
    
    Attributes:
        config: Pipeline configuration
        document_parser: Document parser component
        text_chunker: Text chunker component
        catalog: Reference catalog
        embedding_engine: Embedding engine
        vector_store: Vector store
        hybrid_retriever: Hybrid retriever
        llm_runtime: LLM runtime
        gap_analysis_engine: Gap analysis engine
        policy_revision_engine: Policy revision engine
        roadmap_generator: Roadmap generator
        gap_report_generator: Gap report generator
        audit_logger: Audit logger
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize analysis pipeline.
        
        Args:
            config: Optional pipeline configuration
        """
        self.config = config or PipelineConfig()
        
        # Components (initialized in initialize_resources)
        self.document_parser = None
        self.text_chunker = None
        self.catalog = None
        self.embedding_engine = None
        self.vector_store = None
        self.hybrid_retriever = None
        self.llm_runtime = None
        self.gap_analysis_engine = None
        self.policy_revision_engine = None
        self.roadmap_generator = None
        self.gap_report_generator = None
        self.audit_logger = None
        
        # State
        self._initialized = False
        
        logger.info("AnalysisPipeline created")
    
    def execute(
        self,
        policy_path: str,
        domain: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> AnalysisResult:
        """Execute complete analysis pipeline.
        
        Workflow:
        1. Initialize resources (models, vector store, catalog)
        2. Parse policy document
        3. Chunk and embed policy text
        4. Retrieve relevant CSF subcategories
        5. Execute two-stage gap analysis
        6. Generate revised policy
        7. Generate implementation roadmap
        8. Write all outputs
        9. Create audit log
        10. Cleanup resources
        
        Args:
            policy_path: Path to policy document to analyze
            domain: Optional policy domain for prioritization
            output_dir: Optional output directory (overrides config)
            
        Returns:
            AnalysisResult with gap report, revised policy, roadmap, and metadata
            
        Raises:
            FileNotFoundError: If policy file doesn't exist
            ValueError: If policy content is insufficient for analysis
            RuntimeError: If analysis fails
        """
        start_time = time.time()
        
        logger.info(f"Starting analysis pipeline for: {policy_path}")
        logger.info(f"Domain: {domain or 'auto-detect'}")
        
        # Create step progress tracker
        step_progress = StepProgress(total_steps=9, operation_name="Policy Analysis")
        
        try:
            # Step 1: Initialize resources
            if not self._initialized:
                step_progress.start_step("Initializing pipeline resources")
                self.initialize_resources()
            
            # Step 2: Parse document
            step_progress.start_step("Parsing policy document")
            parsed_policy = self._parse_document(policy_path)
            logger.info(f"Parsed {parsed_policy.page_count} pages, {len(parsed_policy.text)} characters")
            
            # INPUT VALIDATION: Check for minimum content
            if len(parsed_policy.text.strip()) < 50:
                error_msg = (
                    f"Policy content is too short for analysis ({len(parsed_policy.text)} characters). "
                    f"Minimum required: 50 characters. Please provide a policy document with sufficient content."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Step 3: Chunk policy text
            step_progress.start_step("Chunking policy text")
            policy_chunks = self._chunk_policy(parsed_policy)
            logger.info(f"Created {len(policy_chunks)} chunks")
            
            # INPUT VALIDATION: Check for minimum chunks
            if len(policy_chunks) == 0:
                error_msg = (
                    f"Policy document produced 0 text chunks. "
                    f"This typically indicates the document is empty or contains only whitespace. "
                    f"Please provide a policy document with actual content."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Step 4: Embed policy chunks
            step_progress.start_step("Embedding policy chunks")
            self._embed_policy_chunks(policy_chunks)
            logger.info("Policy chunks embedded")
            
            # Step 5: Retrieve relevant CSF subcategories (handled by gap analysis engine)
            step_progress.start_step("Retrieving relevant CSF subcategories")
            # Retrieval is integrated into gap analysis
            
            # Step 6: Execute gap analysis
            step_progress.start_step("Executing two-stage gap analysis")
            gap_report = self._execute_gap_analysis(
                policy_chunks=policy_chunks,
                input_file=policy_path,
                domain=domain
            )
            logger.info(f"Gap analysis complete: {len(gap_report.gaps)} gaps identified")
            
            # Step 7: Generate revised policy
            step_progress.start_step("Generating revised policy")
            revised_policy = self._generate_revised_policy(
                parsed_policy=parsed_policy,
                gaps=gap_report.gaps
            )
            logger.info(f"Revised policy generated: {len(revised_policy.revisions)} revisions")
            
            # Step 8: Generate implementation roadmap
            step_progress.start_step("Generating implementation roadmap")
            roadmap = self._generate_roadmap(gaps=gap_report.gaps)
            logger.info(
                f"Roadmap generated: {len(roadmap.immediate_actions)} immediate, "
                f"{len(roadmap.near_term_actions)} near-term, "
                f"{len(roadmap.medium_term_actions)} medium-term actions"
            )
            
            # Step 9: Write outputs
            step_progress.start_step("Writing outputs")
            output_directory = self._write_outputs(
                gap_report=gap_report,
                revised_policy=revised_policy,
                roadmap=roadmap,
                policy_path=policy_path,
                output_dir=output_dir
            )
            logger.info(f"Outputs written to: {output_directory}")
            
            # Step 10: Create audit log
            step_progress.start_step("Creating audit log")
            duration = time.time() - start_time
            self._create_audit_log(
                input_file=policy_path,
                output_directory=output_directory,
                duration=duration
            )
            logger.info("Audit log created")
            
            # Mark complete
            step_progress.finish()
            
            # Build result
            result = AnalysisResult(
                gap_report=gap_report,
                revised_policy=revised_policy,
                roadmap=roadmap,
                output_directory=output_directory,
                duration_seconds=duration
            )
            
            logger.info(
                f"Analysis pipeline complete in {duration:.2f} seconds"
            )
            
            return result
            
        except ValueError as e:
            # Input validation errors - user-friendly message already provided
            logger.error(f"Input validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Analysis pipeline failed: {e}", exc_info=True)
            raise RuntimeError(f"Analysis pipeline failed: {e}") from e
        
        finally:
            # Cleanup is optional - resources can be reused for multiple analyses
            pass
    
    def initialize_resources(self) -> None:
        """Initialize all pipeline resources.
        
        Loads models, vector store, and reference catalog. This method
        should be called once before executing analyses.
        
        Raises:
            FileNotFoundError: If required resources are missing
            RuntimeError: If initialization fails
        """
        logger.info("Initializing pipeline resources...")
        
        try:
            # Initialize document parser
            logger.info("Initializing document parser...")
            self.document_parser = DocumentParser()
            
            # Initialize text chunker
            logger.info("Initializing text chunker...")
            self.text_chunker = TextChunker(
                chunk_size=self.config.chunk_size,
                overlap=self.config.overlap
            )
            
            # Load or build reference catalog
            logger.info("Loading reference catalog...")
            self.catalog = self._load_or_build_catalog()
            logger.info(f"Reference catalog loaded: {len(self.catalog.get_all_subcategories())} subcategories")
            
            # Initialize embedding engine
            logger.info("Initializing embedding engine...")
            self.embedding_engine = EmbeddingEngine(
                model_path=self.config.embedding_model_path
            )
            
            # Initialize vector store
            logger.info("Initializing vector store...")
            self.vector_store = VectorStore(
                persist_directory=self.config.vector_store_path
            )
            
            # Embed and store reference catalog if needed
            self._ensure_catalog_embedded()
            
            # Initialize reranker
            logger.info("Initializing reranker...")
            reranker = Reranker(model_path=self.config.reranker_model_path)
            
            # Initialize hybrid retriever
            logger.info("Initializing hybrid retriever...")
            self.hybrid_retriever = HybridRetriever(
                vector_store=self.vector_store,
                embedding_engine=self.embedding_engine,
                catalog=self.catalog,
                reranker=reranker
            )
            
            # Initialize LLM runtime
            logger.info("Initializing LLM runtime...")
            self.llm_runtime = LLMRuntime(
                model_path=self.config.model_path,
                backend="ollama"
            )
            
            # Initialize Stage A detector
            logger.info("Initializing Stage A detector...")
            stage_a = StageADetector(
                retriever=self.hybrid_retriever,
                embedding_engine=self.embedding_engine
            )
            
            # Initialize Stage B reasoner
            logger.info("Initializing Stage B reasoner...")
            stage_b = StageBReasoner(llm=self.llm_runtime)
            
            # Initialize gap analysis engine
            logger.info("Initializing gap analysis engine...")
            self.gap_analysis_engine = GapAnalysisEngine(
                stage_a=stage_a,
                stage_b=stage_b,
                catalog=self.catalog,
                model_name=self.config.model_name,
                model_version="q4_k_m",
                embedding_model="all-MiniLM-L6-v2",
                prompt_version="1.0.0"
            )
            
            # Initialize policy revision engine
            logger.info("Initializing policy revision engine...")
            self.policy_revision_engine = PolicyRevisionEngine(
                llm=self.llm_runtime,
                catalog=self.catalog,
                temperature=self.config.temperature
            )
            
            # Initialize roadmap generator
            logger.info("Initializing roadmap generator...")
            self.roadmap_generator = RoadmapGenerator(catalog=self.catalog)
            
            # Initialize gap report generator
            logger.info("Initializing gap report generator...")
            self.gap_report_generator = GapReportGenerator()
            
            # Initialize audit logger
            logger.info("Initializing audit logger...")
            self.audit_logger = AuditLogger(audit_dir=self.config.audit_dir)
            
            self._initialized = True
            logger.info("Pipeline resources initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize resources: {e}", exc_info=True)
            raise RuntimeError(f"Resource initialization failed: {e}") from e
    
    def cleanup(self) -> None:
        """Release resources and finalize audit log.
        
        This method should be called when the pipeline is no longer needed.
        It releases model resources and ensures all logs are flushed.
        """
        logger.info("Cleaning up pipeline resources...")
        
        # Cleanup LLM runtime
        if self.llm_runtime:
            try:
                # LLM runtime cleanup if needed
                pass
            except Exception as e:
                logger.warning(f"LLM cleanup failed: {e}")
        
        # Cleanup vector store
        if self.vector_store:
            try:
                # Vector store cleanup if needed
                pass
            except Exception as e:
                logger.warning(f"Vector store cleanup failed: {e}")
        
        self._initialized = False
        logger.info("Pipeline cleanup complete")
    
    def _parse_document(self, policy_path: str) -> ParsedDocument:
        """Parse policy document.
        
        Args:
            policy_path: Path to policy document
            
        Returns:
            ParsedDocument with text and structure
        """
        return self.document_parser.parse(policy_path)
    
    def _chunk_policy(self, parsed_policy: ParsedDocument) -> list[TextChunk]:
        """Chunk policy text.
        
        Args:
            parsed_policy: Parsed policy document
            
        Returns:
            List of text chunks
        """
        return self.text_chunker.chunk(
            text=parsed_policy.text,
            structure=parsed_policy.structure
        )
    
    def _embed_policy_chunks(self, policy_chunks: list[TextChunk]) -> None:
        """Embed policy chunks and store in vector store.
        
        Args:
            policy_chunks: List of text chunks to embed
        """
        # Extract texts
        texts = [chunk.text for chunk in policy_chunks]
        
        # Create progress indicator
        progress = ProgressIndicator(
            total=len(texts),
            operation_name="Embedding chunks",
            show_bar=True
        )
        
        # Generate embeddings in batches with progress tracking
        batch_size = 64
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.embedding_engine.embed_batch(batch_texts, batch_size=batch_size)
            all_embeddings.append(batch_embeddings)
            
            # Update progress
            progress.update(current=min(i + batch_size, len(texts)))
        
        progress.finish()
        
        # Concatenate all embeddings
        import numpy as np
        embeddings = np.vstack(all_embeddings) if len(all_embeddings) > 1 else all_embeddings[0]
        
        # Prepare metadata
        metadata = [
            {
                'chunk_id': chunk.chunk_id,
                'source_file': chunk.source_file,
                'start_pos': chunk.start_pos,
                'end_pos': chunk.end_pos,
                'text': chunk.text
            }
            for chunk in policy_chunks
        ]
        
        # Store in vector store
        self.vector_store.add_embeddings(
            embeddings=embeddings,
            metadata=metadata,
            collection_name='policy'
        )
    
    def _execute_gap_analysis(
        self,
        policy_chunks: list[TextChunk],
        input_file: str,
        domain: Optional[str]
    ) -> GapAnalysisReport:
        """Execute gap analysis.
        
        Args:
            policy_chunks: Policy text chunks
            input_file: Input file path
            domain: Optional policy domain
            
        Returns:
            GapAnalysisReport
        """
        return self.gap_analysis_engine.analyze(
            policy_chunks=policy_chunks,
            input_file=input_file,
            domain=domain,
            config_hash=self._calculate_config_hash(),
            retrieval_params={
                'chunk_size': self.config.chunk_size,
                'overlap': self.config.overlap,
                'top_k': self.config.top_k
            }
        )
    
    def _generate_revised_policy(
        self,
        parsed_policy: ParsedDocument,
        gaps: list
    ) -> RevisedPolicy:
        """Generate revised policy.
        
        Args:
            parsed_policy: Original parsed policy
            gaps: List of identified gaps
            
        Returns:
            RevisedPolicy
        """
        return self.policy_revision_engine.revise(
            original_policy=parsed_policy,
            gaps=gaps
        )
    
    def _generate_roadmap(self, gaps: list) -> ImplementationRoadmap:
        """Generate implementation roadmap.
        
        Args:
            gaps: List of identified gaps
            
        Returns:
            ImplementationRoadmap
        """
        return self.roadmap_generator.generate(gaps=gaps)
    
    def _write_outputs(
        self,
        gap_report: GapAnalysisReport,
        revised_policy: RevisedPolicy,
        roadmap: ImplementationRoadmap,
        policy_path: str,
        output_dir: Optional[str]
    ) -> str:
        """Write all outputs to files.
        
        Args:
            gap_report: Gap analysis report
            revised_policy: Revised policy
            roadmap: Implementation roadmap
            policy_path: Original policy path
            output_dir: Optional output directory
            
        Returns:
            Output directory path
        """
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        policy_name = Path(policy_path).stem
        output_directory = Path(output_dir or self.config.output_dir) / f"{policy_name}_{timestamp}"
        output_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Writing outputs to: {output_directory}")
        
        # Write gap report (markdown and JSON)
        gap_report_md = output_directory / "gap_analysis_report.md"
        gap_report_json = output_directory / "gap_analysis_report.json"
        self.gap_report_generator.generate_markdown(gap_report, str(gap_report_md))
        self.gap_report_generator.generate_json(gap_report, str(gap_report_json))
        
        # Write revised policy (markdown)
        revised_policy_md = output_directory / "revised_policy.md"
        revised_policy_md.write_text(revised_policy.revised_text, encoding='utf-8')
        
        # Write roadmap (markdown and JSON)
        roadmap_md = output_directory / "implementation_roadmap.md"
        roadmap_json = output_directory / "implementation_roadmap.json"
        self.roadmap_generator.generate_markdown(roadmap, str(roadmap_md), policy_path)
        self.roadmap_generator.generate_json(roadmap, str(roadmap_json), policy_path)
        
        return str(output_directory)
    
    def _create_audit_log(
        self,
        input_file: str,
        output_directory: str,
        duration: float
    ) -> None:
        """Create audit log entry.
        
        Args:
            input_file: Input file path
            output_directory: Output directory path
            duration: Analysis duration in seconds
        """
        self.audit_logger.log_analysis(
            input_file_path=input_file,
            model_name=self.config.model_name,
            model_version="q4_k_m",
            embedding_model_version="all-MiniLM-L6-v2",
            configuration_parameters={
                'chunk_size': self.config.chunk_size,
                'overlap': self.config.overlap,
                'temperature': self.config.temperature,
                'max_tokens': self.config.max_tokens
            },
            retrieval_parameters={
                'top_k': self.config.top_k
            },
            prompt_template_version="1.0.0",
            output_directory=output_directory,
            analysis_duration_seconds=duration
        )
    
    def _load_or_build_catalog(self) -> ReferenceCatalog:
        """Load existing catalog or build from CIS guide.
        
        Returns:
            ReferenceCatalog
        """
        catalog_path = Path(self.config.catalog_path)
        
        if catalog_path.exists():
            logger.info(f"Loading existing catalog from: {catalog_path}")
            catalog = ReferenceCatalog()
            catalog.load(str(catalog_path))
            return catalog
        else:
            logger.info("Building new catalog from CIS guide...")
            catalog = ReferenceCatalog()
            catalog.build_from_cis_guide(self.config.cis_guide_path)
            
            # Persist for future use
            catalog_path.parent.mkdir(parents=True, exist_ok=True)
            catalog.persist(str(catalog_path))
            logger.info(f"Catalog built and saved to: {catalog_path}")
            
            return catalog
    
    def _ensure_catalog_embedded(self) -> None:
        """Ensure reference catalog is embedded in vector store."""
        # Check if catalog collection exists
        try:
            # Try to load existing collection
            if self.vector_store.load_collection('catalog'):
                logger.info("Reference catalog already embedded")
                return
        except Exception:
            pass
        
        # Embed catalog
        logger.info("Embedding reference catalog...")
        
        # Extract subcategory texts
        texts = [
            f"{sub.subcategory_id}: {sub.description}"
            for sub in self.catalog.get_all_subcategories()
        ]
        
        # Create progress indicator
        progress = ProgressIndicator(
            total=len(texts),
            operation_name="Embedding catalog",
            show_bar=True
        )
        
        # Generate embeddings
        embeddings = self.embedding_engine.embed_batch(texts, batch_size=64)
        progress.update(current=len(texts))
        progress.finish()
        
        # Prepare metadata
        metadata = [
            {
                'subcategory_id': sub.subcategory_id,
                'function': sub.function,
                'category': sub.category,
                'description': sub.description,
                'text': f"{sub.subcategory_id}: {sub.description}"
            }
            for sub in self.catalog.get_all_subcategories()
        ]
        
        # Store in vector store
        self.vector_store.add_embeddings(
            embeddings=embeddings,
            metadata=metadata,
            collection_name='catalog'
        )
        
        logger.info("Reference catalog embedded successfully")
    
    def _calculate_config_hash(self) -> str:
        """Calculate hash of configuration for audit trail.
        
        Returns:
            Configuration hash string
        """
        import hashlib
        import json
        
        config_dict = {
            'chunk_size': self.config.chunk_size,
            'overlap': self.config.overlap,
            'top_k': self.config.top_k,
            'temperature': self.config.temperature,
            'max_tokens': self.config.max_tokens,
            'model_name': self.config.model_name
        }
        
        config_str = json.dumps(config_dict, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
    
    def __repr__(self) -> str:
        """String representation of pipeline."""
        return f"AnalysisPipeline(initialized={self._initialized})"
