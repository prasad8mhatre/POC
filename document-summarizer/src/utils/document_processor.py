import os
import json
from typing import BinaryIO, Dict, List, Any, Tuple
from ..parsers.factory import ParserFactory
from ..embeddings.manager import EmbeddingManager
from ..indexing.faiss_manager import FAISSManager
from src.utils.logger import setup_logger

class DocumentProcessor:
    """Handles the complete document processing pipeline."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the document processor.
        
        Args:
            data_dir (str): Directory to store all data (index, metadata, etc.)
        """
        self.data_dir = data_dir
        self.index_dir = os.path.join(data_dir, "index")
        self.metadata_file = os.path.join(data_dir, "metadata.json")
        
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing DocumentProcessor")
        
        self.parser_factory = ParserFactory()
        self.embedding_manager = EmbeddingManager()
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize FAISS index
        self.faiss_manager = FAISSManager(self.embedding_manager.embedding_dim)
        
        # Load existing index and metadata if available
        self.indexed_documents = []
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing index and document map if they exist."""
        try:
            index_path = "data/index/faiss.index"
            if os.path.exists(index_path):
                self.logger.info("Loading existing FAISS index")
                self.faiss_manager.load_index(index_path)
            
            metadata_path = "data/index/document_map.json"
            if os.path.exists(metadata_path):
                self.logger.info("Loading existing document map")
                with open(metadata_path, "r") as f:
                    self.indexed_documents = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading existing data: {str(e)}")
    
    def _save_data(self):
        """Save index and document map."""
        try:
            # Create directories if they don't exist
            os.makedirs("data/index", exist_ok=True)
            
            # Save FAISS index
            index_path = "data/index/faiss.index"
            self.logger.info(f"Saving FAISS index to {index_path}")
            self.faiss_manager.save_index(index_path)
            
            # Save document metadata
            metadata_path = "data/index/document_map.json"
            self.logger.info(f"Saving document map to {metadata_path}")
            with open(metadata_path, "w") as f:
                json.dump(self.indexed_documents, f)
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
    
    def process_document(self, file_obj: Any, filename: str, extension: str) -> Dict:
        """
        Process a document: parse, chunk, embed, and index.
        
        Args:
            file_obj: File object to process
            filename: Name of the file
            extension: File extension
            
        Returns:
            dict: Document metadata
        """
        try:
            self.logger.info(f"Processing document: {filename}")
            
            # Get appropriate parser
            parser = self.parser_factory.get_parser(extension)
            if not parser:
                raise ValueError(f"No parser available for extension: {extension}")
            
            # Parse and chunk document
            self.logger.debug(f"Parsing document: {filename}")
            chunks = parser.parse(file_obj)
            
            # Create document metadata
            metadata = {
                "filename": filename,
                "extension": extension,
                "chunk_count": len(chunks)
            }
            
            # Generate embeddings and index chunks
            self.logger.debug(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = self.embedding_manager.generate_embeddings(chunks)
            
            self.logger.debug("Adding embeddings to FAISS index")
            self.faiss_manager.add_embeddings(embeddings, chunks, metadata)
            
            # Add to indexed documents list
            self.indexed_documents.append(metadata)
            
            # Save updated data
            self._save_data()
            
            self.logger.info(f"Successfully processed document: {filename}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error processing document {filename}: {str(e)}")
            raise
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for relevant document chunks.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            list: List of relevant chunks with metadata
        """
        try:
            self.logger.info(f"Searching documents for query: {query}")
            
            # Generate query embedding
            self.logger.debug("Generating query embedding")
            query_embeddings = self.embedding_manager.generate_embeddings(query)
            # Since we're searching with a single query, get the first embedding
            query_embedding = query_embeddings[0] if isinstance(query_embeddings, list) else query_embeddings
            
            # Search index
            self.logger.debug(f"Searching FAISS index for top {k} results")
            results = self.faiss_manager.search(query_embedding, k)
            
            self.logger.info(f"Found {len(results)} relevant chunks")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching documents: {str(e)}")
            raise
    
    def remove_document(self, filename: str) -> bool:
        """
        Remove a document from the index.
        
        Args:
            filename (str): Name of the file to remove
            
        Returns:
            bool: True if document was removed, False otherwise
        """
        try:
            self.logger.info(f"Removing document: {filename}")
            
            # Remove from indexed documents list
            self.indexed_documents = [
                doc for doc in self.indexed_documents 
                if doc['filename'] != filename
            ]
            
            # Note: We can't easily remove specific documents from FAISS index
            # So we'll rebuild the index if needed in a future update
            
            # Save updated metadata
            self._save_data()
            
            self.logger.info(f"Successfully removed document: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing document {filename}: {str(e)}")
            return False
    
    @property
    def supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return self.parser_factory.supported_extensions 