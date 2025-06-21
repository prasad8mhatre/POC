"""Test script for the MCP client."""
import asyncio
from src.services.text_to_svg_client import TextToSVGClient
from src.utils.logger import setup_logger

async def test_visualization_generation():
    """Test the visualization generation functionality."""
    logger = setup_logger('test_client')
    logger.info("Starting test client")
    
    try:
        # Create client instance
        client = TextToSVGClient()
        
        # Test getting visualization types
        logger.info("Testing get_visualization_types")
        types = await client.get_visualization_types()
        logger.info(f"Available visualization types: {types}")
        
        # Test text to generate visualizations
        test_text = """
        Our company's quarterly performance shows:
        - Revenue increased by 25%
        - Customer satisfaction at 92%
        - New product launch successful
        - Market share grew to 35%
        """
        
        logger.info("Testing generate_visualizations")
        logger.info(f"Input text:\n{test_text}")
        
        # Generate visualizations
        visualizations = await client.generate_visualizations(test_text)
        
        # Log results
        logger.info(f"Generated {len(visualizations)} visualizations")
        for i, viz in enumerate(visualizations, 1):
            logger.info(f"\nVisualization {i}:")
            logger.info(f"Description: {viz['description']}")
            logger.info(f"SVG length: {len(viz['svg_code'])} characters")
        
        logger.info("Test completed successfully")
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_visualization_generation()) 