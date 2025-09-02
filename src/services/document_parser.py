"""
Document Parser Service with Watermark Protection
Copyright (c) 2024 Balenci Cash - All Rights Reserved
This module handles parsing of various document formats.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import hashlib

from pypdf import PdfReader
from docx import Document as DocxDocument
import markdown

from src.utils.logger import logger
from src.utils.watermark import protect, protect_class, watermark
from config.settings import settings


class BaseParser(ABC):
    """Base parser with watermark protection."""
    
    def __init__(self):
        self.author = "Balenci Cash"
        self.parser_signature = hashlib.md5(f"{self.author}_parser".encode()).hexdigest()
    
    @abstractmethod
    def parse(self, file_path: Path) -> str:
        """Parse document and extract text."""
        pass
    
    def _add_watermark_to_content(self, content: str) -> str:
        """Add invisible watermark to parsed content."""
        watermark_tag = f"\n<!-- Parsed by: {self.author} | Sig: {self.parser_signature[:8]} -->\n"
        return content + watermark_tag


@protect_class
class PDFParser(BaseParser):
    """PDF document parser with watermark protection."""
    
    @protect
    def parse(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            logger.info(f"Parsing PDF: {file_path}")
            reader = PdfReader(file_path)
            text_content = []
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(f"[Page {page_num}]\n{page_text}")
            
            full_content = "\n\n".join(text_content)
            return self._add_watermark_to_content(full_content)
            
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            raise


@protect_class
class WordParser(BaseParser):
    """Word document parser with watermark protection."""
    
    @protect
    def parse(self, file_path: Path) -> str:
        """Extract text from Word document."""
        try:
            logger.info(f"Parsing Word document: {file_path}")
            doc = DocxDocument(file_path)
            paragraphs = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
            
            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            paragraphs.append(cell.text)
            
            full_content = "\n\n".join(paragraphs)
            return self._add_watermark_to_content(full_content)
            
        except Exception as e:
            logger.error(f"Error parsing Word document {file_path}: {e}")
            raise


@protect_class
class MarkdownParser(BaseParser):
    """Markdown document parser with watermark protection."""
    
    @protect
    def parse(self, file_path: Path) -> str:
        """Extract and convert markdown to plain text."""
        try:
            logger.info(f"Parsing Markdown: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert markdown to HTML then extract text
            html = markdown.markdown(md_content)
            # Simple HTML tag removal (for plain text extraction)
            import re
            text = re.sub('<[^<]+?>', '', html)
            
            return self._add_watermark_to_content(text)
            
        except Exception as e:
            logger.error(f"Error parsing Markdown {file_path}: {e}")
            raise


@protect_class
class TextParser(BaseParser):
    """Plain text parser with watermark protection."""
    
    @protect
    def parse(self, file_path: Path) -> str:
        """Read plain text file."""
        try:
            logger.info(f"Parsing text file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self._add_watermark_to_content(content)
            
        except Exception as e:
            logger.error(f"Error parsing text file {file_path}: {e}")
            raise


@protect_class
class DocumentParserService:
    """
    Main document parser service with watermark protection.
    Copyright (c) 2024 Balenci Cash
    """
    
    def __init__(self):
        self.parsers = {
            '.pdf': PDFParser(),
            '.docx': WordParser(),
            '.md': MarkdownParser(),
            '.txt': TextParser()
        }
        self.author = "Balenci Cash"
        self.service_id = "BC-PARSER-2024"
        logger.info(f"Document Parser Service initialized - Author: {self.author}")
    
    @protect
    def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parse document and return extracted content with metadata.
        Includes watermark in the result.
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = path.suffix.lower()
        if extension not in self.parsers:
            raise ValueError(f"Unsupported file type: {extension}")
        
        # Parse document
        parser = self.parsers[extension]
        content = parser.parse(path)
        
        # Calculate content hash for integrity
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Prepare result with watermark
        result = {
            "file_name": path.name,
            "file_path": str(path),
            "file_type": extension,
            "content": content,
            "content_hash": content_hash,
            "char_count": len(content),
            "metadata": {
                "parser_service": self.service_id,
                "author": self.author,
                "watermark": watermark._signature_hash[:16],
                "protected": True
            }
        }
        
        logger.success(f"Successfully parsed {path.name} - Hash: {content_hash[:8]}")
        return result
    
    @protect
    def validate_file(self, file_path: str) -> bool:
        """Validate if file is supported and within size limits."""
        path = Path(file_path)
        
        if not path.exists():
            return False
        
        if path.suffix.lower() not in self.parsers:
            return False
        
        file_size = path.stat().st_size
        if file_size > settings.MAX_FILE_SIZE:
            logger.warning(f"File {path.name} exceeds size limit: {file_size} bytes")
            return False
        
        return True


# Create singleton instance
document_parser_service = DocumentParserService()