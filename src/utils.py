import os
from dotenv import load_dotenv
from pathlib import Path

from langchain_openai import AzureChatOpenAI,AzureOpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama



# path set up
def setup_env() -> Path:
    here = Path(__file__).resolve().parent
    for folder in (here, here.parent):
        env_file = folder / ".env"
        if env_file.exists():
            load_dotenv(env_file, override=True)
            return env_file
    raise FileNotFoundError(f".env not found in {here} or {here.parent}")

def embedding_model_mode(EMBEDDINGS_MODEL_MODE) :

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
        
    return embeddings,INDEX_NAME,TARGET_DIMENSION

def llm_model_mode(AGENT_LLM_SETTING):
    if AGENT_LLM_SETTING == "OPENAI":
        print("LLM Mode: Utilizing Cloud OpenAI Reasoner (gpt-4o)...")
        llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            temperature=0.0
            )

    else:  # FALLBACK / DEFAULT RUNNER MODE
        print("LLM Mode: Local Fallback Activated. Binding Local Ollama (qwen2.5:7b)...")
        llm = ChatOllama(model="qwen2.5:7b", temperature=0, num_predict=1024)    

    return llm