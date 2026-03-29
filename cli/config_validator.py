#!/usr/bin/env python3
"""
Configuration file validation for policy-analyzer.

Validates YAML/JSON configuration files against expected schema.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


class ConfigValidator:
    """Validates configuration files."""
    
    # Expected configuration schema
    SCHEMA = {
        'chunk_size': {'type': int, 'min': 128, 'max': 2048, 'default': 512},
        'overlap': {'type': int, 'min': 0, 'max': 512, 'default': 50},
        'top_k': {'type': int, 'min': 1, 'max': 20, 'default': 5},
        'temperature': {'type': float, 'min': 0.0, 'max': 1.0, 'default': 0.1},
        'max_tokens': {'type': int, 'min': 128, 'max': 4096, 'default': 512},
        'model_name': {'type': str, 'default': 'qwen2.5:3b-instruct'},
        'severity_thresholds': {
            'type': dict,
            'schema': {
                'critical': {'type': float, 'min': 0.0, 'max': 1.0},
                'high': {'type': float, 'min': 0.0, 'max': 1.0},
                'medium': {'type': float, 'min': 0.0, 'max': 1.0},
                'low': {'type': float, 'min': 0.0, 'max': 1.0}
            }
        },
        'csf_function_priority': {
            'type': list,
            'optional': True,
            'items': {'type': str, 'choices': ['GV', 'ID', 'PR', 'DE', 'RS', 'RC']}
        }
    }
    
    def __init__(self, config_path: Path):
        """Initialize validator.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.config: Dict[str, Any] = {}
    
    def load_config(self) -> bool:
        """Load configuration file.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.suffix in ['.yaml', '.yml']:
                    self.config = yaml.safe_load(f)
                elif self.config_path.suffix == '.json':
                    self.config = json.load(f)
                else:
                    self.errors.append(f"Unsupported file format: {self.config_path.suffix}")
                    return False
            
            if not isinstance(self.config, dict):
                self.errors.append("Configuration must be a dictionary/object")
                return False
            
            return True
            
        except FileNotFoundError:
            self.errors.append(f"Configuration file not found: {self.config_path}")
            return False
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {e}")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON parsing error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error loading configuration: {e}")
            return False
    
    def validate_field(self, key: str, value: Any, schema: Dict[str, Any]) -> bool:
        """Validate a single configuration field.
        
        Args:
            key: Field name
            value: Field value
            schema: Field schema
            
        Returns:
            True if valid, False otherwise
        """
        # Check type
        expected_type = schema['type']
        if not isinstance(value, expected_type):
            self.errors.append(
                f"{key}: Expected {expected_type.__name__}, got {type(value).__name__}"
            )
            return False
        
        # Check numeric ranges
        if expected_type in [int, float]:
            if 'min' in schema and value < schema['min']:
                self.errors.append(
                    f"{key}: Value {value} is below minimum {schema['min']}"
                )
                return False
            if 'max' in schema and value > schema['max']:
                self.errors.append(
                    f"{key}: Value {value} exceeds maximum {schema['max']}"
                )
                return False
        
        # Check string choices
        if expected_type == str and 'choices' in schema:
            if value not in schema['choices']:
                self.errors.append(
                    f"{key}: Invalid value '{value}'. Must be one of: {schema['choices']}"
                )
                return False
        
        # Check nested dict
        if expected_type == dict and 'schema' in schema:
            for nested_key, nested_schema in schema['schema'].items():
                if nested_key not in value:
                    self.errors.append(f"{key}.{nested_key}: Required field missing")
                    return False
                if not self.validate_field(f"{key}.{nested_key}", value[nested_key], nested_schema):
                    return False
        
        # Check list items
        if expected_type == list and 'items' in schema:
            for i, item in enumerate(value):
                if not self.validate_field(f"{key}[{i}]", item, schema['items']):
                    return False
        
        return True
    
    def validate(self) -> bool:
        """Validate the configuration.
        
        Returns:
            True if valid, False otherwise
        """
        if not self.load_config():
            return False
        
        # Check for unknown fields
        for key in self.config.keys():
            if key not in self.SCHEMA:
                self.warnings.append(f"Unknown configuration field: {key}")
        
        # Validate each field
        for key, schema in self.SCHEMA.items():
            if key not in self.config:
                if schema.get('optional', False):
                    continue
                else:
                    self.warnings.append(
                        f"{key}: Missing (will use default: {schema.get('default', 'N/A')})"
                    )
                    continue
            
            self.validate_field(key, self.config[key], schema)
        
        # Additional validation rules
        self._validate_severity_thresholds()
        self._validate_chunk_overlap()
        
        return len(self.errors) == 0
    
    def _validate_severity_thresholds(self):
        """Validate severity thresholds are in descending order."""
        if 'severity_thresholds' in self.config:
            thresholds = self.config['severity_thresholds']
            if all(k in thresholds for k in ['critical', 'high', 'medium', 'low']):
                if not (thresholds['critical'] >= thresholds['high'] >= 
                        thresholds['medium'] >= thresholds['low']):
                    self.errors.append(
                        "severity_thresholds: Must be in descending order "
                        "(critical >= high >= medium >= low)"
                    )
    
    def _validate_chunk_overlap(self):
        """Validate chunk overlap is less than chunk size."""
        if 'chunk_size' in self.config and 'overlap' in self.config:
            if self.config['overlap'] >= self.config['chunk_size']:
                self.errors.append(
                    f"overlap ({self.config['overlap']}) must be less than "
                    f"chunk_size ({self.config['chunk_size']})"
                )
    
    def print_results(self, verbose: bool = False):
        """Print validation results.
        
        Args:
            verbose: Show detailed information
        """
        if len(self.errors) == 0 and len(self.warnings) == 0:
            console.print(f"[green]✓ Configuration is valid: {self.config_path}[/green]")
            
            if verbose:
                self._print_config_summary()
            
            return
        
        # Print errors
        if self.errors:
            console.print(f"\n[red]✗ Configuration has {len(self.errors)} error(s):[/red]\n")
            for error in self.errors:
                console.print(f"  [red]•[/red] {error}")
        
        # Print warnings
        if self.warnings:
            console.print(f"\n[yellow]⚠ Configuration has {len(self.warnings)} warning(s):[/yellow]\n")
            for warning in self.warnings:
                console.print(f"  [yellow]•[/yellow] {warning}")
        
        console.print()
        
        if verbose and len(self.errors) == 0:
            self._print_config_summary()
    
    def _print_config_summary(self):
        """Print configuration summary table."""
        table = Table(
            title="Configuration Summary",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Parameter", style="cyan", width=25)
        table.add_column("Value", style="white", width=30)
        table.add_column("Default", style="dim", width=20)
        
        for key, schema in self.SCHEMA.items():
            value = self.config.get(key, schema.get('default', 'N/A'))
            default = schema.get('default', 'N/A')
            
            # Format value for display
            if isinstance(value, dict):
                value_str = json.dumps(value, indent=2)
            elif isinstance(value, list):
                value_str = ', '.join(str(v) for v in value)
            else:
                value_str = str(value)
            
            # Highlight if different from default
            if value != default:
                value_str = f"[bold]{value_str}[/bold]"
            
            table.add_row(key, value_str, str(default))
        
        console.print()
        console.print(table)


def validate_config_file(config_path: Path, verbose: bool = False) -> bool:
    """Validate a configuration file.
    
    Args:
        config_path: Path to configuration file
        verbose: Show detailed information
        
    Returns:
        True if valid, False otherwise
    """
    validator = ConfigValidator(config_path)
    is_valid = validator.validate()
    validator.print_results(verbose)
    return is_valid
