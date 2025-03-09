import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import Field

from links.base_link import BaseLink
from chain import LinkConfig

class ExampleLinkConfig(LinkConfig):
    """Extended configuration for ExampleLink with specific parameters"""
    # Add additional type-specific fields
    max_retries: int = Field(default=3, description="Maximum number of retries")
    input_data: Optional[Dict[str, Any]] = Field(default=None, description="Input data for processing")
    use_cache: bool = Field(default=True, description="Whether to use cache")

class ExampleLink(BaseLink):
    """Example Link implementation showing how to leverage LinkConfig"""
    
    def get_required_fields(self) -> list:
        """Returns a list of required fields for this link."""
        # Extend the base required fields
        return super().get_required_fields() + ["parameters"]
    
    def _validate_config_impl(self, config: LinkConfig) -> None:
        """
        Validate that the config has all necessary fields for this link type.
        
        Args:
            config: The configuration to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Check that we have the required parameters in the config
        required_params = ["query"]
        if config.parameters is None:
            raise ValueError(f"Parameters section is required for {self.__class__.__name__}")
            
        for param in required_params:
            if param not in config.parameters:
                raise ValueError(f"Required parameter '{param}' missing from {config.name} configuration")
    
    def _execute_impl(self, config: LinkConfig, context: Dict[str, Any]) -> Any:
        """
        Execute the link implementation with the given config and context.
        
        Args:
            config: The LinkConfig for this step
            context: Current execution context
            
        Returns:
            The result of execution
        """
        # Log the execution start
        logging.info(f"Executing example link with config: {config.name}")
        
        # Get parameters
        query = config.parameters.get("query")
        max_retries = 3  # Default if not in config
        
        # Use advanced configuration if available
        if isinstance(config, ExampleLinkConfig):
            max_retries = config.max_retries
            logging.debug(f"Using extended config with max_retries={max_retries}")
        
        # Simulate processing
        logging.info(f"Processing query: {query}")
        
        # Example returning some processed results
        results = {
            "processed_query": query,
            "timestamp": datetime.now().isoformat(),
            "results": [
                {"id": 1, "value": "Result 1"},
                {"id": 2, "value": "Result 2"}
            ]
        }
        
        # Return the processed data
        return results
