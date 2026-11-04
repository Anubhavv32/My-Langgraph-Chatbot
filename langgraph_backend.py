from langgraph.graph import StateGraph, START, END;
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated;
from dotenv import load_dotenv;
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver

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

checkpointer = MemorySaver()
graph = StateGraph(ChatState)

#add node
graph.add_node('chat_node', chat_node)

#add edge
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

thread_id = 1
config = {'configurable': {'thread_id': thread_id}}

# while True:
#     user_messages = input('Type here: ')
#     print("User: ", user_messages)

#     if user_messages.strip().lower() in ['exit', 'bye', 'quit']:
#         break
#     response = bot.invoke({'messages': [HumanMessage(content=user_messages)]}, config=config)
#     print('AI: ', response['messages'][-1].content, '\n')