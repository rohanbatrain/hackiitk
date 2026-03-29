"""Property test for configuration default fallback.

Property 48: Configuration Default Fallback
Validates: Requirements 18.6

Tests that missing config file uses documented defaults.
"""

import pytest
import tempfile
import yaml
import json
from pathlib import Path
from hypothesis import given, strategies as st, settings
from utils.config_loader import ConfigLoader, AnalyzerConfig


class TestConfigurationDefaultFallback:
    """Property tests for configuration default fallback."""
    
    def test_no_config_file_uses_defaults(self):
        """Test that when no config file is provided, documented defaults are used.
        
        Property: Loading with config_path=None produces default configuration.
        Validates Requirement 18.6.
        """
        loader = ConfigLoader()
        config = loader.load(config_path=None)
        
        # Get documented defaults
        defaults = AnalyzerConfig()
        
        # Verify all parameters match defaults
        assert config.chunk_size == defaults.chunk_size == 512
        assert config.overlap == defaults.overlap == 50
        assert config.top_k == defaults.top_k == 5
        assert config.temperature == defaults.temperature == 0.1
        assert config.max_tokens == defaults.max_tokens == 512
        assert config.severity_thresholds == defaults.severity_thresholds
        assert config.csf_function_priority == defaults.csf_function_priority
        assert config.embedding_model == defaults.embedding_model
        assert config.llm_model == defaults.llm_model
        assert config.vector_store_backend == defaults.vector_store_backend
    
    def test_missing_config_file_uses_defaults(self):
        """Test that when config file doesn't exist, defaults are used.
        
        Property: Loading a non-existent file raises FileNotFoundError
        but can be caught and defaults used instead.
        """
        loader = ConfigLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load('/nonexistent/path/config.yaml')
        
        # After error, can load defaults
        config = loader.load(config_path=None)
        defaults = AnalyzerConfig()
        
        assert config.chunk_size == defaults.chunk_size
        assert config.temperature == defaults.temperature
    
    @given(
        include_chunk_size=st.booleans(),
        include_temperature=st.booleans(),
        include_top_k=st.booleans()
    )
    @settings(max_examples=20, deadline=None)
    def test_partial_config_uses_defaults_for_missing_params(
        self, include_chunk_size, include_temperature, include_top_k
    ):
        """Test that partial configs use defaults for unspecified parameters.
        
        Property: For any subset of parameters specified in config file,
        unspecified parameters use documented defaults.
        Validates Requirement 18.6.
        """
        # Create partial configuration
        config_dict = {}
        if include_chunk_size:
            config_dict['chunk_size'] = 1024
        if include_temperature:
            config_dict['temperature'] = 0.5
        if include_top_k:
            config_dict['top_k'] = 10
        
        loader = ConfigLoader()
        defaults = AnalyzerConfig()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            yaml_path = f.name
        
        try:
            config = loader.load(yaml_path)
            
            # Verify specified parameters are set
            if include_chunk_size:
                assert config.chunk_size == 1024
            else:
                assert config.chunk_size == defaults.chunk_size
            
            if include_temperature:
                assert config.temperature == pytest.approx(0.5, abs=1e-6)
            else:
                assert config.temperature == defaults.temperature
            
            if include_top_k:
                assert config.top_k == 10
            else:
                assert config.top_k == defaults.top_k
            
            # Verify unspecified parameters use defaults
            assert config.overlap == defaults.overlap
            assert config.max_tokens == defaults.max_tokens
            assert config.severity_thresholds == defaults.severity_thresholds
        
        finally:
            Path(yaml_path).unlink()
    
    def test_empty_config_file_uses_all_defaults(self):
        """Test that an empty config file uses all defaults.
        
        Property: An empty YAML/JSON file produces default configuration.
        """
        loader = ConfigLoader()
        defaults = AnalyzerConfig()
        
        # Test with empty YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('')  # Empty file
            yaml_path = f.name
        
        try:
            config = loader.load(yaml_path)
            
            assert config.chunk_size == defaults.chunk_size
            assert config.overlap == defaults.overlap
            assert config.top_k == defaults.top_k
            assert config.temperature == defaults.temperature
            assert config.max_tokens == defaults.max_tokens
        
        finally:
            Path(yaml_path).unlink()
        
        # Test with empty JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            json_path = f.name
        
        try:
            config = loader.load(json_path)
            
            assert config.chunk_size == defaults.chunk_size
            assert config.overlap == defaults.overlap
            assert config.top_k == defaults.top_k
        
        finally:
            Path(json_path).unlink()
    
    def test_get_default_config_static_method(self):
        """Test that static method returns documented defaults.
        
        Property: ConfigLoader.get_default_config() returns same defaults
        as loading with no config file.
        """
        static_defaults = ConfigLoader.get_default_config()
        loader = ConfigLoader()
        loaded_defaults = loader.load(config_path=None)
        
        assert static_defaults.chunk_size == loaded_defaults.chunk_size
        assert static_defaults.overlap == loaded_defaults.overlap
        assert static_defaults.top_k == loaded_defaults.top_k
        assert static_defaults.temperature == loaded_defaults.temperature
        assert static_defaults.max_tokens == loaded_defaults.max_tokens
        assert static_defaults.severity_thresholds == loaded_defaults.severity_thresholds
        assert static_defaults.csf_function_priority == loaded_defaults.csf_function_priority
    
    @given(
        params_to_include=st.lists(
            st.sampled_from([
                'chunk_size', 'overlap', 'top_k', 'temperature', 
                'max_tokens', 'embedding_model', 'llm_model'
            ]),
            min_size=0,
            max_size=7,
            unique=True
        )
    )
    @settings(max_examples=30, deadline=None)
    def test_arbitrary_partial_configs_use_defaults(self, params_to_include):
        """Test that any arbitrary subset of parameters uses defaults for rest.
        
        Property: For any subset S of configurable parameters, loading a config
        with only S specified results in S having custom values and all other
        parameters having default values.
        """
        # Create partial config with arbitrary parameters
        config_dict = {}
        custom_values = {
            'chunk_size': 1024,
            'overlap': 100,
            'top_k': 10,
            'temperature': 0.5,
            'max_tokens': 1024,
            'embedding_model': 'custom-model',
            'llm_model': 'custom-llm'
        }
        
        for param in params_to_include:
            config_dict[param] = custom_values[param]
        
        loader = ConfigLoader()
        defaults = AnalyzerConfig()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            yaml_path = f.name
        
        try:
            config = loader.load(yaml_path)
            
            # Verify included parameters have custom values
            for param in params_to_include:
                actual = getattr(config, param)
                expected = custom_values[param]
                if isinstance(expected, float):
                    assert actual == pytest.approx(expected, abs=1e-6)
                else:
                    assert actual == expected
            
            # Verify excluded parameters have default values
            all_params = set(custom_values.keys())
            excluded_params = all_params - set(params_to_include)
            
            for param in excluded_params:
                actual = getattr(config, param)
                default = getattr(defaults, param)
                if isinstance(default, float):
                    assert actual == pytest.approx(default, abs=1e-6)
                else:
                    assert actual == default
        
        finally:
            Path(yaml_path).unlink()
    
    def test_defaults_are_documented_and_consistent(self):
        """Test that default values are consistent across all access methods.
        
        Property: Defaults obtained through different methods are identical.
        """
        # Method 1: Direct instantiation
        direct_defaults = AnalyzerConfig()
        
        # Method 2: Static method
        static_defaults = ConfigLoader.get_default_config()
        
        # Method 3: Loading with None
        loader = ConfigLoader()
        loaded_defaults = loader.load(config_path=None)
        
        # All methods should produce identical defaults
        assert direct_defaults.chunk_size == static_defaults.chunk_size == loaded_defaults.chunk_size
        assert direct_defaults.overlap == static_defaults.overlap == loaded_defaults.overlap
        assert direct_defaults.top_k == static_defaults.top_k == loaded_defaults.top_k
        assert direct_defaults.temperature == static_defaults.temperature == loaded_defaults.temperature
        assert direct_defaults.max_tokens == static_defaults.max_tokens == loaded_defaults.max_tokens
        assert direct_defaults.severity_thresholds == static_defaults.severity_thresholds == loaded_defaults.severity_thresholds
        assert direct_defaults.csf_function_priority == static_defaults.csf_function_priority == loaded_defaults.csf_function_priority
