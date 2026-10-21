from langgraph.graph import StateGraph,END,START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition


from .state import AgentState
from .nodes import reasoning_node
from src.agent_tools import fde_tools

def create_graph ():
    '''
    Constructs and compiles the Langgraph workflow
    returns :
    Compiles graph : runnable object for execution
    '''
    print("Creating FDE Orchestrator...")
    # initialize the graph with state schema
    graph_builder = StateGraph(AgentState)
    # adding the nodes
    graph_builder.add_node("reasoner", reasoning_node)
    graph_builder.add_node("tools", ToolNode(fde_tools))

    graph_builder.add_edge(START, "reasoner")
    graph_builder.add_conditional_edges("reasoner", tools_condition)
    graph_builder.add_edge("tools", "reasoner")

    fde_agent = graph_builder.compile(checkpointer=MemorySaver())
    
    return fde_agent

fde_agent = create_graph()
