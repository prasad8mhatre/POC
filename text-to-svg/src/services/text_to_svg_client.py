"""Client for the Text to SVG service."""
from typing import Dict, List
from mcp import client
from src.services.text_to_svg_service import TextToSVGService

@client(TextToSVGService)
class TextToSVGClient:
    """Client for interacting with the Text to SVG service."""
    
    def __init__(self):
        """Initialize the client."""
        pass

    async def generate_visualizations(self, text: str) -> List[Dict[str, str]]:
        """Generate SVG visualizations from text.
        
        Args:
            text: The input text to visualize.
            
        Returns:
            List of dictionaries containing visualization data:
            - description: Description of the visualization
            - svg_code: The SVG markup
        """
        return await self.server.generate_visualizations(text)

    async def get_visualization_types(self) -> List[str]:
        """Get available visualization types.
        
        Returns:
            List of available visualization type names.
        """
        return await self.server.get_visualization_types() 