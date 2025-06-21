from typing import List, BinaryIO
from .base import BaseParser

class TextParser(BaseParser):
    """Parser for plain text files."""
    
    def parse(self, file: BinaryIO) -> List[str]:
        """
        Parse a text file and return a list of text chunks.
        
        Args:
            file (BinaryIO): Text file object
            
        Returns:
            List[str]: List of text chunks
        """
        # Read and decode the text file
        content = file.read().decode('utf-8', errors='ignore')
        
        # Clean and chunk the text
        cleaned_text = self.clean_text(content)
        return self.chunk_text(cleaned_text) 