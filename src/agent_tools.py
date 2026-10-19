import os
from dotenv import load_dotenv

import urllib
import requests
from pathlib import Path
from sqlalchemy import create_engine,text

from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings ,AzureOpenAIEmbeddings
from langchain_pinecone import PineconeSparseVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

# set up env
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

load_dotenv(dotenv_path=project_root/".env")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
EMBEDDINGS_MODEL_MODE = os.getenv("EMBEDDINGS_MODEL_MODE")

db_host = os.getenv("SQL_HOST")
db_port = os.getenv("SQL_PORT")
db_user = os.getenv("SQL_AGENT_USER")
db_password = os.getenv("SQL_AGENT_PASSWORD")

if not PINECONE_API_KEY:
    raise ValueError("No pinecone api key availale in .ENV")


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
    
vectore_store = PineconeSparseVectorStore(index_name=INDEX_NAME,embedding=embeddings)
retriever = vectore_store.as_retriever(search_kwargs={"k":2})


# fde agents tools

@tool
def query_telemetry_bd(sql_query:str) -> str:
    '''
    execute a sql select query in dfe_views 
    '''

    connection_string =(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={db_host},{db_port};"
            f"DATABASE=master;"
            f"UID={db_user};"
            f"PWD={db_password};"
            f"Encrypt=no;"
            f"TrustServerCertificate=yes;"
            )
    params = urllib.parse.quote_plus(connection_string)

    engine = create_engine(f"mssql+pyobdc:///?odbc_connect={params}")

    try:
        if not sql_query.strip().upper().startswith("SELECT"):
            return "SECURITY BLOCK: only SELECT operations are allowed on this"

        with engine.connect() as conn:
            cursor = conn.execute(text(sql_query))
            colums = list(cursor.keys())
            rows = cursor.fetchmany(10)

            if not rows:
                return " no records matched the query"
            
            formatted_output = f"columns : {','.join(colums)}\n"
            for row in rows:
                formatted_output += str(tuple(row))+'\n'

            return formatted_output
    
    except Exception as e:
        return f"Detected errors : {str(e)}"

        


    




