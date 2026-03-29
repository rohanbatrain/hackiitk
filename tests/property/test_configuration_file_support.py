"""Property test for configuration file support.

Property 47: Configuration File Support
Validates: Requirements 18.1, 18.2, 18.3, 18.4, 18.5

Tests that all configurable parameters can be set via YAML/JSON.
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from utils.config_loader import ConfigLoader, AnalyzerConfig, ConfigValidationError


# Strategy for valid configuration parameters
@st.composite
def valid_config_dict(draw):
    """Generate valid configuration dictionaries."""
    config = {}
    
    # Randomly include parameters (test partial configs)
    if draw(st.booleans()):
        config['chunk_size'] = draw(st.integers(min_value=128, max_value=2048))
    
    if draw(st.booleans()):
        config['overlap'] = draw(st.integers(min_value=0, max_value=512))
    
    if draw(st.booleans()):
        config['top_k'] = draw(st.integers(min_value=1, max_value=20))
    
    if draw(st.booleans()):
        config['temperature'] = draw(st.floats(min_value=0.0, max_value=2.0))
    
    if draw(st.booleans()):
        config['max_tokens'] = draw(st.integers(min_value=64, max_value=4096))
    
    if draw(st.booleans()):
        # Generate valid severity thresholds
        covered = draw(st.floats(min_value=0.5, max_value=1.0))
        partial_high = draw(st.floats(min_value=0.3, max_value=covered))
        ambiguous_high = draw(st.floats(min_value=0.0, max_value=partial_high))
        
        config['severity_thresholds'] = {
            'covered': covered,
            'partial_high': partial_high,
            'ambiguous_high': ambiguous_high
        }
    
    if draw(st.booleans()):
        # Generate valid CSF function priority list
        functions = ['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover']
        priority = draw(st.lists(
            st.sampled_from(functions),
            min_size=1,
            max_size=6,
            unique=True
        ))
        config['csf_function_priority'] = priority
    
    if draw(st.booleans()):
        config['embedding_model'] = draw(st.text(min_size=1, max_size=50))
    
    if draw(st.booleans()):
        config['llm_model'] = draw(st.text(min_size=1, max_size=50))
    
    if draw(st.booleans()):
        config['vector_store_backend'] = draw(st.sampled_from(['chromadb', 'faiss']))
    
    return config


class TestConfigurationFileSupport:
    """Property tests for configuration file support."""
    
    @given(config_dict=valid_config_dict())
    @settings(max_examples=50, deadline=None)
    def test_yaml_configuration_support(self, config_dict):
        """Test that all configurable parameters can be set via YAML.
        
        Property: For any valid configuration dictionary, saving to YAML
        and loading produces a config with the specified parameters.
        """
        loader = ConfigLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            yaml_path = f.name
        
        try:
            # Load configuration from YAML
            config = loader.load(yaml_path)
            
            # Verify all specified parameters are set correctly
            for param, value in config_dict.items():
                actual_value = getattr(config, param)
                
                if isinstance(value, dict):
                    # For dictionaries, check all keys
                    for key, val in value.items():
                        assert key in actual_value
                        assert actual_value[key] == pytest.approx(val, abs=1e-6)
                elif isinstance(value, list):
                    # For lists, check all elements
                    assert actual_value == value
                elif isinstance(value, float):
                    # For floats, use approximate comparison
                    assert actual_value == pytest.approx(value, abs=1e-6)
                else:
                    # For other types, exact comparison
                    assert actual_value == value
            
            # Verify unspecified parameters use defaults
            defaults = AnalyzerConfig()
            for param in ['chunk_size', 'overlap', 'top_k', 'temperature', 'max_tokens']:
                if param not in config_dict:
                    assert getattr(config, param) == getattr(defaults, param)
        
        finally:
            Path(yaml_path).unlink()
    
    @given(config_dict=valid_config_dict())
    @settings(max_examples=50, deadline=None)
    def test_json_configuration_support(self, config_dict):
        """Test that all configurable parameters can be set via JSON.
        
        Property: For any valid configuration dictionary, saving to JSON
        and loading produces a config with the specified parameters.
        """
        loader = ConfigLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_dict, f)
            json_path = f.name
        
        try:
            # Load configuration from JSON
            config = loader.load(json_path)
            
            # Verify all specified parameters are set correctly
            for param, value in config_dict.items():
                actual_value = getattr(config, param)
                
                if isinstance(value, dict):
                    for key, val in value.items():
                        assert key in actual_value
                        assert actual_value[key] == pytest.approx(val, abs=1e-6)
                elif isinstance(value, list):
                    assert actual_value == value
                elif isinstance(value, float):
                    assert actual_value == pytest.approx(value, abs=1e-6)
                else:
                    assert actual_value == value
        
        finally:
            Path(json_path).unlink()
    
    @given(
        chunk_size=st.integers(min_value=128, max_value=2048),
        overlap=st.integers(min_value=0, max_value=512),
        top_k=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=30, deadline=None)
    def test_chunking_and_retrieval_parameters(self, chunk_size, overlap, top_k):
        """Test that chunking and retrieval parameters are configurable.
        
        Property: chunk_size, overlap, and top_k can be set to any valid value.
        Validates Requirements 18.2.
        """
        config_dict = {
            'chunk_size': chunk_size,
            'overlap': overlap,
            'top_k': top_k
        }
        
        loader = ConfigLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            yaml_path = f.name
        
        try:
            config = loader.load(yaml_path)
            
            assert config.chunk_size == chunk_size
            assert config.overlap == overlap
            assert config.top_k == top_k
        
        finally:
            Path(yaml_path).unlink()
    
    @given(
        temperature=st.floats(min_value=0.0, max_value=2.0),
        max_tokens=st.integers(min_value=64, max_value=4096)
    )
    @settings(max_examples=30, deadline=None)
    def test_llm_generation_parameters(self, temperature, max_tokens):
        """Test that LLM generation parameters are configurable.
        
        Property: temperature and max_tokens can be set to any valid value.
        Validates Requirements 18.3.
        """
        config_dict = {
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        loader = ConfigLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_dict, f)
            json_path = f.name
        
        try:
            config = loader.load(json_path)
            
            assert config.temperature == pytest.approx(temperature, abs=1e-6)
            assert config.max_tokens == max_tokens
        
        finally:
            Path(json_path).unlink()
    
    @given(
        covered=st.floats(min_value=0.5, max_value=1.0),
        partial_high=st.floats(min_value=0.3, max_value=0.9),
        ambiguous_high=st.floats(min_value=0.0, max_value=0.5)
    )
    @settings(max_examples=30, deadline=None)
    def test_severity_thresholds_configuration(self, covered, partial_high, ambiguous_high):
        """Test that severity thresholds are configurable.
        
        Property: severity_thresholds can be set to any valid threshold values.
        Validates Requirements 18.4.
        """
        # Ensure proper ordering
        assume(ambiguous_high <= partial_high <= covered)
        
        config_dict = {
            'severity_thresholds': {
                'covered': covered,
                'partial_high': partial_high,
                'ambiguous_high': ambiguous_high
            }
        }
        
        loader = ConfigLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            yaml_path = f.name
        
        try:
            config = loader.load(yaml_path)
            
            assert config.severity_thresholds['covered'] == pytest.approx(covered, abs=1e-6)
            assert config.severity_thresholds['partial_high'] == pytest.approx(partial_high, abs=1e-6)
            assert config.severity_thresholds['ambiguous_high'] == pytest.approx(ambiguous_high, abs=1e-6)
        
        finally:
            Path(yaml_path).unlink()
    
    @given(
        priority_list=st.lists(
            st.sampled_from(['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover']),
            min_size=1,
            max_size=6,
            unique=True
        )
    )
    @settings(max_examples=30, deadline=None)
    def test_csf_function_priority_configuration(self, priority_list):
        """Test that CSF function priority is configurable.
        
        Property: csf_function_priority can be set to any valid function list.
        Validates Requirements 18.5.
        """
        config_dict = {
            'csf_function_priority': priority_list
        }
        
        loader = ConfigLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_dict, f)
            json_path = f.name
        
        try:
            config = loader.load(json_path)
            
            assert config.csf_function_priority == priority_list
        
        finally:
            Path(json_path).unlink()
    
    def test_invalid_parameter_rejected(self):
        """Test that invalid parameters are rejected with clear error messages."""
        config_dict = {
            'invalid_param': 'some_value',
            'chunk_size': 512
        }
        
        loader = ConfigLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            yaml_path = f.name
        
        try:
            with pytest.raises(ConfigValidationError) as exc_info:
                loader.load(yaml_path)
            
            assert 'invalid_param' in str(exc_info.value)
        
        finally:
            Path(yaml_path).unlink()
    
    def test_out_of_range_values_rejected(self):
        """Test that out-of-range values are rejected."""
        config_dict = {
            'chunk_size': 5000,  # Above maximum
            'temperature': 3.0   # Above maximum
        }
        
        loader = ConfigLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            yaml_path = f.name
        
        try:
            with pytest.raises(ConfigValidationError) as exc_info:
                loader.load(yaml_path)
            
            error_msg = str(exc_info.value)
            assert 'chunk_size' in error_msg or 'temperature' in error_msg
        
        finally:
            Path(yaml_path).unlink()
