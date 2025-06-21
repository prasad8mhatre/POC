from typing import List, BinaryIO
import pandas as pd
from io import BytesIO
from .base import BaseParser

class XlsxParser(BaseParser):
    """Parser for Microsoft Excel spreadsheets."""
    
    def parse(self, file: BinaryIO) -> List[str]:
        """
        Parse an Excel file and return a list of text chunks.
        
        Args:
            file (BinaryIO): Excel file object
            
        Returns:
            List[str]: List of text chunks
        """
        # Read all sheets from the Excel file
        excel_file = pd.ExcelFile(BytesIO(file.read()))
        text_content = []
        
        for sheet_name in excel_file.sheet_names:
            # Read the sheet into a DataFrame
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Convert column names to string and clean them
            df.columns = df.columns.astype(str)
            
            # Add sheet name and column headers
            text_content.append(f"Sheet: {sheet_name}")
            text_content.append(f"Columns: {' | '.join(df.columns)}")
            
            # Convert DataFrame to string representation
            for _, row in df.iterrows():
                # Convert all values to string and clean them
                row_values = [str(val).strip() for val in row.values]
                # Only add non-empty rows
                if any(val for val in row_values):
                    text_content.append(' | '.join(row_values))
            
            # Add separator between sheets
            text_content.append('-' * 50)
        
        # Join all content and chunk the text
        full_text = '\n'.join(text_content)
        return self.chunk_text(self.clean_text(full_text)) 