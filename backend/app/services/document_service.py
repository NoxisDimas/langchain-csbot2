import os
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiofiles
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangChainDocument
import pypdf
from docx import Document as DocxDocument
import markdown
import uuid
from datetime import datetime

from app.services.database_service import DatabaseService

class DocumentService:
    def __init__(self):
        try:
            self.db_service = DatabaseService()
        except Exception:
            self.db_service = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    def get_file_extension(self, filename: str) -> str:
        return Path(filename).suffix.lower()
    
    def is_supported_file(self, filename: str) -> bool:
        supported_extensions = {
            '.pdf', '.txt', '.md', '.csv', '.xlsx', '.xls', 
            '.docx', '.doc', '.json', '.xml', '.html'
        }
        return self.get_file_extension(filename) in supported_extensions
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        safe_name = os.path.basename(filename).replace("..", "").replace("/", "_").replace("\\", "_")
        if not safe_name:
            safe_name = f"upload_{uuid.uuid4().hex}"
        file_path = self.upload_dir / safe_name
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        return str(file_path)

    def process_file_to_chunks(self, file_content: bytes, filename: str, knowledge_base_name: str = "default") -> List[LangChainDocument]:
        file_path = None
        try:
            file_path = self.upload_dir / os.path.basename(filename).replace("..", "").replace("/", "_").replace("\\", "_")
            with open(file_path, 'wb') as f:
                f.write(file_content)
        except Exception:
            pass

        file_type = self.get_file_extension(filename)
        text_content = self.extract_text_from_file(str(file_path) if file_path else filename, file_type)
        if not text_content.strip():
            return []
        chunks = self.chunk_text(text_content, {
            "filename": filename,
            "knowledge_base": knowledge_base_name,
        })
        for idx, c in enumerate(chunks):
            c.metadata = {**(c.metadata or {}), "chunk_index": idx}
        return chunks
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        try:
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""
    
    def extract_text_from_csv(self, file_path: str) -> str:
        try:
            df = pd.read_csv(file_path)
            return df.to_string()
        except Exception as e:
            print(f"Error extracting text from CSV: {e}")
            return ""
    
    def extract_text_from_excel(self, file_path: str) -> str:
        try:
            df = pd.read_excel(file_path)
            return df.to_string()
        except Exception as e:
            print(f"Error extracting text from Excel: {e}")
            return ""
    
    def extract_text_from_markdown(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
                html = markdown.markdown(md_content)
                import re
                text = re.sub(r'<[^>]+>', '', html)
                return text
        except Exception as e:
            print(f"Error extracting text from Markdown: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error extracting text from TXT: {e}")
            return ""
    
    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        file_type = file_type.lower()
        if file_type == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type == '.docx':
            return self.extract_text_from_docx(file_path)
        elif file_type == '.csv':
            return self.extract_text_from_csv(file_path)
        elif file_type in ['.xlsx', '.xls']:
            return self.extract_text_from_excel(file_path)
        elif file_type == '.md':
            return self.extract_text_from_markdown(file_path)
        elif file_type == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            return self.extract_text_from_txt(file_path)
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[LangChainDocument]:
        if not text.strip():
            return []
        docs = [LangChainDocument(page_content=text, metadata=metadata or {})]
        chunks = self.text_splitter.split_documents(docs)
        return chunks

    async def process_file(self, file_content: bytes, filename: str, knowledge_base_name: str = "default") -> Optional[None]:
        try:
            return None
        except Exception as e:
            print(f"Error processing file: {e}")
            return None