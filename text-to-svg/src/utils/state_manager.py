"""State management for the application."""
import streamlit as st
from typing import Dict, List, Optional

class StateManager:
    """Manages application state using Streamlit's session state."""
    
    def __init__(self):
        """Initialize the state manager."""
        if 'document_content' not in st.session_state:
            st.session_state.document_content = ""
        if 'selected_text' not in st.session_state:
            st.session_state.selected_text = ""
        if 'visualizations' not in st.session_state:
            st.session_state.visualizations = []
        if 'selected_visualization' not in st.session_state:
            st.session_state.selected_visualization = None

    def get_document_content(self) -> str:
        """Get the current document content.
        
        Returns:
            The current document content.
        """
        return st.session_state.document_content

    def update_document_content(self, content: str):
        """Update the document content.
        
        Args:
            content: The new document content.
        """
        st.session_state.document_content = content

    def get_selected_text(self) -> str:
        """Get the currently selected text.
        
        Returns:
            The currently selected text.
        """
        return st.session_state.selected_text

    def update_selected_text(self, text: str):
        """Update the selected text.
        
        Args:
            text: The newly selected text.
        """
        st.session_state.selected_text = text

    def get_visualizations(self) -> List[Dict[str, str]]:
        """Get the current visualizations.
        
        Returns:
            List of visualization dictionaries.
        """
        return st.session_state.visualizations

    def update_visualizations(self, visualizations: List[Dict[str, str]]):
        """Update the visualizations.
        
        Args:
            visualizations: List of new visualization dictionaries.
        """
        st.session_state.visualizations = visualizations

    def get_selected_visualization(self) -> Optional[Dict[str, str]]:
        """Get the currently selected visualization.
        
        Returns:
            The selected visualization dictionary or None.
        """
        return st.session_state.selected_visualization

    def update_selected_visualization(self, visualization: Optional[Dict[str, str]]):
        """Update the selected visualization.
        
        Args:
            visualization: The new visualization dictionary or None.
        """
        st.session_state.selected_visualization = visualization 