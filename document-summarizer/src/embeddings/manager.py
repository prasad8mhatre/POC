from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

from src.utils.logger import setup_logger

class EmbeddingManager:
    """Manages text embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the embedding manager.
        
        Args:
            model_name (str): Name of the sentence-transformers model to use
        """
        self.logger = setup_logger(__name__)
        self.logger.info(f"Initializing EmbeddingManager with model: {model_name}")
        
        try:
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.logger.debug(f"Model loaded successfully. Embedding dimension: {self.dimension}")
            
        except Exception as e:
            self.logger.error(f"Error loading model {model_name}: {str(e)}")
            raise
    
    def generate_embeddings(
        self, 
        texts: Union[str, List[str]]
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text string or list of text strings
            
        Returns:
            Embeddings as numpy arrays
        """
        try:
            self.logger.info("Generating embeddings")
            
            # Handle single text input
            if isinstance(texts, str):
                texts = [texts]
                self.logger.debug("Converting single text to list")
            
            # Generate embeddings
            self.logger.debug(f"Processing {len(texts)} texts")
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            
            # Convert to list format
            if len(embeddings.shape) == 1:
                embeddings = [embeddings.tolist()]
            else:
                embeddings = embeddings.tolist()
            
            self.logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    @property
    def embedding_dim(self) -> int:
        """Get the dimension of the embeddings."""
        return self.model.get_sentence_embedding_dimension() 