import os
from dotenv import load_dotenv

import urllib
import requests
from pathlib import Path
from sqlalchemy import create_engine,text

from langchain_core.tools import tool
from langchain_pinecone import PineconeVectorStore

from src.utils import embedding_model_mode,setup_env

# set up env
setup_env()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
EMBEDDINGS_MODEL_MODE = os.getenv("EMBEDDINGS_MODEL_MODE")

db_host = os.getenv("SQL_HOST")
db_port = os.getenv("SQL_PORT")
db_user = os.getenv("SQL_AGENT_USER")
db_password = os.getenv("SQL_AGENT_PASSWORD")

if not PINECONE_API_KEY:
    raise ValueError("No pinecone api key availale in .ENV")

embeddings,INDEX_NAME,TARGET_DIMENSION = embedding_model_mode(EMBEDDINGS_MODEL_MODE)    

vectore_store = PineconeVectorStore(index_name=INDEX_NAME,embedding=embeddings)
retriever = vectore_store.as_retriever(search_kwargs={"k":2})

# fde agents tools
_conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={db_host},{db_port};DATABASE=YourDatabase;"
    f"UID={db_user};PWD={db_password};"
    "Encrypt=no;TrustServerCertificate=yes;"
)
engine = create_engine(
    "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(_conn_str)
)


@tool
def query_telemetry_db(sql_query:str) -> str:
 
    """Run one read-only SQL SELECT against the FDE_VIEWS schema (SQL Server T-SQL).
  Returns up to 10 rows. Use TOP, not LIMIT."""
    try:

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
    
    
fde_tools = [query_telemetry_db, fetch_corridor_conditions, search_compliance_sop]


