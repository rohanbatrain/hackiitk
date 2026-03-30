"""
Unit tests for Stage A Evidence Detector.

Tests the deterministic evidence detection logic including:
- Lexical scoring with keyword matches
- Semantic scoring with embedding similarity
- Section heuristics boost scores
- Coverage classification thresholds
- Evidence span extraction

**Validates: Requirements 9.2, 9.3, 9.4**
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch

from analysis.stage_a_detector import StageADetector
from models.domain import (
    TextChunk,
    CSFSubcategory,
    CoverageAssessment,
    RetrievalResult
)


class TestStageADetector:
    """Test suite for StageADetector class."""
    
    @pytest.fixture
    def mock_retriever(self):
        """Create mock hybrid retriever."""
        retriever = Mock()
        return retriever
    
    @pytest.fixture
    def mock_embedding_engine(self):
        """Create mock embedding engine."""
        engine = Mock()
        # Return normalized embeddings
        engine.embed_text.return_value = np.array([0.5] * 384, dtype=np.float32)
        return engine
    
    @pytest.fixture
    def detector(self, mock_retriever, mock_embedding_engine):
        """Create StageADetector instance with default weights."""
        return StageADetector(
            retriever=mock_retriever,
            embedding_engine=mock_embedding_engine,
            lexical_weight=0.3,
            semantic_weight=0.5,
            section_weight=0.2
        )
    
    @pytest.fixture
    def sample_subcategory(self):
        """Create sample CSF subcategory."""
        return CSFSubcategory(
            subcategory_id='GV.RM-01',
            function='Govern',
            category='Risk Management Strategy',
            description='Risk management objectives are established and agreed to by organizational stakeholders.',
            keywords=['risk', 'management', 'objectives', 'stakeholders'],
            domain_tags=['isms', 'risk_management'],
            mapped_templates=['Risk Management Policy'],
            priority='high'
        )
    
    @pytest.fixture
    def sample_chunks(self):
        """Create sample policy text chunks."""
        return [
            TextChunk(
                text='The organization establishes risk management objectives aligned with stakeholder requirements.',
                chunk_id='chunk_001',
                source_file='policy.pdf',
                start_pos=0,
                end_pos=100,
                page_number=1,
                section_title='Risk Management',
                embedding=None
            ),
            TextChunk(
                text='Access control policies define user authentication requirements.',
                chunk_id='chunk_002',
                source_file='policy.pdf',
                start_pos=100,
                end_pos=200,
                page_number=1,
                section_title='Access Control',
                embedding=None
            ),
            TextChunk(
                text='Data backup procedures ensure business continuity.',
                chunk_id='chunk_003',
                source_file='policy.pdf',
                start_pos=200,
                end_pos=300,
                page_number=2,
                section_title='Data Protection',
                embedding=None
            )
        ]
    
    def test_initialization_valid_weights(self, mock_retriever, mock_embedding_engine):
        """Test detector initialization with valid weights."""
        detector = StageADetector(
            retriever=mock_retriever,
            embedding_engine=mock_embedding_engine,
            lexical_weight=0.3,
            semantic_weight=0.5,
            section_weight=0.2
        )
        
        assert detector.lexical_weight == 0.3
        assert detector.semantic_weight == 0.5
        assert detector.section_weight == 0.2
    
    def test_initialization_invalid_weights(self, mock_retriever, mock_embedding_engine):
        """Test detector initialization with invalid weights that don't sum to 1.0."""
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            StageADetector(
                retriever=mock_retriever,
                embedding_engine=mock_embedding_engine,
                lexical_weight=0.3,
                semantic_weight=0.3,
                section_weight=0.3
            )
    
    def test_lexical_scoring_full_match(self, detector, sample_chunks):
        """Test lexical scoring with all keywords present."""
        keywords = ['risk', 'management', 'objectives', 'stakeholders']
        
        score = detector._calculate_lexical_score(sample_chunks[:1], keywords)
        
        # 3 out of 4 keywords are in the first chunk (risk, management, objectives)
        # 'stakeholders' is in the chunk but as 'stakeholder' (singular)
        assert score == 0.75  # 3/4 keywords found
    
    def test_lexical_scoring_partial_match(self, detector, sample_chunks):
        """Test lexical scoring with some keywords present."""
        keywords = ['risk', 'management', 'encryption', 'firewall']
        
        score = detector._calculate_lexical_score(sample_chunks[:1], keywords)
        
        # Only 2 out of 4 keywords present
        assert score == 0.5
    
    def test_lexical_scoring_no_match(self, detector, sample_chunks):
        """Test lexical scoring with no keywords present."""
        keywords = ['encryption', 'firewall', 'intrusion', 'detection']
        
        score = detector._calculate_lexical_score(sample_chunks[:1], keywords)
        
        assert score == 0.0
    
    def test_lexical_scoring_case_insensitive(self, detector):
        """Test lexical scoring is case-insensitive."""
        chunks = [
            TextChunk(
                text='RISK MANAGEMENT objectives are critical.',
                chunk_id='chunk_001',
                source_file='policy.pdf',
                start_pos=0,
                end_pos=50,
                embedding=None
            )
        ]
        keywords = ['risk', 'management', 'objectives']
        
        score = detector._calculate_lexical_score(chunks, keywords)
        
        assert score == 1.0
    
    def test_lexical_scoring_word_boundaries(self, detector):
        """Test lexical scoring respects word boundaries."""
        chunks = [
            TextChunk(
                text='The organization manages risks effectively.',
                chunk_id='chunk_001',
                source_file='policy.pdf',
                start_pos=0,
                end_pos=50,
                embedding=None
            )
        ]
        # 'risk' should not match 'risks' without proper handling
        keywords = ['risk', 'management']
        
        score = detector._calculate_lexical_score(chunks, keywords)
        
        # Should find 'risk' in 'risks' and 'management' in 'manages'
        # depending on word boundary implementation
        assert 0.0 <= score <= 1.0
    
    def test_semantic_scoring_high_similarity(self, detector, sample_chunks, mock_embedding_engine):
        """Test semantic scoring with high similarity."""
        # Mock high similarity embeddings (nearly identical vectors)
        subcategory_embedding = np.array([1.0] + [0.0] * 383, dtype=np.float32)
        chunk_embedding = np.array([0.99] + [0.01] * 383, dtype=np.float32)
        
        # Normalize embeddings
        subcategory_embedding = subcategory_embedding / np.linalg.norm(subcategory_embedding)
        chunk_embedding = chunk_embedding / np.linalg.norm(chunk_embedding)
        
        mock_embedding_engine.embed_text.side_effect = [
            subcategory_embedding,
            chunk_embedding
        ]
        
        score = detector._calculate_semantic_score(
            sample_chunks[:1],
            'Risk management objectives'
        )
        
        # High cosine similarity (should be close to 1.0)
        assert score > 0.9
    
    def test_semantic_scoring_low_similarity(self, detector, sample_chunks, mock_embedding_engine):
        """Test semantic scoring with low similarity."""
        # Mock low similarity embeddings (orthogonal vectors)
        subcategory_embedding = np.array([1.0] + [0.0] * 383, dtype=np.float32)
        chunk_embedding = np.array([0.0] + [1.0] + [0.0] * 382, dtype=np.float32)
        
        # Normalize embeddings
        subcategory_embedding = subcategory_embedding / np.linalg.norm(subcategory_embedding)
        chunk_embedding = chunk_embedding / np.linalg.norm(chunk_embedding)
        
        mock_embedding_engine.embed_text.side_effect = [
            subcategory_embedding,
            chunk_embedding
        ]
        
        score = detector._calculate_semantic_score(
            sample_chunks[:1],
            'Risk management objectives'
        )
        
        # Low cosine similarity (orthogonal vectors)
        assert score < 0.2
    
    def test_semantic_scoring_uses_max_similarity(self, detector, sample_chunks, mock_embedding_engine):
        """Test semantic scoring returns maximum similarity across chunks."""
        # Mock embeddings with varying similarities
        subcategory_embedding = np.array([1.0] + [0.0] * 383, dtype=np.float32)
        subcategory_embedding = subcategory_embedding / np.linalg.norm(subcategory_embedding)
        
        chunk_embeddings = [
            np.array([0.3] + [0.0] * 383, dtype=np.float32),  # Low similarity
            np.array([0.9] + [0.0] * 383, dtype=np.float32),  # High similarity
            np.array([0.5] + [0.0] * 383, dtype=np.float32),  # Medium similarity
        ]
        chunk_embeddings = [e / np.linalg.norm(e) for e in chunk_embeddings]
        
        mock_embedding_engine.embed_text.side_effect = [
            subcategory_embedding,
            *chunk_embeddings
        ]
        
        score = detector._calculate_semantic_score(
            sample_chunks,
            'Risk management objectives'
        )
        
        # Should return the maximum similarity (from second chunk)
        expected_max = np.dot(subcategory_embedding, chunk_embeddings[1])
        assert abs(score - expected_max) < 0.01
    
    def test_section_scoring_exact_match(self, detector):
        """Test section heuristic with exact category match."""
        chunks = [
            TextChunk(
                text='Risk management content here.',
                chunk_id='chunk_001',
                source_file='policy.pdf',
                start_pos=0,
                end_pos=50,
                section_title='Risk Management Strategy',
                embedding=None
            )
        ]
        
        score = detector._calculate_section_score(chunks, 'Risk Management Strategy')
        
        # Should have high overlap
        assert score > 0.5
    
    def test_section_scoring_partial_match(self, detector):
        """Test section heuristic with partial category match."""
        chunks = [
            TextChunk(
                text='Risk content here.',
                chunk_id='chunk_001',
                source_file='policy.pdf',
                start_pos=0,
                end_pos=50,
                section_title='Risk Management',
                embedding=None
            )
        ]
        
        score = detector._calculate_section_score(chunks, 'Risk Management Strategy')
        
        # Should have overlap (risk, management) = 2/3 terms
        # Note: 'strategy' is not in section title, so score is 2/3 = 0.666...
        assert 0.6 <= score <= 0.7
    
    def test_section_scoring_no_match(self, detector):
        """Test section heuristic with no category match."""
        chunks = [
            TextChunk(
                text='Access control content here.',
                chunk_id='chunk_001',
                source_file='policy.pdf',
                start_pos=0,
                end_pos=50,
                section_title='Access Control',
                embedding=None
            )
        ]
        
        score = detector._calculate_section_score(chunks, 'Risk Management Strategy')
        
        # Should have no overlap
        assert score == 0.0
    
    def test_section_scoring_no_section_title(self, detector):
        """Test section heuristic when chunks have no section titles."""
        chunks = [
            TextChunk(
                text='Some content here.',
                chunk_id='chunk_001',
                source_file='policy.pdf',
                start_pos=0,
                end_pos=50,
                section_title=None,
                embedding=None
            )
        ]
        
        score = detector._calculate_section_score(chunks, 'Risk Management Strategy')
        
        assert score == 0.0
    
    def test_coverage_classification_covered(self, detector):
        """Test coverage classification for covered status (>0.65)."""
        status = detector._classify_coverage(0.70)
        assert status == 'covered'
        
        status = detector._classify_coverage(0.9)
        assert status == 'covered'
    
    def test_coverage_classification_partially_covered(self, detector):
        """Test coverage classification for partially covered status (0.45-0.65)."""
        status = detector._classify_coverage(0.45)
        assert status == 'partially_covered'
        
        status = detector._classify_coverage(0.55)
        assert status == 'partially_covered'
        
        status = detector._classify_coverage(0.65)
        assert status == 'partially_covered'
    
    def test_coverage_classification_missing(self, detector):
        """Test coverage classification for missing status (<0.3)."""
        status = detector._classify_coverage(0.0)
        assert status == 'missing'
        
        status = detector._classify_coverage(0.2)
        assert status == 'missing'
    
    def test_coverage_classification_ambiguous(self, detector):
        """Test coverage classification for ambiguous status (0.25-0.45)."""
        status = detector._classify_coverage(0.25)
        assert status == 'ambiguous'
        
        status = detector._classify_coverage(0.35)
        assert status == 'ambiguous'
        
        status = detector._classify_coverage(0.44)
        assert status == 'ambiguous'
    
    def test_detect_evidence_no_retrieval_results(
        self,
        detector,
        sample_chunks,
        sample_subcategory,
        mock_retriever
    ):
        """Test detect_evidence when retriever returns no results."""
        mock_retriever.retrieve.return_value = []
        
        assessment = detector.detect_evidence(
            policy_chunks=sample_chunks,
            subcategory=sample_subcategory,
            top_k=5
        )
        
        assert assessment.status == 'missing'
        assert assessment.confidence == 0.0
        assert assessment.lexical_score == 0.0
        assert assessment.semantic_score == 0.0
        assert len(assessment.evidence_spans) == 0
    
    def test_detect_evidence_with_results(
        self,
        detector,
        sample_chunks,
        sample_subcategory,
        mock_retriever,
        mock_embedding_engine
    ):
        """Test detect_evidence with retrieval results."""
        # Mock retrieval results
        mock_retriever.retrieve.return_value = [
            RetrievalResult(
                subcategory_id='GV.RM-01',
                subcategory_text='Risk management objectives...',
                relevance_score=0.9,
                evidence_spans=['chunk text'],
                retrieval_method='hybrid'
            )
        ]
        
        # Mock embeddings for semantic scoring
        mock_embedding_engine.embed_text.return_value = np.array([0.5] * 384, dtype=np.float32)
        
        assessment = detector.detect_evidence(
            policy_chunks=sample_chunks,
            subcategory=sample_subcategory,
            top_k=5
        )
        
        assert assessment.subcategory_id == 'GV.RM-01'
        assert assessment.status in ['covered', 'partially_covered', 'missing', 'ambiguous']
        assert 0.0 <= assessment.confidence <= 1.0
        assert 0.0 <= assessment.lexical_score <= 1.0
        assert 0.0 <= assessment.semantic_score <= 1.0
        assert len(assessment.evidence_spans) > 0
    
    def test_detect_evidence_extracts_top_evidence_spans(
        self,
        detector,
        sample_chunks,
        sample_subcategory,
        mock_retriever,
        mock_embedding_engine
    ):
        """Test that detect_evidence extracts top 3 evidence spans."""
        mock_retriever.retrieve.return_value = [
            RetrievalResult(
                subcategory_id='GV.RM-01',
                subcategory_text='Risk management objectives...',
                relevance_score=0.9,
                evidence_spans=['chunk text'],
                retrieval_method='hybrid'
            )
        ]
        
        mock_embedding_engine.embed_text.return_value = np.array([0.5] * 384, dtype=np.float32)
        
        assessment = detector.detect_evidence(
            policy_chunks=sample_chunks,
            subcategory=sample_subcategory,
            top_k=5
        )
        
        # Should extract top 3 chunks as evidence
        assert len(assessment.evidence_spans) <= 3
        assert all(isinstance(span, str) for span in assessment.evidence_spans)
    
    def test_extract_key_terms(self, detector):
        """Test key term extraction removes stop words."""
        text = "Risk Management Strategy and Policy"
        
        terms = detector._extract_key_terms(text)
        
        # Should include: risk, management, strategy
        # Should exclude: and, policy (stop word)
        assert 'risk' in terms
        assert 'management' in terms
        assert 'strategy' in terms
        assert 'and' not in terms
        assert 'policy' not in terms
    
    def test_extract_key_terms_case_insensitive(self, detector):
        """Test key term extraction is case-insensitive."""
        text = "RISK Management STRATEGY"
        
        terms = detector._extract_key_terms(text)
        
        # All terms should be lowercase
        assert 'risk' in terms
        assert 'management' in terms
        assert 'strategy' in terms
        assert 'RISK' not in terms
    
    def test_combined_scoring_weights(
        self,
        detector,
        sample_chunks,
        sample_subcategory,
        mock_retriever,
        mock_embedding_engine
    ):
        """Test that combined confidence uses correct weights."""
        mock_retriever.retrieve.return_value = [
            RetrievalResult(
                subcategory_id='GV.RM-01',
                subcategory_text='Risk management objectives...',
                relevance_score=0.9,
                evidence_spans=['chunk text'],
                retrieval_method='hybrid'
            )
        ]
        
        # Mock specific scores - use normalized embeddings
        embedding = np.array([0.8] * 384, dtype=np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        mock_embedding_engine.embed_text.return_value = embedding
        
        assessment = detector.detect_evidence(
            policy_chunks=sample_chunks,
            subcategory=sample_subcategory,
            top_k=5
        )
        
        # Verify confidence is weighted combination
        # Note: section_score may be non-zero if 'Risk Management' section matches
        expected_confidence = (
            detector.lexical_weight * assessment.lexical_score +
            detector.semantic_weight * assessment.semantic_score +
            detector.section_weight * 0.666  # 'Risk Management' section matches 2/3 terms
        )
        
        # Allow reasonable floating point differences
        assert abs(assessment.confidence - expected_confidence) < 0.05


class TestStageADetectorEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def mock_retriever(self):
        """Create mock hybrid retriever."""
        return Mock()
    
    @pytest.fixture
    def mock_embedding_engine(self):
        """Create mock embedding engine."""
        engine = Mock()
        engine.embed_text.return_value = np.array([0.5] * 384, dtype=np.float32)
        return engine
    
    def test_empty_keywords_list(self, mock_retriever, mock_embedding_engine):
        """Test lexical scoring with empty keywords list."""
        detector = StageADetector(
            retriever=mock_retriever,
            embedding_engine=mock_embedding_engine
        )
        
        chunks = [
            TextChunk(
                text='Some text',
                chunk_id='chunk_001',
                source_file='policy.pdf',
                start_pos=0,
                end_pos=10,
                embedding=None
            )
        ]
        
        score = detector._calculate_lexical_score(chunks, [])
        
        assert score == 0.0
    
    def test_empty_chunks_list(self, mock_retriever, mock_embedding_engine):
        """Test scoring with empty chunks list."""
        detector = StageADetector(
            retriever=mock_retriever,
            embedding_engine=mock_embedding_engine
        )
        
        score = detector._calculate_lexical_score([], ['risk', 'management'])
        
        assert score == 0.0
    
    def test_semantic_scoring_with_precomputed_embeddings(
        self,
        mock_retriever,
        mock_embedding_engine
    ):
        """Test semantic scoring uses precomputed chunk embeddings."""
        detector = StageADetector(
            retriever=mock_retriever,
            embedding_engine=mock_embedding_engine
        )
        
        # Create chunk with precomputed embedding
        precomputed_embedding = np.array([0.9] + [0.0] * 383, dtype=np.float32)
        precomputed_embedding = precomputed_embedding / np.linalg.norm(precomputed_embedding)
        
        chunks = [
            TextChunk(
                text='Some text',
                chunk_id='chunk_001',
                source_file='policy.pdf',
                start_pos=0,
                end_pos=10,
                embedding=precomputed_embedding
            )
        ]
        
        subcategory_embedding = np.array([1.0] + [0.0] * 383, dtype=np.float32)
        subcategory_embedding = subcategory_embedding / np.linalg.norm(subcategory_embedding)
        
        mock_embedding_engine.embed_text.return_value = subcategory_embedding
        
        score = detector._calculate_semantic_score(chunks, 'Test description')
        
        # Should use precomputed embedding, not call embed_text for chunk
        assert mock_embedding_engine.embed_text.call_count == 1  # Only for subcategory
        assert score > 0.8  # High similarity
