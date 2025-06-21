import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import re
from collections import Counter
from datetime import datetime
import json

from src.utils.document_processor import DocumentProcessor
from src.utils.gemini import GeminiManager

# Load environment variables
load_dotenv()

def create_relevance_chart(chunks):
    """Create a bar chart showing document relevance scores."""
    df = pd.DataFrame([{
        'Document': f"{c['metadata']['filename']} (Chunk {i+1})",
        'Relevance Score': 1 - c['distance'] / max(chunk['distance'] for chunk in chunks)  # Normalize to 0-1
    } for i, c in enumerate(chunks)])
    
    fig = px.bar(
        df,
        x='Relevance Score',
        y='Document',
        orientation='h',
        title='Document Relevance Scores',
        labels={'Relevance Score': 'Relevance', 'Document': 'Document Chunk'},
        color='Relevance Score',
        color_continuous_scale='viridis'
    )
    fig.update_layout(height=min(400, 100 + len(chunks) * 50))
    return fig

def create_document_distribution_chart(chunks):
    """Create a pie chart showing distribution of source documents."""
    doc_counts = pd.DataFrame([{
        'Document': c['metadata']['filename']
    } for c in chunks]).value_counts().reset_index()
    doc_counts.columns = ['Document', 'Count']
    
    fig = px.pie(
        doc_counts,
        values='Count',
        names='Document',
        title='Source Document Distribution'
    )
    return fig

def create_chunk_network(chunks, query):
    """Create a network graph showing relationships between chunks and query."""
    nodes = [{'id': 'query', 'label': 'Query', 'group': 0}]
    edges = []
    
    for i, chunk in enumerate(chunks):
        node_id = f"chunk_{i}"
        nodes.append({
            'id': node_id,
            'label': f"{chunk['metadata']['filename']}\nChunk {i+1}",
            'group': 1
        })
        edges.append({
            'from': 'query',
            'to': node_id,
            'value': 1 - chunk['distance'] / max(c['distance'] for c in chunks)
        })
    
    # Create figure
    fig = go.Figure()
    
    # Add nodes
    node_x = [0] + [np.cos(2 * np.pi * i / len(chunks)) for i in range(len(chunks))]
    node_y = [0] + [np.sin(2 * np.pi * i / len(chunks)) for i in range(len(chunks))]
    
    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(size=20, color=['red'] + ['blue'] * len(chunks)),
        text=[n['label'] for n in nodes],
        textposition="bottom center",
        name='Nodes'
    ))
    
    # Add edges
    for i, edge in enumerate(edges):
        fig.add_trace(go.Scatter(
            x=[0, node_x[i+1]],
            y=[0, node_y[i+1]],
            mode='lines',
            line=dict(width=2 * edge['value'], color='gray'),
            name=f"Edge {i+1}"
        ))
    
    fig.update_layout(
        title='Query-Document Relationship Network',
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    return fig

def extract_numerical_data(text):
    """Extract numerical data from text for visualization."""
    # Find all numbers in the text
    numbers = re.findall(r'\d+(?:\.\d+)?', text)
    numbers = [float(n) for n in numbers]
    
    # Find words around numbers for context
    number_contexts = re.findall(r'(\w+\s+\d+(?:\.\d+)?(?:\s+\w+)?)', text)
    
    return numbers, number_contexts

def extract_key_terms(text, n=10):
    """Extract key terms and their frequencies."""
    # Remove common words and punctuation
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was', 'were'}
    words = re.findall(r'\b\w+\b', text.lower())
    words = [w for w in words if w not in common_words and len(w) > 2]
    
    # Get word frequencies
    word_freq = Counter(words)
    return dict(word_freq.most_common(n))

def create_answer_visualizations(response_text, query):
    """Create visualizations based on the answer content."""
    charts = []
    
    # Extract numerical data
    numbers, contexts = extract_numerical_data(response_text)
    if numbers:
        # Create trend line for numbers if there are any
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(numbers))),
            y=numbers,
            mode='lines+markers',
            name='Numerical Values'
        ))
        fig.update_layout(
            title='Numerical Data in Response',
            xaxis_title='Sequence',
            yaxis_title='Value'
        )
        charts.append(fig)
    
    # Create word frequency chart
    word_freq = extract_key_terms(response_text)
    if word_freq:
        fig = px.bar(
            x=list(word_freq.keys()),
            y=list(word_freq.values()),
            title='Key Terms Frequency',
            labels={'x': 'Term', 'y': 'Frequency'}
        )
        charts.append(fig)
    
    # Try to identify any temporal data (dates, times)
    dates = re.findall(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4}', response_text)
    if dates:
        # Create timeline visualization
        fig = go.Figure(data=[go.Scatter(
            x=dates,
            y=[1] * len(dates),
            mode='markers',
            marker=dict(size=10)
        )])
        fig.update_layout(
            title='Timeline of Events',
            showlegend=False
        )
        charts.append(fig)
    
    # Try to identify comparisons (using common patterns)
    comparisons = re.findall(r'(\d+(?:\.\d+)?%|\d+)\s*(?:vs\.?|versus|compared to)\s*(\d+(?:\.\d+)?%|\d+)', response_text)
    if comparisons:
        # Create comparison chart
        fig = go.Figure(data=[
            go.Bar(
                x=[f'Comparison {i+1}' for i in range(len(comparisons))],
                y=[float(re.sub(r'[%]', '', comp[0])) for comp in comparisons],
                name='First Value'
            ),
            go.Bar(
                x=[f'Comparison {i+1}' for i in range(len(comparisons))],
                y=[float(re.sub(r'[%]', '', comp[1])) for comp in comparisons],
                name='Second Value'
            )
        ])
        fig.update_layout(
            title='Comparisons Found in Response',
            barmode='group'
        )
        charts.append(fig)
    
    # If no specific data patterns found, create a relevance visualization
    if not charts:
        # Create word cloud-like visualization using plotly
        words = extract_key_terms(response_text, n=15)
        fig = go.Figure(data=[go.Scatter(
            x=list(range(len(words))),
            y=list(words.values()),
            mode='markers+text',
            text=list(words.keys()),
            textposition="top center",
            marker=dict(
                size=[v * 20 for v in words.values()],
                color=list(range(len(words))),
                colorscale='Viridis'
            )
        )])
        fig.update_layout(
            title='Key Concepts in Response',
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        charts.append(fig)
    
    return charts

def create_visualizations(structured_data: dict):
    """Create visualizations based on structured data from LLM response."""
    charts = []
    
    # Handle numerical data
    if structured_data.get('numerical_data'):
        df = pd.DataFrame(structured_data['numerical_data'])
        fig = px.bar(
            df,
            x='name',
            y='value',
            title='Numerical Values',
            labels={'name': 'Metric', 'value': 'Value'}
        )
        charts.append(fig)
    
    # Handle temporal data
    if structured_data.get('temporal_data'):
        # Convert dates to datetime
        df = pd.DataFrame(structured_data['temporal_data'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=[1] * len(df),
            mode='markers+text',
            text=df['event'],
            textposition="top center"
        ))
        fig.update_layout(
            title='Timeline of Events',
            showlegend=False,
            yaxis=dict(showticklabels=False)
        )
        charts.append(fig)
    
    # Handle categorical data
    if structured_data.get('categorical_data'):
        df = pd.DataFrame(structured_data['categorical_data'])
        fig = px.pie(
            df,
            values='value',
            names='category',
            title='Category Distribution',
            hover_data=['description']
        )
        charts.append(fig)
    
    # Handle comparisons
    if structured_data.get('comparisons'):
        for i, comp in enumerate(structured_data['comparisons']):
            fig = go.Figure(data=[
                go.Bar(
                    x=[comp['item1'], comp['item2']],
                    y=[comp['value1'], comp['value2']],
                    text=[comp['value1'], comp['value2']],
                    textposition='auto',
                )
            ])
            fig.update_layout(
                title=f"Comparison: {comp['metric']}",
                xaxis_title="Items",
                yaxis_title="Value"
            )
            charts.append(fig)
    
    # Handle key terms
    if structured_data.get('key_terms'):
        df = pd.DataFrame(structured_data['key_terms'])
        fig = px.scatter(
            df,
            x=range(len(df)),
            y='importance',
            size='importance',
            text='term',
            title='Key Terms and Their Importance',
            labels={'importance': 'Importance Score', 'term': 'Term'}
        )
        fig.update_traces(textposition='top center')
        fig.update_layout(
            xaxis=dict(showticklabels=False),
            showlegend=False
        )
        charts.append(fig)
    
    return charts

def init_session_state():
    """Initialize session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processor' not in st.session_state:
        st.session_state.processor = DocumentProcessor()
    if 'gemini' not in st.session_state:
        st.session_state.gemini = GeminiManager()
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = set()  # Track processed files

def process_uploaded_file(file):
    """Process an uploaded file and add it to the index."""
    try:
        # Get file extension
        file_extension = Path(file.name).suffix[1:]  # Remove the dot
        
        # Process the document
        metadata = st.session_state.processor.process_document(
            file,
            file.name,
            file_extension
        )
        
        # Add to indexed documents list
        st.session_state.processor.indexed_documents.append(metadata)
        
        return True, f"Successfully processed {file.name}"
    except Exception as e:
        return False, f"Error processing {file.name}: {str(e)}"

def create_document_stats():
    """Create statistics about indexed documents."""
    if not st.session_state.processor.indexed_documents:
        return None
    
    # Create DataFrame from indexed documents
    df = pd.DataFrame(st.session_state.processor.indexed_documents)
    
    # Group by extension
    ext_counts = df.groupby('extension')['chunk_count'].agg(['count', 'sum'])
    ext_counts.columns = ['Number of Files', 'Total Chunks']
    
    return ext_counts

def main():
    st.set_page_config(
        page_title="Document Summarizer",
        page_icon="📚",
        layout="wide"
    )
    
    init_session_state()
    
    st.title("Document Summarizer")
    
    # Create tabs
    upload_tab, documents_tab, chat_tab = st.tabs([
        "Upload Documents", 
        "Indexed Documents", 
        "Chat Interface"
    ])
    
    # Upload Documents Tab
    with upload_tab:
        st.header("Upload Your Documents")
        
        # Show supported formats
        st.info(f"Supported formats: {', '.join(st.session_state.processor.supported_formats)}")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=st.session_state.processor.supported_formats,
            accept_multiple_files=True
        )
        
        if uploaded_files:
            with st.spinner("Processing documents..."):
                for file in uploaded_files:
                    # Check if file has already been processed
                    if file.name not in st.session_state.processed_files:
                        try:
                            # Get file extension
                            file_extension = Path(file.name).suffix[1:]  # Remove the dot
                            
                            # Process the document
                            metadata = st.session_state.processor.process_document(
                                file,
                                file.name,
                                file_extension
                            )
                            
                            # Add to processed files set
                            st.session_state.processed_files.add(file.name)
                            st.success(f"Successfully processed {file.name}")
                        except Exception as e:
                            st.error(f"Error processing {file.name}: {str(e)}")
                    else:
                        st.info(f"Skipped {file.name} (already processed)")
        
        # Add option to clear processed files
        if st.session_state.processed_files:
            if st.button("Clear Processed Files List"):
                st.session_state.processed_files.clear()
                st.success("Cleared processed files list. You can now reprocess previously uploaded files.")
                st.rerun()
    
    # Indexed Documents Tab
    with documents_tab:
        st.header("Indexed Documents")
        
        indexed_docs = st.session_state.processor.indexed_documents
        
        # Debug info about indexed_docs
        #st.write("Debug: Type of indexed_docs:", type(indexed_docs))
        #st.write("Debug: Content of indexed_docs:", indexed_docs)
        
        if not indexed_docs or not isinstance(indexed_docs, list):
            st.info("No documents have been indexed yet.")
            # Initialize empty list if needed
            if not isinstance(indexed_docs, list):
                st.session_state.processor.indexed_documents = []
        else:
            try:
                # Show statistics
                st.subheader("Document Statistics")
                
                # Validate document structure
                valid_docs = []
                for doc in indexed_docs:
                    if isinstance(doc, dict) and all(key in doc for key in ['extension', 'filename', 'chunk_count']):
                        valid_docs.append(doc)
                    else:
                        st.warning(f"Skipping invalid document structure: {doc}")
                
                if not valid_docs:
                    st.warning("No valid documents found in the index.")
                    return
                
                # Create DataFrame with proper column names
                df = pd.DataFrame([{
                    'Extension': str(doc.get('extension', '')).lower(),
                    'Filename': str(doc.get('filename', '')),
                    'Chunks': int(doc.get('chunk_count', 0))
                } for doc in valid_docs])
                
                # Debug info
                #st.write("Debug: Number of valid documents:", len(valid_docs))
                #st.write("Debug: DataFrame shape:", df.shape)
                #st.write("Debug: DataFrame columns:", df.columns.tolist())
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Show total documents by type
                    extension_counts = df['Extension'].value_counts().reset_index()
                    extension_counts.columns = ['Extension', 'Count']
                    fig = px.pie(
                        extension_counts,
                        values='Count',
                        names='Extension',
                        title='Documents by Type'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Show chunks by document type
                    chunks_by_type = df.groupby('Extension')['Chunks'].sum().reset_index()
                    chunks_by_type.columns = ['Extension', 'Total Chunks']
                    fig = px.bar(
                        chunks_by_type,
                        x='Extension',
                        y='Total Chunks',
                        title='Total Chunks by Document Type'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Show document list with delete option
                st.subheader("Indexed Documents")
                
                # Create columns for the table header
                cols = st.columns([3, 2, 2, 1])
                cols[0].write("**Filename**")
                cols[1].write("**Extension**")
                cols[2].write("**Chunks**")
                cols[3].write("**Action**")
                
                # Add a separator line
                st.markdown("---")
                
                # Show each document in a row
                for idx, doc in enumerate(valid_docs):
                    cols = st.columns([3, 2, 2, 1])
                    
                    # File information
                    cols[0].write(doc['filename'])
                    cols[1].write(doc['extension'])
                    cols[2].write(str(doc['chunk_count']))
                    
                    # Delete button
                    if cols[3].button("🗑️", key=f"delete_{idx}_{doc['filename']}", help="Delete document"):
                        if st.session_state.processor.remove_document(doc['filename']):
                            st.success(f"Removed {doc['filename']}")
                            st.rerun()
                
                # Show detailed information in expandable sections below the table
                st.subheader("Document Details")
                for doc in valid_docs:
                    with st.expander(f"Details for {doc['filename']}"):
                        st.json(doc)
            except Exception as e:
                st.error(f"Error processing documents: {str(e)}")
                st.write("Debug: Error details:", e)
    
    # Chat Interface Tab
    with chat_tab:
        # Custom CSS for chat interface
        st.markdown("""
        <style>
        /* Main container */
        .main-chat-container {
            display: flex;
            flex-direction: column;
            height: calc(100vh - 180px);  /* Account for tabs and header */
            position: relative;
            padding: 0;
            overflow: hidden;
            background-color: #ffffff;
            margin-top: -1rem;
        }
        
        /* Header section */
        .header-section {
            text-align: center;
            padding: 1rem;
            background: linear-gradient(to right, #f8f9fa, #ffffff);
            border-bottom: 1px solid #eaecef;
        }
        
        /* Keep Streamlit tabs visible */
        .stTabs {
            background-color: #ffffff;
            padding-top: 1rem;
        }
        
        /* Style the tab buttons */
        .stTabs button {
            border-radius: 4px;
            font-weight: 500;
        }
        
        /* Style active tab */
        .stTabs button[aria-selected="true"] {
            border-radius: 4px;
            background-color: #f0f2f5;
        }
        
        /* Hide only specific Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Show header but style it */
        header {
            background-color: transparent !important;
            padding-top: 0.5rem;
        }
        
        /* Rest of your existing styles */
        .app-title {
            font-size: 2rem;
            font-weight: bold;
            color: #1a1a1a;
            margin-bottom: 0.5rem;
        }
        
        .app-subtitle {
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 1.5rem;
        }
        
        .topic-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: center;
            margin-bottom: 1rem;
            padding: 0 1rem;
        }
        
        .topic-chip {
            background-color: #f8f9fa;
            border: 1px solid #eaecef;
            border-radius: 20px;
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
            color: #666;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .topic-chip:hover {
            background-color: #e9ecef;
            color: #1a1a1a;
        }
        
        .chat-history {
            flex-grow: 1;
            overflow-y: auto;
            padding: 1rem;
            margin-bottom: 80px;
        }
        
        .chat-container {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            max-width: 80%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .user-message {
            background-color: #f8f9fa;
            margin-left: auto;
            border: 1px solid #eaecef;
        }
        
        .assistant-message {
            background-color: #ffffff;
            margin-right: auto;
            border: 1px solid #eaecef;
        }
        
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #ffffff;
            padding: 1rem;
            border-top: 1px solid #eaecef;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
            z-index: 1000;
        }
        
        .source-container, .visualization-container {
            background-color: #ffffff;
            border: 1px solid #eaecef;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 0.5rem;
        }
        
        .chat-header {
            color: #666;
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        /* Adjust Streamlit's default padding */
        .stApp {
            margin: 0;
        }
        
        .element-container {
            padding: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create main container
        st.markdown('<div class="">', unsafe_allow_html=True)
        
        # Header section with smaller padding
        st.markdown("""
        <div class="header-section">
            <div class="app-title">Document Summarizer</div>
            <div class="app-subtitle">Ask questions about your documents and get instant insights</div>
            
        </div>
        """, unsafe_allow_html=True)
        
        # Chat history container
        st.markdown('<div class="chat-history">', unsafe_allow_html=True)
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-container user-message">
                    <div class="chat-header">You</div>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                try:
                    # Handle JSON string response
                    if isinstance(message["content"], str) and message["content"].startswith('```json'):
                        json_str = message["content"].split('```json')[1].split('```')[0].strip()
                        response_data = json.loads(json_str)
                        response_text = response_data.get("text", message["content"])
                    elif isinstance(message["content"], dict):
                        response_text = message["content"].get("text", str(message["content"]))
                    else:
                        response_text = message["content"]
                except Exception as e:
                    response_text = message["content"]
                
                st.markdown(f"""
                <div class="chat-container assistant-message">
                    <div class="chat-header">AI Assistant</div>
                    {response_text}
                </div>
                """, unsafe_allow_html=True)
                
                # Show source documents in a collapsible section if available
                if message.get("chunks"):
                    with st.expander("📚 Source Documents"):
                        for chunk in message["chunks"]:
                            st.markdown(f"""
                            <div class="source-container">
                                <strong>Document:</strong> {chunk['metadata']['filename']}<br/>
                                <strong>Relevant Text:</strong><br/>
                                {chunk['text']}
                            </div>
                            """, unsafe_allow_html=True)
                
                # Show visualizations if available
                try:
                    structured_data = None
                    if isinstance(message["content"], str) and message["content"].startswith('```json'):
                        json_str = message["content"].split('```json')[1].split('```')[0].strip()
                        response_data = json.loads(json_str)
                        structured_data = response_data.get("structured_data")
                    elif isinstance(message["content"], dict):
                        structured_data = message["content"].get("structured_data")
                    
                    if structured_data:
                        with st.expander("📊 Insights & Visualizations"):
                            # Display key points if available
                            if "key_points" in structured_data:
                                st.markdown("### 🎯 Key Points")
                                for point in structured_data["key_points"]:
                                    st.markdown(f"• {point}")
                                st.markdown("---")
                            
                            # Display statistics if available
                            if "statistics" in structured_data:
                                st.markdown("### 📊 Statistics")
                                # Convert statistics to a format suitable for visualization
                                stats_data = []
                                for key, value in structured_data["statistics"].items():
                                    # Try to extract numerical values
                                    try:
                                        # Extract number from string (e.g., "4000 INR" -> 4000)
                                        num_value = float(''.join(filter(str.isdigit, str(value))))
                                        stats_data.append({"Metric": key, "Value": num_value})
                                    except:
                                        # If we can't extract a number, just display as text
                                        st.markdown(f"**{key}:** {value}")
                                
                                if stats_data:
                                    # Create a bar chart for numerical statistics
                                    df = pd.DataFrame(stats_data)
                                    fig = px.bar(
                                        df,
                                        x='Metric',
                                        y='Value',
                                        title='Numerical Statistics',
                                        labels={'Value': 'Amount', 'Metric': ''},
                                        text='Value'
                                    )
                                    fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                                    fig.update_layout(
                                        showlegend=False,
                                        xaxis_tickangle=-45,
                                        height=400
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                                st.markdown("---")
                            
                            # Display categories if available
                            if "categories" in structured_data:
                                st.markdown("### 🏷️ Categories")
                                # Create a pie chart for categories
                                categories = structured_data["categories"]
                                category_counts = {cat: 1 for cat in categories}  # Simple count for now
                                df = pd.DataFrame([{"Category": k, "Count": v} for k, v in category_counts.items()])
                                fig = px.pie(
                                    df,
                                    values='Count',
                                    names='Category',
                                    title='Document Categories',
                                    hole=0.4
                                )
                                fig.update_traces(textposition='outside', textinfo='label+percent')
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # Display sentiment if available
                            if "sentiment" in structured_data:
                                st.markdown("### 😊 Sentiment Analysis")
                                sentiment = structured_data["sentiment"]
                                sentiment_color = {
                                    "positive": "🟢 Positive",
                                    "negative": "🔴 Negative",
                                    "neutral": "⚪ Neutral"
                                }.get(sentiment.lower(), sentiment)
                                st.markdown(f"**Overall Sentiment:** {sentiment_color}")
                except Exception as e:
                    st.error(f"Error displaying visualizations: {str(e)}")
                    pass
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close chat-history
        
        # Input container at the bottom
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        if user_input := st.chat_input("Ask a question about your documents...", key="chat_input"):
            # Add user message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Generate response
            if not st.session_state.processor.indexed_documents:
                st.warning("Please upload some documents first.")
            else:
                with st.spinner("Searching documents and generating response..."):
                    relevant_chunks = st.session_state.processor.search_documents(user_input)
                    response = st.session_state.gemini.generate_response(
                        user_input,
                        relevant_chunks,
                        st.session_state.chat_history[:-1]
                    )
                    
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response,
                        "chunks": relevant_chunks
                    })
                    
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)  # Close input-container
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close main-chat-container

if __name__ == "__main__":
    main() 