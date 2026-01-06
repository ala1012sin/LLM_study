# from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory, BaseChatMessageHistory

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")   # ← (모델 지정)
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

with_message_history = RunnableWithMessageHistory(llm, get_session_history)

config = {"configurable": {"session_id": "abc2"}}

response = with_message_history.invoke(
    [HumanMessage(content="안녕? 난 이성용이야")],
    config=config
)
print(response.content)

response = with_message_history.invoke(
    [HumanMessage(content="내 이름은 뭐야?")],
    config=config
)
print(response.content)

response = with_message_history.invoke(
    [HumanMessage(content="오늘 날씨 어때?")],
    config=config
)
print(response.content)

response = with_message_history.invoke(
    [HumanMessage(content="내 국적을 맞춰보고 해당 나라의 국가를 불러줘")],
    config=config
)
print(response.content)

for i in with_message_history.stream(
    [HumanMessage(content="내 국적을 맞춰보고 해당 나라의 국가를 불러줘")],
    config=config
):
    print(i.content, end="|")