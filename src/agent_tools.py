import os
from dotenv import load_dotenv

import urllib
import requests
from pathlib import Path
from sqlalchemy import create_engine,text

from langchain_core.tools import tool
from langchain_openai import AzureOpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
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
    
vectore_store = PineconeVectorStore(index_name=INDEX_NAME,embedding=embeddings)
retriever = vectore_store.as_retriever(search_kwargs={"k":2})


# fde agents tools

@tool
def query_telemetry_db(sql_query:str) -> str:
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

    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

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

        


@tool
def fetch_corridor_conditions(latitude: float, longitude: float) -> str:
    """
    Fetches real-time weather and corridor conditions from a live REST API for given GPS coordinates.
    Provides temperature, wind speed, and computed corridor congestion index.
    """
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        # print(url)
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        payload = response.json().get("current_weather", {})
        temp = payload.get("temperature", "N/A")
        wind = payload.get("windspeed", 0.0)
        
        congestion_index = 8.5 if wind > 10.0 else 2.5
        status_note = "High Transit Disruption" if wind > 10.0 else "Corridor Normal"
        
        return (
            f"--- LIVE CORRIDOR TELEMETRY ---\n"
            f"Target GPS: {latitude}, {longitude}\n"
            f"External Temp: {temp}°C | Wind Speed: {wind} km/h\n"
            f"Corridor Risk: {status_note} (Congestion Index: {congestion_index}/10)\n"
            f"-------------------------------"
        )
    except Exception as e:
        return f"Corridor API Communication Failure: {str(e)}"
    
@tool
def search_compliance_sop(query: str) -> str:
    """
    Searches enterprise Standard Operating Procedures (SOPs) indexed in the Pinecone Vector DB.
    Use this to retrieve regulatory thresholds, cold-chain breach mitigations, and rerouting rules.
    """
    try:
        matched_docs = retriever.invoke(query)
        if not matched_docs:
            return "No matching compliance clauses found."
            
        formatted_context = "\n\n".join(
            [f"[Source: {doc.metadata.get('source_file', 'SOP')} | Format: {doc.metadata.get('file_format', 'RAW')}]\n{doc.page_content}" for doc in matched_docs]
        )
        return f"--- COMPLIANCE SOP CONTEXT ---\n{formatted_context}\n------------------------------"
    except Exception as e:
        return f"Vector Store Retrieval Error: {str(e)}"
    
    
if __name__ == "__main__":
    # print("\n--- Testing Tool 1: SQL Telemetry View ---")
    # print(query_telemetry_db.invoke("SELECT TOP 2 Latitude, Longitude, Current_Temperature_C FROM FDE_VIEWS.VW_ACTIVE_FLEET"))
    
    print("\n--- Testing Tool 2: Live Corridor API ---")
    print(fetch_corridor_conditions.invoke({"latitude": 43.77, "longitude": -118.19}))
    
    # print("\n--- Testing Tool 3: Pinecone Vector Retrieval ---")
    # print(search_compliance_sop.invoke("What are the temperature rules for fresh perishables?"))



