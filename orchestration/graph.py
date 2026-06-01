import os
from dotenv import load_dotenv
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver  # <-- MemorySaver imported
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Import our custom pieces!
from state import TelecomState
from adk_remote_client import ask_network_agent, ask_billing_agent
from crew_nodes import generate_customer_response
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llamaindex_rag.document_rag import get_policy_answer
from llamaindex_rag.sql_semantic_search import get_sql_analytics_answer

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def supervisor_router(state: TelecomState):
    # <-- MODIFIED: Smarter routing prompt to catch account IDs and outages
    prompt = f"""
    You are a telecom routing supervisor. Read the user's message and output EXACTLY ONE of these words based on their intent:
    - 'network': if they mention dropped calls, outages, 5G issues, or checking a specific tower.
    - 'billing': if they mention accounts, account IDs (like CUST-), duplicate charges, balances, refunds, or credits.
    - 'policy': if they ask general questions about SLA, roaming rules, or general guidelines.
    - 'analytics': if they ask for historical data, regional outage counts, or broad database statistics.
    
    User Message: "{state['customer_message']}"
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    decision = response.content.strip().lower()
    if decision not in ['network', 'billing', 'policy', 'analytics']:
        decision = 'policy' 
        
    return {"route_decision": decision}

def call_network_worker(state: TelecomState):
    print("\n[Supervisor] Routing to Network Diagnostics ADK...")
    raw_data = ask_network_agent(state['customer_message'])
    print(f"\n[DEBUG - RAW NETWORK DATA]: {raw_data}\n")
    return {"raw_worker_data": f"Network ADK Output: {raw_data}"}

def call_billing_worker(state: TelecomState):
    print("\n[Supervisor] Routing to Billing Resolution ADK...")
    raw_data = ask_billing_agent(state['customer_message'])
    print(f"\n[DEBUG - RAW WORKER DATA]: {raw_data}\n")
    return {"raw_worker_data": f"Billing ADK Output: {raw_data}"}

def call_policy_worker(state: TelecomState):
    print("\n[Supervisor] Routing to LlamaIndex Policy RAG...")
    raw_data = get_policy_answer(state['customer_message'])
    return {"raw_worker_data": f"Policy RAG Output: {raw_data}"}

def call_analytics_worker(state: TelecomState):
    print("\n[Supervisor] Routing to LlamaIndex Semantic SQL...")
    raw_data = get_sql_analytics_answer(state['customer_message'])
    return {"raw_worker_data": f"SQL Analytics Output: {raw_data}"}

def call_crew_communications(state: TelecomState):
    print("\n[Supervisor] Worker finished. Sending raw data to CrewAI for formatting...")
    final_text = generate_customer_response(
        user_query=state['customer_message'], 
        agent_context=state['raw_worker_data']
    )
    return {"final_email": final_text}

def route_to_worker(state: TelecomState) -> Literal["network_node", "billing_node", "policy_node", "analytics_node"]:
    decision = state['route_decision']
    if decision == 'network': return "network_node"
    if decision == 'billing': return "billing_node"
    if decision == 'analytics': return "analytics_node"
    return "policy_node"

workflow = StateGraph(TelecomState)

workflow.add_node("supervisor", supervisor_router)
workflow.add_node("network_node", call_network_worker)
workflow.add_node("billing_node", call_billing_worker)
workflow.add_node("policy_node", call_policy_worker)
workflow.add_node("analytics_node", call_analytics_worker)
workflow.add_node("crew_communications", call_crew_communications)
workflow.set_entry_point("supervisor")
workflow.add_conditional_edges("supervisor", route_to_worker)
workflow.add_edge("network_node", "crew_communications")
workflow.add_edge("billing_node", "crew_communications")
workflow.add_edge("policy_node", "crew_communications")
workflow.add_edge("analytics_node", "crew_communications")

workflow.add_edge("crew_communications", END)

# <-- Checkpointer initialization
memory = MemorySaver()

# <-- App compilation includes checkpointer
app = workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    print("Initializing Autonomous Telecom System...")
    test_message = "My 5G connection has been dropping constantly. Can you run diagnostics on tower TWR-104?"
    print(f"\nUser: {test_message}")
    
    # <-- Config block for local terminal testing
    config = {"configurable": {"thread_id": "test_session_123"}}
    final_state = app.invoke({"customer_message": test_message}, config=config)
    
    print("\n" + "="*50)
    print("FINAL OUTPUT DELIVERED TO USER:")
    print("="*50)
    print(final_state['final_email'])