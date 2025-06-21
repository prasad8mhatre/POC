from typing import List, BinaryIO
from PyPDF2 import PdfReader
from .base import BaseParser

class PDFParser(BaseParser):
    """Parser for PDF documents."""
    
    def parse(self, file: BinaryIO) -> List[str]:
        """
        Parse a PDF file and return a list of text chunks.
        
        Args:
            file (BinaryIO): PDF file object
            
        Returns:
            List[str]: List of text chunks
        """
        # Create PDF reader
        reader = PdfReader(file)
        
        # Extract text from each page
        text_content = []
        for page in reader.pages:
            text = page.extract_text()
            if text.strip():  # Only add non-empty pages
                cleaned_text = self.clean_text(text)
                text_content.append(cleaned_text)
        
        # Join all pages and chunk the text
        full_text = ' '.join(text_content)
        return self.chunk_text(full_text) 