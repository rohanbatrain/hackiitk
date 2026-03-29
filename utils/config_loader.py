"""Configuration loader for the Offline Policy Gap Analyzer.

This module provides configuration management with YAML/JSON support,
schema validation, and documented default values.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict


@dataclass
class AnalyzerConfig:
    """Configuration parameters for the Policy Analyzer.
    
    All parameters have documented defaults that are used when no config file
    is provided or when specific parameters are missing.
    """
    
    # Text chunking parameters
    chunk_size: int = 512  # Maximum tokens per chunk
    overlap: int = 50  # Token overlap between consecutive chunks
    
    # Retrieval parameters
    top_k: int = 5  # Number of results to retrieve
    
    # LLM generation parameters
    temperature: float = 0.1  # Sampling temperature (low for determinism)
    max_tokens: int = 512  # Maximum generation length
    
    # Severity thresholds for gap classification
    severity_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'covered': 0.8,  # Score > 0.8 = Covered
        'partial_high': 0.5,  # Score 0.5-0.8 = Partial
        'ambiguous_high': 0.3,  # Score 0.3-0.5 = Ambiguous
        # Score < 0.3 = Missing
    })
    
    # CSF function priority for domain-specific analysis
    csf_function_priority: List[str] = field(default_factory=lambda: [
        'Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover'
    ])
    
    # Additional optional parameters
    embedding_model: str = 'all-MiniLM-L6-v2'
    llm_model: str = 'qwen2.5-3b-instruct'
    vector_store_backend: str = 'chromadb'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigLoader:
    """Loads and validates configuration from YAML or JSON files.
    
    Supports:
    - YAML and JSON configuration files
    - Schema validation for all parameters
    - Documented default values
    - Detailed error messages for invalid configurations
    """
    
    # Valid parameter ranges and types
    SCHEMA = {
        'chunk_size': {'type': int, 'min': 128, 'max': 2048},
        'overlap': {'type': int, 'min': 0, 'max': 512},
        'top_k': {'type': int, 'min': 1, 'max': 20},
        'temperature': {'type': float, 'min': 0.0, 'max': 2.0},
        'max_tokens': {'type': int, 'min': 64, 'max': 4096},
        'severity_thresholds': {
            'type': dict,
            'required_keys': ['covered', 'partial_high', 'ambiguous_high'],
            'value_type': float,
            'value_min': 0.0,
            'value_max': 1.0
        },
        'csf_function_priority': {
            'type': list,
            'valid_values': ['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover']
        },
        'embedding_model': {'type': str},
        'llm_model': {'type': str},
        'vector_store_backend': {'type': str, 'valid_values': ['chromadb', 'faiss']}
    }
    
    def __init__(self):
        """Initialize configuration loader."""
        self.config: Optional[AnalyzerConfig] = None
    
    def load(self, config_path: Optional[str] = None) -> AnalyzerConfig:
        """Load configuration from file or use defaults.
        
        Args:
            config_path: Path to YAML or JSON config file. If None, uses defaults.
            
        Returns:
            AnalyzerConfig with loaded or default parameters
            
        Raises:
            ConfigValidationError: If configuration is invalid
            FileNotFoundError: If config_path specified but file doesn't exist
        """
        if config_path is None:
            # Use documented defaults
            self.config = AnalyzerConfig()
            return self.config
        
        # Load configuration file
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                f"Using default configuration instead."
            )
        
        # Parse based on file extension
        try:
            with open(config_file, 'r') as f:
                if config_file.suffix in ['.yaml', '.yml']:
                    config_dict = yaml.safe_load(f)
                elif config_file.suffix == '.json':
                    config_dict = json.load(f)
                else:
                    raise ConfigValidationError(
                        f"Unsupported config file format: {config_file.suffix}\n"
                        f"Supported formats: .yaml, .yml, .json"
                    )
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"Invalid YAML syntax: {e}")
        except json.JSONDecodeError as e:
            raise ConfigValidationError(f"Invalid JSON syntax: {e}")
        
        if config_dict is None:
            config_dict = {}
        
        # Validate configuration
        self._validate_config(config_dict)
        
        # Merge with defaults (defaults for missing parameters)
        defaults = AnalyzerConfig()
        merged_config = {**asdict(defaults), **config_dict}
        
        # Create config object
        self.config = AnalyzerConfig(**merged_config)
        return self.config
    
    def _validate_config(self, config_dict: Dict[str, Any]) -> None:
        """Validate configuration against schema.
        
        Args:
            config_dict: Configuration dictionary to validate
            
        Raises:
            ConfigValidationError: If validation fails
        """
        errors = []
        
        for param, value in config_dict.items():
            if param not in self.SCHEMA:
                errors.append(f"Unknown parameter: '{param}'")
                continue
            
            schema = self.SCHEMA[param]
            
            # Type validation
            expected_type = schema['type']
            if not isinstance(value, expected_type):
                errors.append(
                    f"Parameter '{param}': expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
                continue
            
            # Range validation for numeric types
            if expected_type in [int, float]:
                if 'min' in schema and value < schema['min']:
                    errors.append(
                        f"Parameter '{param}': value {value} below minimum {schema['min']}"
                    )
                if 'max' in schema and value > schema['max']:
                    errors.append(
                        f"Parameter '{param}': value {value} above maximum {schema['max']}"
                    )
            
            # Dictionary validation
            if expected_type == dict and param == 'severity_thresholds':
                required_keys = schema.get('required_keys', [])
                missing_keys = set(required_keys) - set(value.keys())
                if missing_keys:
                    errors.append(
                        f"Parameter '{param}': missing required keys {missing_keys}"
                    )
                
                # Validate threshold values
                for key, threshold in value.items():
                    if not isinstance(threshold, (int, float)):
                        errors.append(
                            f"Parameter '{param}.{key}': expected numeric value, "
                            f"got {type(threshold).__name__}"
                        )
                    elif threshold < 0.0 or threshold > 1.0:
                        errors.append(
                            f"Parameter '{param}.{key}': value {threshold} must be between 0.0 and 1.0"
                        )
            
            # List validation
            if expected_type == list and 'valid_values' in schema:
                valid_values = schema['valid_values']
                invalid_items = [item for item in value if item not in valid_values]
                if invalid_items:
                    errors.append(
                        f"Parameter '{param}': invalid values {invalid_items}. "
                        f"Valid values: {valid_values}"
                    )
            
            # String validation with valid values
            if expected_type == str and 'valid_values' in schema:
                valid_values = schema['valid_values']
                if value not in valid_values:
                    errors.append(
                        f"Parameter '{param}': invalid value '{value}'. "
                        f"Valid values: {valid_values}"
                    )
        
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ConfigValidationError(error_message)
    
    def get_config(self) -> AnalyzerConfig:
        """Get current configuration.
        
        Returns:
            Current AnalyzerConfig instance
            
        Raises:
            RuntimeError: If no configuration loaded
        """
        if self.config is None:
            raise RuntimeError("No configuration loaded. Call load() first.")
        return self.config
    
    @staticmethod
    def get_default_config() -> AnalyzerConfig:
        """Get default configuration without loading from file.
        
        Returns:
            AnalyzerConfig with documented default values
        """
        return AnalyzerConfig()
    
    @staticmethod
    def save_config(config: AnalyzerConfig, output_path: str, format: str = 'yaml') -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration to save
            output_path: Path to output file
            format: Output format ('yaml' or 'json')
            
        Raises:
            ValueError: If format is not supported
        """
        config_dict = config.to_dict()
        
        with open(output_path, 'w') as f:
            if format == 'yaml':
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
            elif format == 'json':
                json.dump(config_dict, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}. Use 'yaml' or 'json'.")
