"""Document editor component for the application."""
import streamlit as st
from src.config.settings import EDITOR_HEIGHT
from src.utils.state_manager import StateManager

class DocumentEditor:
    """Component for handling document editing functionality."""
    
    def __init__(self, state_manager: StateManager):
        """Initialize the document editor.
        
        Args:
            state_manager: Instance of StateManager for state management.
        """
        self.state_manager = state_manager
    
    def render(self):
        """Render the document editor component."""
        st.subheader("📝 Business Story Editor")
        
        # Help text
        st.markdown("""
        Write your business narrative here. Some suggestions:
        - Business processes and workflows
        - Key performance indicators (KPIs)
        - Market analysis and trends
        - Project timelines and milestones
        - Organizational structures
        - Strategic initiatives
        """)
        
        # Custom button styling
        st.markdown("""
        <style>
        .stTextArea textarea {
            font-size: 16px !important;
            line-height: 1.5 !important;
            padding: 1rem !important;
            border-radius: 8px !important;
            border: 1px solid #ccc !important;
            background-color: white !important;
        }
        .stTextArea textarea:focus {
            box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.2) !important;
            border-color: #1E88E5 !important;
        }
        .generate-button {
            margin-top: 1rem;
        }
        div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
            margin-top: 1rem;
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Main document editor
        new_content = st.text_area(
            "Start writing your business story...",
            value=self.state_manager.get_document_content(),
            height=EDITOR_HEIGHT,
            key="editor",
            help="Write or paste your business content here. Select specific text or use entire content for visualization."
        )
        
        # Add the generate button below the textarea
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎨 Generate Visualization", 
                        type="primary",
                        use_container_width=True,
                        help="Click to generate visualizations for selected text or entire content"):
                selected_text = st.session_state.get('selected_text', '')
                # If no text is selected, use the entire content
                if not selected_text and new_content.strip():
                    selected_text = new_content
                if selected_text:
                    st.session_state.selected_text = selected_text
                    st.session_state.trigger_generation = True
        
        if new_content != self.state_manager.get_document_content():
            self.state_manager.update_document_content(new_content)
        
        # Add JavaScript for handling text selection
        st.markdown("""
        <script>
        function handleTextSelection() {
            const selection = window.getSelection().toString().trim();
            if (selection) {
                // Send selected text to Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: selection
                }, '*');
            }
        }

        // Add selection event listeners
        document.addEventListener('mouseup', handleTextSelection);
        document.addEventListener('keyup', handleTextSelection);
        </script>
        """, unsafe_allow_html=True)
        
        # Get selected text from session state
        selected_text = st.session_state.get('selected_text', '')
        
        return selected_text 