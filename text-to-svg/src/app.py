"""Main application module."""
import streamlit as st
from src.components.document_editor import DocumentEditor
from src.components.visualization_panel import VisualizationPanel
from src.services.text_to_svg_client import TextToSVGClient
from src.utils.state_manager import StateManager
from src.utils.logger import setup_logger

class StoryVizApp:
    """Main application class for StoryViz."""
    
    def __init__(self):
        """Initialize the application."""
        # Set up logging
        self.logger = setup_logger('storyviz')
        self.logger.info("Initializing StoryViz AI application")
        
        # Initialize state manager
        self.state_manager = StateManager()
        
        # Initialize components
        self.document_editor = DocumentEditor(self.state_manager)
        self.visualization_panel = VisualizationPanel(self.state_manager)
        
        # Initialize MCP client
        self.text_to_svg_client = TextToSVGClient()
        
        # Set page config
        st.set_page_config(
            page_title="StoryViz AI - Visual Business Storytelling",
            page_icon="🎨",
            layout="wide"
        )
        
        # Apply custom styling
        st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .main {
            padding: 2rem;
        }
        h1, h2, h3 {
            color: #1E88E5;
        }
        </style>
        """, unsafe_allow_html=True)

    async def _handle_visualization_generation(self, text: str):
        """Handle visualization generation request.
        
        Args:
            text: Text to generate visualizations for.
        """
        self.logger.info("Handling visualization generation request")
        try:
            # Generate visualizations using MCP client
            visualizations = await self.text_to_svg_client.generate_visualizations(text)
            self.state_manager.update_visualizations(visualizations)
            self.logger.info(f"Generated {len(visualizations)} visualizations")
        except Exception as e:
            self.logger.error(f"Error generating visualizations: {e}")
            st.error("Failed to generate visualizations. Please try again.")

    def run(self):
        """Run the application."""
        try:
            self.logger.info("Starting StoryViz AI application")
            
            # Display header
            st.title("StoryViz AI")
            st.markdown("Transform your business stories into professional visualizations")
            
            # Create main layout
            col1, col2 = st.columns([1, 1])
            
            # Render document editor in first column
            with col1:
                selected_text = self.document_editor.render()
                self.state_manager.update_selected_text(selected_text)
            
            # Render visualization panel in second column
            with col2:
                self.visualization_panel.render(self._handle_visualization_generation)
            
            self.logger.info("Application running successfully")
            
        except Exception as e:
            self.logger.error(f"Error running application: {e}")
            st.error("An error occurred while running the application. Please check the logs for details.")

def main():
    """Application entry point."""
    try:
        logger.info("Starting main application")
        app = StoryVizApp()
        app.run()
    except Exception as e:
        logger.critical("Critical error in main application", exc_info=True)
        st.error("A critical error occurred. Please contact support.")

if __name__ == "__main__":
    main() 