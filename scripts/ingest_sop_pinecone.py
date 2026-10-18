import os
from dotenv import load_dotenv

import hashlib
import json
from pathlib import Path
import pandas as pd
import pypdf

from pinecone import Pinecone,ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter,RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# disable windowns symlink warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"]="true"

# path set up
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
load_dotenv(project_root/".env")


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE API KEY in .env file")

# clean data production 
cache_dir = project_root/'data'/'cache'
cache_dir.mkdir(parents=True,exist_ok=True)
HASH_CACHE_FILE = cache_dir/"ingestion_hash_cache.json"

hash_cache = {}

if HASH_CACHE_FILE.exists():
    try:
        with open(HASH_CACHE_FILE,"r") as f :
            hash_cache = json.load(f)
    except Exception:
        hash_cache = {}
        
# embedding config
EMBEDDINGS_MODEL_SETTINGS = os.getenv("embedding_model","local").strip().upper()

if EMBEDDINGS_MODEL_SETTINGS == "OPENAI":
    print("MODE : cloud openAI embedding")
    embeddings = OpenAIEmbeddings()
    INDEX_NAME = 'fde-sop-index-openai'
    TARGET_DIMENSION = 2
else:
    print("MODE : local embedding")
    embeddings = OpenAIEmbeddings()
    INDEX_NAME = 'fde-sop-index-openai'
    TARGET_DIMENSION = 2
    
