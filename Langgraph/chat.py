from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from bs4 import BeautifulSoup
import requests

llm = ChatOllama(model="qwen3.5:latest", temperature=0.5)

@tool
def get_agent_information_tool(url: str):
    """
    Fetches agent information from a given URL.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

agent = create_react_agent(
    model=llm,
    tools=[get_agent_information_tool],
    prompt="you are assistant based on the data provide only detail provide not out of the data you are provide detall"
)

result = agent.invoke({
    "messages": [HumanMessage(content=
                              """
                              "https://docs.langchain.com/oss/python/langchain/agents""explain this in hinglish for understand the thing i am not understand these thing you translatge the thing in hinglish  and only explain the creaete of agent in low cost"
                              """
                              )]
})

print(result["messages"][-1].content)