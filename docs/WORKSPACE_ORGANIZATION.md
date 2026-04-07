# Workspace Organization

This document describes the cleaned and organized workspace structure.

## Directory Structure

### Core Application
- `analysis/` - Core gap analysis engine
- `cli/` - Command-line interface
- `ingestion/` - Document parsing and text processing
- `models/` - Data models and schemas
- `orchestration/` - Analysis pipeline orchestration
- `reference_builder/` - Reference catalog builders
- `reporting/` - Report and audit log generation
- `retrieval/` - Vector store and retrieval system
- `revision/` - Policy revision engine
- `utils/` - Shared utilities

### Data & Configuration
- `data/` - Reference data, policies, and test data
  - `data/policies/` - Policy documents
  - `data/test-policies/` - Test policy samples
- `vector_store/` - Vector database storage

### Documentation
- `docs/` - All project documentation
  - `docs/guides/` - User guides and quick starts
  - `docs/status-reports/` - Status and fix reports
  - `docs/summaries/` - Task and test summaries
  - `docs/presentation/` - Presentation materials

### Development
- `scripts/` - Utility and setup scripts
- `tests/` - Complete test suite
  - `tests/unit/` - Unit tests
  - `tests/integration/` - Integration tests
  - `tests/property/` - Property-based tests
  - `tests/performance/` - Performance tests
- `examples/` - Usage examples

### Build & Output
- `outputs/` - Analysis output files
- `test_outputs/` - Test execution outputs
- `audit_logs/` - Audit trail logs
- `archive/` - Archived files and old outputs
  - `archive/test-outputs/` - Old test runs
  - `archive/old-configs/` - Deprecated configs

### Environment
- `.venv/` - Python virtual environment (active)
- `.git/` - Git repository
- `.github/` - GitHub workflows
- `.kiro/` - Kiro IDE configuration

## Cleanup Actions Performed

1. **Documentation Consolidation**
   - Moved 40+ markdown files from root to `docs/`
   - Organized into subdirectories: guides, status-reports, summaries
   - Created documentation index

2. **Script Organization**
   - Moved all `.sh` scripts to `scripts/`
   - Moved utility Python scripts to `scripts/`

3. **Test Output Cleanup**
   - Archived old test run directories
   - Moved test logs to archive
   - Organized test data

4. **Virtual Environment Cleanup**
   - Removed duplicate venvs (venv, venv311, venv312, .venv-test)
   - Kept only `.venv/` as the active environment

5. **Configuration Management**
   - Moved example configs to archive
   - Kept active `config.yaml` in root

6. **Data Organization**
   - Moved test policies to `data/test-policies/`
   - Consolidated policy documents

## Root Directory Files

Only essential files remain in root:
- `README.md` - Project overview
- `setup.py` - Package setup
- `pyproject.toml` - Project metadata
- `requirements*.txt` - Dependencies
- `config.yaml` - Active configuration
- `Dockerfile` - Container definition
- `.gitignore` - Git ignore rules
- `__main__.py` - Entry point

## Next Steps

1. Review the organized structure
2. Update any hardcoded paths in scripts
3. Update CI/CD pipelines if needed
4. Consider adding `.gitignore` entries for output directories
