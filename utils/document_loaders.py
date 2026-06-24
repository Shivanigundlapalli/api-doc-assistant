import os
import json
import yaml
from pathlib import Path
from langchain_community.document_loaders import (
    PyPDFLoader,
    BSHTMLLoader,
    TextLoader
)
from langchain_core.documents import Document

def load_documents(directory_path: str):
    """
    Load documents from a directory based on their extensions.
    Supports .md, .pdf, .html, .json, .yaml
    """
    documents = []
    if not os.path.exists(directory_path):
        return documents

    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            ext = Path(file_path).suffix.lower()
            
            try:
                if ext == ".pdf":
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())
                elif ext in [".html", ".htm"]:
                    loader = BSHTMLLoader(file_path)
                    documents.extend(loader.load())
                elif ext in [".md", ".txt"]:
                    loader = TextLoader(file_path, encoding='utf-8')
                    documents.extend(loader.load())
                elif ext == ".json":
                    documents.extend(load_json_swagger(file_path))
                elif ext in [".yaml", ".yml"]:
                    documents.extend(load_yaml_swagger(file_path))
                else:
                    print(f"Unsupported file type skipped: {file_path}")
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")
                
    return documents

def load_json_swagger(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            content = json.dumps(data, indent=2)
            return [Document(page_content=content, metadata={"source": file_path, "type": "swagger-json"})]
    except Exception as e:
        print(f"Failed to parse JSON {file_path}: {e}")
        return []

def load_yaml_swagger(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            content = yaml.dump(data)
            return [Document(page_content=content, metadata={"source": file_path, "type": "swagger-yaml"})]
    except Exception as e:
        print(f"Failed to parse YAML {file_path}: {e}")
        return []
