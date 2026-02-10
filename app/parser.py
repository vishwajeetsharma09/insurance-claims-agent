"""
Document parser for PDF and TXT files.
"""
import logging
from typing import Union
from pathlib import Path
import pdfplumber

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parser for extracting text from PDF and TXT documents."""
    
    @staticmethod
    def parse(file_path: Union[str, Path]) -> str:
        """
        Parse a document and extract text content.
        
        Args:
            file_path: Path to the document file (PDF or TXT)
            
        Returns:
            Extracted text content as string
            
        Raises:
            ValueError: If file extension is not supported
            FileNotFoundError: If file does not exist
            Exception: For parsing errors
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return DocumentParser._parse_pdf(file_path)
        elif extension == '.txt':
            return DocumentParser._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}. Supported types: .pdf, .txt")
    
    @staticmethod
    def _parse_pdf(file_path: Path) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text_content = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            full_text = "\n".join(text_content)
            logger.info(f"Successfully parsed PDF: {file_path}, extracted {len(full_text)} characters")
            return full_text
            
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {str(e)}")
            raise Exception(f"Failed to parse PDF: {str(e)}")
    
    @staticmethod
    def _parse_txt(file_path: Path) -> str:
        """
        Extract text from TXT file.
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Extracted text content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Successfully parsed TXT: {file_path}, extracted {len(content)} characters")
            return content
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                logger.info(f"Successfully parsed TXT with latin-1 encoding: {file_path}")
                return content
            except Exception as e:
                logger.error(f"Error parsing TXT {file_path}: {str(e)}")
                raise Exception(f"Failed to parse TXT: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing TXT {file_path}: {str(e)}")
            raise Exception(f"Failed to parse TXT: {str(e)}")

