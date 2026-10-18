import os
from dotenv import load_dotenv

import hashlib
import json
from pathlib import Path
import pandas as pd
import pypdf

from pinecone import Pinecone,ServerlessSpec
from langchain_openai import AzureChatOpenAI,AzureOpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter,RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from openai import AzureOpenAI


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
EMBEDDINGS_MODEL_MODE = os.getenv("EMBEDDINGS_MODEL_MODE","local").strip().upper()

if EMBEDDINGS_MODEL_MODE == "OPENAI":
    print("MODE : cloud openAI embedding")

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT","text-embedding-3-small"),
        openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
    )
    INDEX_NAME = 'fde-sop-index-openai'
    TARGET_DIMENSION = 1536
    try :
        vec = embeddings.embed_query('test')
        print(f"CONNECTED : {len(vec)}")
    except Exception as e:
        print(f"azure openai connection failed : {e}")
    
else:
    print("MODE : local embedding")
    
    local_model_target = os.getenv("LOCAL_EMBEDDING_MODEL")
    embeddings = HuggingFaceEmbeddings(
        model_name = local_model_target ,
        model_kwargs={"device":"cpu"}
    )
    INDEX_NAME = 'fde-sop-index-openai'
    TARGET_DIMENSION =1024
    
#pinecone
print("connecting to Pinecone ....")
pc = Pinecone(api_key=PINECONE_API_KEY)

existing_indexes = pc.list_indexes().names()

print(existing_indexes)


    
    
