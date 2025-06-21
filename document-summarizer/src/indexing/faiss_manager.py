import faiss
import numpy as np
from typing import List, Dict, Any
import pickle
from pathlib import Path

from src.utils.logger import setup_logger

class FAISSManager:
    """Manages FAISS index for document embeddings."""
    
    def __init__(self, dimension: int = 768):
        """
        Initialize FAISS index manager.
        
        Args:
            dimension (int): Dimension of embeddings (default: 768 for sentence-transformers)
        """
        self.logger = setup_logger(__name__)
        self.logger.info(f"Initializing FAISS index with dimension {dimension}")
        
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.chunks = []
        self.metadata = []
    
    def add_embeddings(self, embeddings: List[List[float]], chunks: List[str], metadata: Dict[str, Any]):
        """
        Add embeddings to the index.
        
        Args:
            embeddings: List of embedding vectors
            chunks: List of text chunks
            metadata: Document metadata
        """
        try:
            self.logger.info(f"Adding {len(embeddings)} embeddings to index")
            
            # Convert embeddings to numpy array
            embeddings_array = np.array(embeddings).astype('float32')
            
            # Add to FAISS index
            self.index.add(embeddings_array)
            
            # Store chunks and metadata
            chunk_metadata = [metadata for _ in chunks]
            self.chunks.extend(chunks)
            self.metadata.extend(chunk_metadata)
            
            self.logger.debug(f"Index now contains {len(self.chunks)} total chunks")
            
        except Exception as e:
            self.logger.error(f"Error adding embeddings to index: {str(e)}")
            raise
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """
        Search for similar vectors in the index.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            list: List of dictionaries containing chunks and metadata
        """
        try:
            self.logger.info(f"Searching index for top {k} results")
            
            # Convert query to numpy array and ensure it's 2D
            query_array = np.array(query_embedding, dtype='float32')
            if len(query_array.shape) == 1:
                query_array = query_array.reshape(1, -1)
            
            # Search index
            self.logger.debug(f"Searching with query shape: {query_array.shape}")
            distances, indices = self.index.search(query_array, k)
            
            # Prepare results
            results = []
            for idx in indices[0]:  # indices[0] since we only have one query
                if idx < len(self.chunks):  # Ensure index is valid
                    results.append({
                        'text': self.chunks[idx],
                        'metadata': self.metadata[idx]
                    })
            
            self.logger.debug(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching index: {str(e)}")
            raise
    
    def save_index(self, filepath: str):
        """
        Save the index and associated data to disk.
        
        Args:
            filepath: Path to save the index
        """
        try:
            self.logger.info(f"Saving index to {filepath}")
            
            # Create directory if it doesn't exist
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, filepath)
            
            # Save chunks and metadata to a separate pickle file
            pickle_path = str(Path(filepath).parent / 'chunks_metadata.pkl')
            with open(pickle_path, 'wb') as f:
                pickle.dump({
                    'chunks': self.chunks,
                    'metadata': self.metadata
                }, f)
            
            self.logger.debug("Successfully saved index and associated data")
            
        except Exception as e:
            self.logger.error(f"Error saving index: {str(e)}")
            raise
    
    def load_index(self, filepath: str):
        """
        Load the index and associated data from disk.
        
        Args:
            filepath: Path to load the index from
        """
        try:
            self.logger.info(f"Loading index from {filepath}")
            
            # Load FAISS index
            self.index = faiss.read_index(filepath)
            
            # Load chunks and metadata from the separate pickle file
            pickle_path = str(Path(filepath).parent / 'chunks_metadata.pkl')
            with open(pickle_path, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.metadata = data['metadata']
            
            self.logger.debug(f"Successfully loaded index with {len(self.chunks)} chunks")
            
        except Exception as e:
            self.logger.error(f"Error loading index: {str(e)}")
            raise 