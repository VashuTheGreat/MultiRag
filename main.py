from langgraph.graph import StateGraph, START, END
from langchain.messages import HumanMessage, SystemMessage
from langchain_core.messages import BaseMessage
from typing import Annotated, List
from typing import TypedDict
from langgraph.graph import add_messages
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from typing import TypedDict
import os
from retreiver_pipeline import get_retreived_docs
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool
import vconsoleprint
from dotenv import load_dotenv

from langgraph.checkpoint.sqlite import SqliteSaver

import sqlite3
import requests

load_dotenv()
conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

llm = ChatGroq(model="llama-3.1-8b-instant")

@tool
def search_tool(query: str):
    """Perform Google search using DuckDuckGo and return top results"""
    search = DuckDuckGoSearchRun()
    return search.invoke(query)

@tool
def retreive_from_docs(query: list):
    """Retrieve relevant information from uploaded documents"""
    if isinstance(query, str):
        query = [query]
    results = []
    for q in query:
        results.extend(get_retreived_docs(q))
    return results

tools = [search_tool, retreive_from_docs]
llm_with_tools = llm.bind_tools(tools)




class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
   
    messages = state["messages"]
    system = SystemMessage(
        content="You are a helpful assistant. Answer clearly and concisely. Always respond strictly in Markdown format."
    )
    response = llm_with_tools.invoke([system,*messages])
    return {"messages": [response]}

tool_node = ToolNode(tools)





graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node')

graph = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)


def load_conversation(thread_id):
    state = graph.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])


if __name__=="__main__":
    config = {"configurable": {"thread_id": "2"}}
    print(graph.invoke({"messages":[HumanMessage(content="what is ml")]},config=config))


