# Implementation Plan: GitHub Fast Test Execution

## Overview

This implementation plan creates a production-ready GitHub Actions workflow that executes all 8 test categories in parallel with intelligent caching, Ollama LLM service integration, and comprehensive result aggregation. The implementation uses Bash for the test runner script and Python for result aggregation, leveraging GitHub Actions matrix strategy for parallelization.

## Tasks

- [x] 1. Create test runner script
  - [x] 1.1 Create .github/scripts/run_tests.sh with category mapping
    - Implement bash script that accepts category and output_dir parameters
    - Map each category to corresponding test paths (property, boundary, adversarial, stress, chaos, performance, unit, integration)
    - Configure maxfail limits per category (property: 5, boundary: 5, adversarial: 5, stress: 3, chaos: 3, performance: 3, unit: 10, integration: 5)
    - Execute pytest with verbose output, short traceback, and continue-on-error flags
    - Generate JUnit XML output as junit_<category>.xml
    - Generate JSON report as report_<category>.json
    - Handle "all" category by running all test categories sequentially
    - Make script executable with proper shebang
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8, 15.3, 15.4, 15.5_

  - [x] 1.2 Write unit tests for test runner script
    - Test category mapping logic for all 8 categories
    - Test invalid category handling
    - Test output file generation
    - Test maxfail configuration per category
    - _Requirements: 13.1-13.8_

- [x] 2. Update GitHub Actions workflow with caching
  - [x] 2.1 Add pip package caching to workflow
    - Configure cache action with key based on requirements.txt hash
    - Set cache path to ~/.cache/pip
    - Add restore-keys for fallback cache matching
    - _Requirements: 2.1, 2.4, 2.5_

  - [x] 2.2 Add Hypothesis database caching to workflow
    - Configure cache action with key based on test file hashes
    - Set cache path to .hypothesis/ directory
    - Add restore-keys for fallback cache matching
    - _Requirements: 2.3, 2.4_

  - [x] 2.3 Configure Docker container image caching
    - Update container configuration to use ghcr.io registry
    - Add authentication using GITHUB_TOKEN
    - Configure network host mode for Ollama connectivity
    - _Requirements: 2.2, 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 3. Implement Ollama service management
  - [x] 3.1 Add Ollama setup step to workflow
    - Install Ollama using official install script
    - Start Ollama service in background mode
    - Add sleep delay for service readiness
    - Pull qwen2.5:3b model with fallback on failure
    - Verify Ollama service status before tests
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 3.2 Configure environment variables for Ollama
    - Set OLLAMA_HOST to http://localhost:11434
    - Set PYTHONPATH to /github/workspace
    - _Requirements: 15.1, 15.2_

- [x] 4. Configure parallel execution matrix
  - [x] 4.1 Update workflow with matrix strategy
    - Define matrix with 8 test categories
    - Set fail-fast to false for independent execution
    - Set max-parallel to 8 for concurrent execution
    - Configure continue-on-error for resilience
    - Set timeout-minutes to 120 for each job
    - _Requirements: 1.1, 1.2, 1.3, 9.1, 9.2, 9.3, 9.4, 10.1_

  - [x] 4.2 Configure workflow triggers
    - Add push trigger for main and develop branches
    - Add pull_request trigger for main and develop branches
    - Add schedule trigger for weekly runs (Sunday 2 AM)
    - Add workflow_dispatch with category selection input
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 5. Implement result collection and artifact management
  - [x] 5.1 Add artifact upload step to test jobs
    - Upload JSON, HTML, and XML result files
    - Name artifacts with test category for identification
    - Configure if-no-files-found to ignore for resilience
    - Set retention-days to 30
    - Use if: always() to upload even on failure
    - _Requirements: 4.1, 4.2, 11.1, 11.2, 11.3, 11.5_

  - [x] 5.2 Add artifact download step to aggregation job
    - Download all test-results-* artifacts
    - Store in all-test-results directory
    - _Requirements: 4.3, 11.4_

- [x] 6. Implement result aggregation logic
  - [x] 6.1 Create Python aggregation script in workflow
    - Parse JSON result files from all categories
    - Calculate total_tests, passed, failed, errors, skipped across all categories
    - Calculate total duration_seconds across all categories
    - Calculate pass_rate percentage from aggregated results
    - Generate per-category statistics with test counts
    - Calculate per-category pass rates
    - Count parallel_jobs from artifact directories
    - Handle missing artifacts gracefully (minimal dependency mode)
    - Handle malformed JSON with try-except and error logging
    - _Requirements: 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 10.4_

  - [x] 6.2 Write unit tests for aggregation logic
    - Test aggregation with complete results from all categories
    - Test aggregation with missing categories
    - Test aggregation with malformed JSON files
    - Test aggregation with zero tests (minimal dependency mode)
    - Test pass rate calculation accuracy
    - _Requirements: 5.1-5.5, 10.4_

- [x] 7. Implement production-ready report generation
  - [x] 7.1 Create report output formatting in aggregation script
    - Generate aggregated_results.json with all metrics
    - Include execution_date timestamp in ISO 8601 format
    - Include parallel_jobs count in report
    - Include category breakdown with pass rates
    - Format console output with separator lines (80 characters)
    - Display parallel jobs, total tests, passed, failed, errors, skipped
    - Display pass rate with one decimal place
    - Display duration in minutes with one decimal place
    - Display per-category breakdown with test counts and pass rates
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 14.1, 14.2, 14.3, 14.4, 14.5_

  - [x] 7.2 Implement success criteria validation
    - Calculate overall pass rate from aggregated results
    - Display "SUCCESS CRITERIA MET" when pass rate >= 95%
    - Display "SUCCESS CRITERIA NOT MET" when pass rate < 95%
    - Display "No tests executed (minimal dependency mode)" when total tests = 0
    - Use emoji indicators (✅, ⚠️, ℹ️) for visual clarity
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 7.3 Add final artifact upload for aggregated results
    - Upload aggregated_results.json as separate artifact
    - Name artifact as aggregated-test-results
    - Use if: always() to upload even on failure
    - _Requirements: 11.4_

- [x] 8. Configure error handling and resilience
  - [x] 8.1 Add continue-on-error to test execution step
    - Configure test runner step with continue-on-error: true
    - Ensure failures are captured in result files
    - _Requirements: 10.1, 10.3_

  - [x] 8.2 Configure aggregation job to always run
    - Set aggregation job with if: always() condition
    - Set needs: test-suite dependency
    - Ensure aggregation runs even when all test jobs fail
    - _Requirements: 10.5_

  - [x] 8.3 Add maxfail limits to test runner script
    - Configure pytest maxfail per category in run_tests.sh
    - Use appropriate limits (3-10) based on category
    - _Requirements: 10.2_

- [ ] 9. Checkpoint - Validate workflow execution
  - Manually trigger workflow with "all" categories
  - Verify all 8 categories run in parallel
  - Confirm cache is created and restored on second run
  - Verify Ollama service starts successfully
  - Confirm result aggregation produces correct metrics
  - Validate final report format and success criteria logic
  - Ensure all tests pass, ask the user if questions arise

- [ ] 10. Add integration tests for complete workflow
  - [~] 10.1 Test workflow with all categories
    - Trigger workflow and verify all 8 jobs execute
    - Validate aggregated results match individual results
    - _Requirements: 1.1, 1.3, 1.4_

  - [~] 10.2 Test workflow with specific category
    - Trigger workflow with manual dispatch for single category
    - Verify only selected category executes
    - _Requirements: 8.5_

  - [~] 10.3 Test cache behavior
    - Run workflow twice and verify cache hit on second run
    - Modify requirements.txt and verify cache invalidation
    - _Requirements: 2.4, 2.5_

  - [~] 10.4 Test error resilience
    - Simulate test failures and verify workflow continues
    - Verify aggregation runs even with all failures
    - _Requirements: 10.1, 10.5_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The checkpoint ensures incremental validation before final testing
- The implementation uses Bash for test runner script and Python for aggregation
- All error handling is designed for graceful degradation and resilience
