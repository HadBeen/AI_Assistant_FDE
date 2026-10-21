import os

from .state import AgentState
from src.agent_tools import fde_tools
from src.utils import llm_model_mode


AGENT_LLM_SETTING = os.getenv("AGENT_LLM_SETTING", "OLLAMA").strip().upper()

llm = llm_model_mode(AGENT_LLM_SETTING)

llm_with_tools = llm.bind_tools(fde_tools)

def reasoning_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}
