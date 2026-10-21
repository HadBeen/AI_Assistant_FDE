import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import  SystemMessage

from src.utils import setup_env
from src.graph.workflow import fde_agent


project_root = setup_env()

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
load_dotenv(project_root / ".env")

AGENT_LLM_SETTING = os.getenv("AGENT_LLM_SETTING", "OLLAMA").strip().upper()
print(AGENT_LLM_SETTING)



if __name__ == "__main__":
    print("\n" + "="*55)
    print("🚀 FDE Supply Chain Orchestrator State Machine Online")
    print(f"   Configured Execution: [LLM: {AGENT_LLM_SETTING}] -> [Embeddings: {os.getenv('Embeddings_model', 'LOCAL')}]")
    print("="*55 + "\n")
    
    # Load the business-structured system prompt from the external file
    prompt_path = project_root / "src" / "prompts" / "system_prompt.txt"
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_instructions = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {prompt_path}")
        system_instructions = "You are a helpful AI assistant." # Basic fallback

    system_prompt = SystemMessage(content=system_instructions)
    
    thread_config = {"configurable": {"thread_id": "production_test_1"}}
    fde_agent.invoke({"messages": [system_prompt]}, config=thread_config)
    
    while True:
        user_input = input("\nDispatcher > ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        events = fde_agent.stream({"messages": [("user", user_input)]}, config=thread_config, stream_mode="updates")
        for event in events:
            for node_name, node_state in event.items():
                if node_name == "tools":
                    print("   [System] 🔄 Retrieving external data elements via ToolNode...")
                elif node_name == "reasoner":
                    latest_msg = node_state["messages"][-1]
                    if latest_msg.content:
                        print(f"\n🤖 FDE Agent:\n{latest_msg.content}")