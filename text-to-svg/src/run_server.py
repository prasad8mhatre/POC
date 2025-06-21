"""Script to run the MCP server."""
import asyncio
from mcp import Server
from src.services.text_to_svg_service import TextToSVGService
from src.utils.logger import setup_logger

async def main():
    """Run the MCP server."""
    logger = setup_logger('mcp_server')
    logger.info("Starting MCP server")
    
    try:
        # Create and start the server
        server = Server()
        
        # Register the TextToSVG service
        server.register(TextToSVGService())
        
        # Start the server
        await server.serve()
        logger.info("MCP server is running")
        
        # Keep the server running
        await asyncio.Future()  # run forever
        
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 