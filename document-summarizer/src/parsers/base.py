from abc import ABC, abstractmethod
from typing import List, BinaryIO

class BaseParser(ABC):
    """Base class for all document parsers."""
    
    @abstractmethod
    def parse(self, file: BinaryIO) -> List[str]:
        """
        Parse the document and return a list of text chunks.
        
        Args:
            file (BinaryIO): The file object to parse
            
        Returns:
            List[str]: List of text chunks extracted from the document
        """
        pass
    
    def clean_text(self, text: str) -> str:
        """
        Clean the extracted text by removing extra whitespace and normalizing newlines.
        
        Args:
            text (str): The text to clean
            
        Returns:
            str: The cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Normalize newlines
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks of approximately equal size.
        
        Args:
            text (str): The text to chunk
            chunk_size (int): Target size of each chunk in characters
            overlap (int): Number of characters to overlap between chunks
            
        Returns:
            List[str]: List of text chunks
        """
        if not text:
            return []
        
        # Split text into sentences (simple approach)
        sentences = text.split('.')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence = sentence.strip() + '.'
            sentence_size = len(sentence)
            
            if current_size + sentence_size > chunk_size and current_chunk:
                # Join the current chunk and add it to chunks
                chunks.append(' '.join(current_chunk))
                # Keep last few sentences for overlap
                overlap_size = 0
                overlap_chunk = []
                for s in reversed(current_chunk):
                    if overlap_size + len(s) <= overlap:
                        overlap_chunk.insert(0, s)
                        overlap_size += len(s)
                    else:
                        break
                current_chunk = overlap_chunk
                current_size = overlap_size
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks 