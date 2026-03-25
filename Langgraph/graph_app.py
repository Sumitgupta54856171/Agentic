from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt.chat_agent_executor import AgentState
import  operator



def mock_llm(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "hello world"}]}

graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()

print(graph.invoke({"messages": [{"role": "user", "content": "hi!"}]}))

class Agent:
    def __init__(self,model,tools,system=""):
        self.system=system
        graph=StateGraph(AgentState)


