import os

from langchain_openai import AzureChatOpenAI,AzureOpenAIEmbeddings
from langchain_core.messages import SystemMessage,HumanMessage
from langchain_community.chat_models import ChatOllama

from src.graph.state import AgentState
from src.agent_tools import query_telemetry_db, fetch_corridor_conditions, search_compliance_sop
from src.utils import llm_model_mode





AGENT_LLM_SETTING = os.getenv("Agent_llm", "OLLAMA").strip().upper()

llm = llm_model_mode()

fde_tools = [query_telemetry_db, fetch_corridor_conditions, search_compliance_sop]
llm_with_tools = llm.bind_tools(fde_tools)

def reasoning_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}
