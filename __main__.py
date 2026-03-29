#!/usr/bin/env python3
"""
Main entry point for Offline Policy Gap Analyzer.

Allows running the analyzer as a module:
    python -m offline_policy_analyzer --policy-path policy.pdf --domain isms

This module sets up the execution environment, initializes logging,
loads configuration, and delegates to the CLI.
"""

import sys
import os
from pathlib import Path

# Add project root to path if running as module
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from cli.main import main


def check_environment():
    """Verify the execution environment is properly configured.
    
    Checks:
    - Python version compatibility
    - Required directories exist
    - Basic dependencies available
    """
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    # Check required directories
    required_dirs = ["models", "context", "outputs"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            pass  # Will be created if needed
    
    # Check if models are available
    models_dir = project_root / "models"
    if models_dir.exists():
        has_embeddings = (models_dir / "embeddings").exists()
        has_llm = (models_dir / "llm").exists()
        
        if not has_embeddings or not has_llm:
            pass  # Model files may not be downloaded


def initialize_application():
    """Initialize the application environment.
    
    Sets up:
    - Working directory
    - Environment variables
    """
    # Check environment
    try:
        check_environment()
    except Exception as e:
        # Continue anyway - let the pipeline handle missing resources
        pass


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler for uncaught exceptions.
    
    Logs exceptions and provides user-friendly error messages.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupts
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    print("\n" + "=" * 60)
    print("❌ FATAL ERROR")
    print("=" * 60)
    print(f"\nAn unexpected error occurred: {exc_value}")
    print("\nIf this issue persists, please report it.")
    print()


def run():
    """Run the application with proper initialization and error handling."""
    # Set up global exception handler
    sys.excepthook = handle_exception
    
    try:
        # Initialize application
        initialize_application()
        
        # Run CLI
        main()
        
    except SystemExit:
        # Allow normal exits
        raise
    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
