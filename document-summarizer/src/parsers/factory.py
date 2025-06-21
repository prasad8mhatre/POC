from typing import Dict, Type, Optional
from .base import BaseParser
from .pdf_parser import PDFParser
from .docx_parser import DocxParser
from .xlsx_parser import XlsxParser
from .pptx_parser import PptxParser
from .text_parser import TextParser

from src.utils.logger import setup_logger

class ParserFactory:
    """Factory class for creating document parsers."""
    
    def __init__(self):
        """Initialize the parser factory with supported file types."""
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing ParserFactory")
        
        self._parsers: Dict[str, Type[BaseParser]] = {
            'pdf': PDFParser,
            'docx': DocxParser,
            'xlsx': XlsxParser,
            'xls': XlsxParser,
            'pptx': PptxParser,
            'ppt': PptxParser,
            'txt': TextParser
        }
        
        self.logger.debug(f"Registered parsers for formats: {', '.join(self._parsers.keys())}")
    
    def get_parser(self, file_extension: str) -> Optional[BaseParser]:
        """
        Get the appropriate parser for the given file extension.
        
        Args:
            file_extension (str): File extension without the dot (e.g., 'pdf')
            
        Returns:
            BaseParser: An instance of the appropriate parser or None if not supported
            
        Raises:
            ValueError: If the file type is not supported
        """
        extension = file_extension.lower()
        
        if extension not in self._parsers:
            self.logger.warning(f"No parser available for extension: {extension}")
            return None
        
        self.logger.debug(f"Retrieved parser for extension: {extension}")
        return self._parsers[extension]()
    
    @property
    def supported_extensions(self) -> list:
        """Get a list of supported file extensions."""
        return list(self._parsers.keys()) 