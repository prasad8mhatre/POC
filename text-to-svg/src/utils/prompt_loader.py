"""Utility for loading and managing prompts from YAML files."""
import os
from typing import Dict, Any
import yaml

class PromptLoader:
    """Loads and manages prompts from YAML files."""
    
    def __init__(self, prompts_dir: str = None):
        """Initialize the prompt loader.
        
        Args:
            prompts_dir: Directory containing prompt YAML files.
                        Defaults to src/prompts if not specified.
        """
        if prompts_dir is None:
            # Get the directory of the current file
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            prompts_dir = os.path.join(current_dir, 'prompts')
        
        self.prompts_dir = prompts_dir
        self.prompts: Dict[str, Any] = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """Load all YAML files from the prompts directory."""
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                file_path = os.path.join(self.prompts_dir, filename)
                with open(file_path, 'r') as f:
                    self.prompts.update(yaml.safe_load(f))
    
    def get_prompt(self, prompt_key: str) -> str:
        """Get a prompt by its key.
        
        Args:
            prompt_key: The key to look up the prompt.
            
        Returns:
            str: The prompt template.
            
        Raises:
            KeyError: If the prompt key is not found.
        """
        # Navigate nested dictionary using dot notation
        keys = prompt_key.split('.')
        value = self.prompts
        for key in keys:
            value = value[key]
        
        if isinstance(value, dict) and 'prompt' in value:
            return value['prompt']
        return value
    
    def format_prompt(self, prompt_key: str, **kwargs) -> str:
        """Get and format a prompt with the provided arguments.
        
        Args:
            prompt_key: The key to look up the prompt.
            **kwargs: Format arguments for the prompt template.
            
        Returns:
            str: The formatted prompt.
        """
        prompt_template = self.get_prompt(prompt_key)
        return prompt_template.format(**kwargs) 