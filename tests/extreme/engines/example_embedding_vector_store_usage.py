"""
Example Usage of Embedding and Vector Store Stress Tester

This script demonstrates how to use the EmbeddingVectorStoreStressTester
in the extreme testing framework.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.extreme.engines.embedding_vector_store_stress_tester import (
    EmbeddingVectorStoreStressTester,
    EmbeddingVectorStoreConfig
)
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.data_generator import TestDataGenerator
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Run embedding and vector store stress tests."""
    logger.info("=" * 80)
    logger.info("Embedding and Vector Store Stress Testing")
    logger.info("=" * 80)
    
    # Initialize components
    config = EmbeddingVectorStoreConfig(
        sequential_searches=1000,  # Reduced for demo
        concurrent_searches=50,
        max_top_k=1000,
        embedding_test_sizes=[100, 1000, 5000],
        large_chunk_count=1000
    )
    
    metrics_collector = MetricsCollector()
    data_generator = TestDataGenerator()
    output_dir = "test_outputs/embedding_vector_store_demo"
    
    # Create tester
    tester = EmbeddingVectorStoreStressTester(
        config=config,
        metrics_collector=metrics_collector,
        data_generator=data_generator,
        output_dir=output_dir
    )
    
    # Run all tests
    logger.info("\nRunning all embedding and vector store stress tests...")
    results = tester.run_tests()
    
    # Analyze results
    logger.info("\n" + "=" * 80)
    logger.info("Test Results Summary")
    logger.info("=" * 80)
    
    passed = sum(1 for r in results if r.status.value == "pass")
    failed = sum(1 for r in results if r.status.value == "fail")
    
    logger.info(f"\nTotal Tests: {len(results)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    
    # Detailed results
    logger.info("\nDetailed Results:")
    logger.info("-" * 80)
    
    for result in results:
        status_symbol = "✓" if result.status.value == "pass" else "✗"
        logger.info(f"{status_symbol} {result.test_id}")
        logger.info(f"  Requirement: {result.requirement_id}")
        logger.info(f"  Duration: {result.duration_seconds:.2f}s")
        
        if result.error_message:
            logger.info(f"  Error: {result.error_message}")
        
        if result.metrics:
            logger.info(f"  Memory Peak: {result.metrics.memory_peak_mb:.2f} MB")
            logger.info(f"  CPU Peak: {result.metrics.cpu_peak_percent:.1f}%")
        
        logger.info("")
    
    # Summary by requirement
    logger.info("\n" + "=" * 80)
    logger.info("Results by Requirement")
    logger.info("=" * 80)
    
    requirements = {}
    for result in results:
        for req_id in result.requirement_id.split(","):
            if req_id not in requirements:
                requirements[req_id] = {"passed": 0, "failed": 0}
            
            if result.status.value == "pass":
                requirements[req_id]["passed"] += 1
            else:
                requirements[req_id]["failed"] += 1
    
    for req_id in sorted(requirements.keys()):
        stats = requirements[req_id]
        total = stats["passed"] + stats["failed"]
        logger.info(f"Requirement {req_id}: {stats['passed']}/{total} passed")
    
    logger.info("\n" + "=" * 80)
    logger.info("Testing Complete")
    logger.info("=" * 80)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
