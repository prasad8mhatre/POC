"""Visualization panel component for displaying and selecting visualizations."""
import streamlit as st
from typing import List, Dict, Callable

from src.utils.state_manager import StateManager
from src.config.settings import THEME_COLOR, SECONDARY_COLOR

class VisualizationPanel:
    """Component for handling visualization display and selection."""
    
    def __init__(self, state_manager: StateManager):
        """Initialize the visualization panel.
        
        Args:
            state_manager: Instance of StateManager for state management.
        """
        self.state_manager = state_manager
    
    def render(self, on_generate_click: Callable[[str], None]):
        """Render the visualization panel component.
        
        Args:
            on_generate_click: Callback function for generate button click.
        """
        st.subheader("🎨 Business Visualizations")
        
        # Custom styling for SVG containers
        st.markdown("""
        <style>
        .svg-container {
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .svg-container svg {
            width: 100%;
            height: auto;
            max-height: 500px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Help text
        st.markdown("""
        Transform your business content into professional visualizations.
        You can either:
        - Select specific text to visualize a particular section
        - Use the entire content to generate comprehensive visualizations
        
        Common visualization types:
        - Numerical data and statistics
        - Step-by-step processes
        - Hierarchical relationships
        - Time-based information
        - Comparisons and contrasts
        """)
        
        selected_text = self.state_manager.get_selected_text()
        
        # Check if generation was triggered
        if st.session_state.get('trigger_generation', False) and selected_text:
            with st.spinner("Creating professional visualizations..."):
                on_generate_click(selected_text)
            # Reset the trigger
            st.session_state.trigger_generation = False
        
        # Show text being visualized if any
        if selected_text:
            with st.container():
                is_full_content = selected_text == self.state_manager.get_document_content()
                header = "✨ Full Content" if is_full_content else "✨ Selected Text"
                st.markdown(f"### {header}")
                # If it's the full content, show a note
                if is_full_content:
                    st.info("Generating visualizations for the entire document content")
                st.markdown(f"*{selected_text}*")
        else:
            # Show instruction when no text is available
            st.info("👆 Write your content and click generate to create visualizations")
        
        visualizations = self.state_manager.get_visualizations()
        
        if visualizations:
            st.markdown("### 📊 Available Visualizations")
            
            # Add tabs for different visualization types
            viz_types = list(set(self._get_visualization_type(viz['description']) for viz in visualizations))
            tabs = st.tabs([f"📌 {viz_type}" for viz_type in viz_types])
            
            # Group visualizations by type
            for tab_idx, (tab, viz_type) in enumerate(zip(tabs, viz_types)):
                with tab:
                    type_vizs = [viz for viz in visualizations 
                               if self._get_visualization_type(viz['description']) == viz_type]
                    
                    for viz_idx, viz in enumerate(type_vizs):
                        # Create a unique key combining tab and visualization indices
                        unique_key = f"tab_{tab_idx}_viz_{viz_idx}"
                        
                        with st.expander(f"💡 Option {viz_idx + 1}: {viz['description']}", expanded=True):
                            # Display the SVG with proper styling
                            st.markdown(f"""
                            <div class="svg-container">
                                {viz['svg_code']}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add usage suggestions
                            st.markdown("**Suggested Uses:**")
                            st.markdown(self._get_usage_suggestions(viz['description']))
                            
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if st.button(
                                    "📎 Insert",
                                    key=f"insert_{unique_key}",
                                    help="Click to insert this visualization into your document"
                                ):
                                    self.state_manager.update_selected_visualization(viz)
                                    st.success("✨ Visualization ready!")
    
    def _get_visualization_type(self, description: str) -> str:
        """Determine the type of visualization based on its description.
        
        Args:
            description: The visualization description.
            
        Returns:
            str: The visualization type category.
        """
        description = description.lower()
        if any(word in description for word in ['chart', 'graph', 'plot']):
            return "Data Visualization"
        elif any(word in description for word in ['flow', 'process', 'step']):
            return "Process Flow"
        elif any(word in description for word in ['timeline', 'time']):
            return "Timeline"
        elif any(word in description for word in ['hierarchy', 'structure']):
            return "Hierarchy/Structure"
        else:
            return "Infographic"
    
    def _get_usage_suggestions(self, description: str) -> str:
        """Generate usage suggestions based on the visualization type.
        
        Args:
            description: The visualization description.
            
        Returns:
            str: Markdown-formatted usage suggestions.
        """
        viz_type = self._get_visualization_type(description)
        suggestions = {
            "Data Visualization": """
            - Executive summaries and reports
            - Performance reviews
            - Market analysis presentations
            - Financial reports
            """,
            "Process Flow": """
            - Standard operating procedures
            - Customer journey maps
            - Project workflows
            - Decision trees
            """,
            "Timeline": """
            - Project roadmaps
            - Strategic planning
            - Historical analysis
            - Milestone tracking
            """,
            "Hierarchy/Structure": """
            - Organizational charts
            - Product hierarchies
            - Market segmentation
            - Strategic frameworks
            """,
            "Infographic": """
            - Executive presentations
            - Marketing materials
            - Training documents
            - Client proposals
            """
        }
        return suggestions.get(viz_type, "") 