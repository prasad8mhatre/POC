"""Main application entry point."""
import streamlit as st
import logging

from src.config.settings import (
    APP_TITLE, 
    APP_DESCRIPTION, 
    DEFAULT_COLUMN_RATIO,
    THEME_COLOR,
    SECONDARY_COLOR
)
from src.components.document_editor import DocumentEditor
from src.components.visualization_panel import VisualizationPanel
from src.services.gemini_service import GeminiService
from src.utils.state_manager import StateManager
from src.utils.logger import get_logger

# Configure application logger
logger = get_logger("storyviz", level=logging.INFO)

class Application:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application components."""
        logger.info("Initializing StoryViz AI application")
        self.state_manager = StateManager()
        self.gemini_service = GeminiService()
        self.document_editor = DocumentEditor(self.state_manager)
        self.visualization_panel = VisualizationPanel(self.state_manager)
    
    def _handle_visualization_generation(self, text: str):
        """Handle the generation of visualizations.
        
        Args:
            text: The text to generate visualizations for.
        """
        logger.info("Handling visualization generation request")
        logger.debug(f"Text length: {len(text)} characters")
        
        self.state_manager.update_selected_text(text)
        visualizations = self.gemini_service.generate_visualizations(text)
        self.state_manager.update_visualizations(visualizations)
        
        if visualizations:
            logger.info(f"Generated {len(visualizations)} visualizations")
        else:
            logger.warning("No visualizations were generated")
    
    def _set_page_style(self):
        """Set custom page styling."""
        logger.debug("Applying custom page styling")
        st.markdown(f"""
        <style>
        .stApp {{
            background-color: #f8f9fa;
        }}
        .main .block-container {{
            padding-top: 2rem;
        }}
        h1 {{
            color: {THEME_COLOR};
        }}
        .stButton>button {{
            background-color: {THEME_COLOR};
            color: white;
        }}
        .stButton>button:hover {{
            background-color: {SECONDARY_COLOR};
            color: black;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Run the application."""
        try:
            logger.info("Starting StoryViz AI application")
            
            # Configure the page
            st.set_page_config(
                layout="wide",
                page_title=APP_TITLE,
                page_icon="📊"
            )
            logger.debug("Page configuration set")
            
            # Apply custom styling
            self._set_page_style()
            
            # Header section
            st.title(APP_TITLE)
            st.markdown(APP_DESCRIPTION)
            
            # Add a horizontal line
            st.markdown("---")
            
            # Initialize the session state
            self.state_manager.initialize_state()
            logger.debug("Session state initialized")
            
            # Create the main layout
            col1, col2 = st.columns(DEFAULT_COLUMN_RATIO)
            
            # Render the components
            with col1:
                selected_text = self.document_editor.render()
                if selected_text != self.state_manager.get_selected_text():
                    logger.debug("Updating selected text")
                    self.state_manager.update_selected_text(selected_text)
            
            with col2:
                self.visualization_panel.render(self._handle_visualization_generation)
            
            # Footer
            st.markdown("---")
            st.markdown(
                """
                <div style='text-align: center; color: #666;'>
                Transform your business stories into compelling visual narratives with AI
                </div>
                """,
                unsafe_allow_html=True
            )
            
            logger.info("Application running successfully")
            
        except Exception as e:
            logger.error("Error running application", exc_info=True)
            st.error("An error occurred while running the application. Please check the logs for details.")

def main():
    """Application entry point."""
    try:
        logger.info("Starting main application")
        app = Application()
        app.run()
    except Exception as e:
        logger.critical("Critical error in main application", exc_info=True)
        st.error("A critical error occurred. Please contact support.")

if __name__ == "__main__":
    main() 