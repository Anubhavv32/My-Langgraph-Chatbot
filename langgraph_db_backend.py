from langgraph.graph import StateGraph, START, END;
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated;
from dotenv import load_dotenv;
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langgraph.graph.message import add_messages
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


load_dotenv()
llm = ChatOpenAI(model="gpt-4o")
def chat_node(state: ChatState):
    # take user query from state
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages': response}

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)
graph = StateGraph(ChatState)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)


#add node
graph.add_node('chat_node', chat_node)

#add edge
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

thread_id = 1
config = {'configurable': {'thread_id': thread_id}}