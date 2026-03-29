"""
Orchestration module for the Offline Policy Gap Analyzer.

This module provides the AnalysisPipeline class that orchestrates the complete
workflow from document parsing through gap analysis, policy revision, roadmap
generation, and output creation.
"""

from orchestration.analysis_pipeline import AnalysisPipeline

__all__ = ['AnalysisPipeline']
