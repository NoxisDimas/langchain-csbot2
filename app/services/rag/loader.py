from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PDFPlumberLoader, UnstructuredWordDocumentLoader
import pandas as pd
import os
import logging

class Loader:
    def __init__(self, file_path, title=None, category=None):
        self.file_path = file_path
        self.title = title
        self.category = category
        self.enriched_docs = []

    def txt_loader(self):
        """Load text files"""
        try:
            loader = TextLoader(self.file_path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                metadata = doc.metadata.copy()
                metadata["title"] = self.title or "Text Document"
                metadata["category"] = self.category or "txt"
                self.enriched_docs.append(Document(page_content=doc.page_content, metadata=metadata))
            logging.info(f"✅ Loaded {len(docs)} text documents from {os.path.basename(self.file_path)}")
            return self.enriched_docs
        except Exception as e:
            logging.error(f"❌ Failed to load TXT {self.file_path}: {str(e)}")
            raise ValueError(f"Failed to load TXT: {str(e)}")

    def csv_loader(self):
        """Load CSV files"""
        try:
            df = pd.read_csv(self.file_path)
            for index, row in df.iterrows():
                content = ", ".join([f"{col}: {row[col]}" for col in df.columns])
                metadata = {
                    "source": self.file_path,
                    "title": self.title or "CSV Document",
                    "category": self.category or "csv",
                    "row_index": index
                }
                self.enriched_docs.append(Document(page_content=content, metadata=metadata))
            logging.info(f"✅ Loaded {len(df)} CSV rows from {os.path.basename(self.file_path)}")
            return self.enriched_docs
        except Exception as e:
            logging.error(f"❌ Failed to load CSV {self.file_path}: {str(e)}")
            raise ValueError(f"Failed to load CSV: {str(e)}")

    def xlsx_loader(self):
        """Load Excel files"""
        try:
            df = pd.read_excel(self.file_path)
            for index, row in df.iterrows():
                content = ", ".join([f"{col}: {row[col]}" for col in df.columns])
                metadata = {
                    "source": self.file_path,
                    "title": self.title or "Excel Document",
                    "category": self.category or "xlsx",
                    "row_index": index
                }
                self.enriched_docs.append(Document(page_content=content, metadata=metadata))
            logging.info(f"✅ Loaded {len(df)} Excel rows from {os.path.basename(self.file_path)}")
            return self.enriched_docs
        except Exception as e:
            logging.error(f"❌ Failed to load Excel {self.file_path}: {str(e)}")
            raise ValueError(f"Failed to load Excel: {str(e)}")

    def md_loader(self):
        """Load Markdown files"""
        try:
            loader = TextLoader(self.file_path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                metadata = doc.metadata.copy()
                metadata["title"] = self.title or "Markdown Document"
                metadata["category"] = self.category or "md"
                self.enriched_docs.append(Document(page_content=doc.page_content, metadata=metadata))
            logging.info(f"✅ Loaded {len(docs)} markdown documents from {os.path.basename(self.file_path)}")
            return self.enriched_docs
        except Exception as e:
            logging.error(f"❌ Failed to load Markdown {self.file_path}: {str(e)}")
            raise ValueError(f"Failed to load Markdown: {str(e)}")

    def pdf_loader(self):
        """Load PDF files"""
        try:
            loader = PDFPlumberLoader(self.file_path)
            docs = loader.load()
            for doc in docs:
                metadata = doc.metadata.copy()
                metadata["title"] = self.title or "PDF Document"
                metadata["category"] = self.category or "pdf"
                self.enriched_docs.append(Document(page_content=doc.page_content, metadata=metadata))
            logging.info(f"✅ Loaded {len(docs)} PDF pages from {os.path.basename(self.file_path)}")
            return self.enriched_docs
        except Exception as e:
            logging.error(f"❌ Failed to load PDF {self.file_path}: {str(e)}")
            raise ValueError(f"Failed to load PDF: {str(e)}")

    def docx_loader(self):
        """Load Word documents"""
        try:
            loader = UnstructuredWordDocumentLoader(self.file_path)
            docs = loader.load()
            for doc in docs:
                metadata = doc.metadata.copy()
                metadata["title"] = self.title or "Word Document"
                metadata["category"] = self.category or "docx"
                self.enriched_docs.append(Document(page_content=doc.page_content, metadata=metadata))
            logging.info(f"✅ Loaded {len(docs)} Word documents from {os.path.basename(self.file_path)}")
            return self.enriched_docs
        except Exception as e:
            logging.error(f"❌ Failed to load DOCX {self.file_path}: {str(e)}")
            raise ValueError(f"Failed to load DOCX: {str(e)}")

    def auto_loader(self):
        """Automatically detect file type and load accordingly"""
        extension = os.path.splitext(self.file_path)[1].lower()

        if extension == ".txt":
            return self.txt_loader()
        elif extension == ".csv":
            return self.csv_loader()
        elif extension == ".xlsx":
            return self.xlsx_loader()
        elif extension == ".md":
            return self.md_loader()
        elif extension == ".pdf":
            return self.pdf_loader()
        elif extension == ".docx":
            return self.docx_loader()
        else:
            logging.error(f"❌ Unsupported file type: {extension}")
            raise ValueError(f"Unsupported file type: {extension}")