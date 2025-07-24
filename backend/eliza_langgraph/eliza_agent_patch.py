
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from web3 import Web3
import json

# Memory layout
class AgentState(TypedDict):
    input: Annotated[str, "User message"]
    agent_data: Annotated[dict, "Parsed proposal info"]
    tx_result: Annotated[str, "Result of smart contract interaction"]

# Parse message into agent_data
def parse_intent(state: AgentState) -> AgentState:
    msg = state["input"].lower()
    if "set ceo" in msg:
        state["agent_data"] = {"action": "setRoles", "ceo": msg.split()[-1]}
    elif "execute agent" in msg:
        parts = msg.split()
        state["agent_data"] = {"action": "executeAgentProposal", "agent": parts[-2], "data": parts[-1]}
    else:
        state["agent_data"] = {"action": "noop"}
    return state

# Mock blockchain logic for testing
def execute_onchain(state: AgentState) -> AgentState:
    d = state["agent_data"]
    if d["action"] == "setRoles":
        state["tx_result"] = f"Simulated setRoles({d['ceo']})"
    elif d["action"] == "executeAgentProposal":
        state["tx_result"] = f"Simulated executeAgentProposal({d['agent']}, {d['data']})"
    else:
        state["tx_result"] = "No action taken"
    return state

# LangGraph pipeline
builder = StateGraph(AgentState)
builder.add_node("parse_intent", parse_intent)
builder.add_node("execute_tx", execute_onchain)
builder.set_entry_point("parse_intent")
builder.add_edge("parse_intent", "execute_tx")
builder.add_edge("execute_tx", END)
eliza_graph = builder.compile()
