"""Utility for managing application state."""
from typing import List, Dict, Optional
import streamlit as st

class StateManager:
    """Manages the application state using Streamlit's session state."""
    
    @staticmethod
    def initialize_state():
        """Initialize all required session state variables."""
        if 'document_content' not in st.session_state:
            st.session_state.document_content = ""
        if 'selected_text' not in st.session_state:
            st.session_state.selected_text = ""
        if 'visualizations' not in st.session_state:
            st.session_state.visualizations = []
        if 'selected_visualization' not in st.session_state:
            st.session_state.selected_visualization = None
    
    @staticmethod
    def update_document_content(content: str):
        """Update the document content in the session state.
        
        Args:
            content: The new document content.
        """
        st.session_state.document_content = content
    
    @staticmethod
    def update_selected_text(text: str):
        """Update the selected text in the session state.
        
        Args:
            text: The newly selected text.
        """
        st.session_state.selected_text = text
    
    @staticmethod
    def update_visualizations(visualizations: List[Dict[str, str]]):
        """Update the visualizations in the session state.
        
        Args:
            visualizations: List of visualization dictionaries.
        """
        st.session_state.visualizations = visualizations
    
    @staticmethod
    def update_selected_visualization(visualization: Optional[Dict[str, str]]):
        """Update the selected visualization in the session state.
        
        Args:
            visualization: The selected visualization dictionary or None.
        """
        st.session_state.selected_visualization = visualization
    
    @staticmethod
    def get_document_content() -> str:
        """Get the current document content.
        
        Returns:
            str: The current document content.
        """
        return st.session_state.document_content
    
    @staticmethod
    def get_selected_text() -> str:
        """Get the currently selected text.
        
        Returns:
            str: The selected text.
        """
        return st.session_state.selected_text
    
    @staticmethod
    def get_visualizations() -> List[Dict[str, str]]:
        """Get the current visualizations.
        
        Returns:
            List[Dict[str, str]]: List of visualization dictionaries.
        """
        return st.session_state.visualizations
    
    @staticmethod
    def get_selected_visualization() -> Optional[Dict[str, str]]:
        """Get the currently selected visualization.
        
        Returns:
            Optional[Dict[str, str]]: The selected visualization dictionary or None.
        """
        return st.session_state.selected_visualization 