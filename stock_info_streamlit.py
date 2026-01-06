from gpt_function import get_current_time, tools
from gpt_function import get_yf_stock_info, get_yf_stock_history, get_yf_stock_recommendations

from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import streamlit as st

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def get_ai_response(messages, tools=None, stream = True):
    response = client.chat.completions.create(
        model="gpt-4o",
        stream=stream,
        messages=messages,
        tools= tools,
    )
    if stream:
        for chunk in response:
            yield chunk
    else:
        return response

st.title("Chatbot")
if 'messages' not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "너는 사용자를 도와주는 상담사야"}
    ]
    
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


messages = [
    {"role": "system", "content": "너는 사용자를 도와주는 상담사야"}
]

       
if user_input := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

ai_response = get_ai_response(st.session_state.messages, tools=tools)

content = ''
tool_calls = None
tool_calls_chunks = []
with st.chat_message("assistant").empty():
    for chunk in ai_response:
        content_chunk = chunk.choices[0].delta.content
        if content_chunk:
            print(content_chunk, end='')
            content += content_chunk
            st.markdown(content)
        if chunk.choices[0].delta.tool_calls:
            tool_calls_chunks.append(chunk.choices[0].delta.tool_calls)
        
print('\n==================')
print(content)

print('n================= tl_calls_chunk')
for tool_call_chunk in tool_calls_chunks:
    print(tool_call_chunk)

#ai_message = ai_response.choices[0].message
#print(ai_message)

#tool_calls = ai_message.tool_calls
if tool_calls:
    
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_call_id = tool_call.id
        
        arguments = json.loads(tool_call.function.arguments)

        if tool_name == "get_current_time":
            func_result = get_current_time(timezone = arguments.get("timezone"))
        elif tool_name == "get_yf_stock_info":
            func_result = get_yf_stock_info(ticker = arguments.get("ticker"))
        elif tool_name == "get_yf_stock_history":
            func_result = get_yf_stock_history(ticker = arguments.get("ticker"), period=arguments.get("period"))
        elif tool_name == "get_yf_stock_recommendations":
            func_result = get_yf_stock_recommendations(ticker = arguments.get("ticker"))
            
        st.session_state.messages.append({
                "role": "function",           
                "tool_call_id": tool_call_id, 
                "name": tool_name,
                "content": func_result
            })
        st.session_state.messages.append({"role": "system", "content": "주어진 결과를 바탕으로 답변해줘"})

    ai_response = get_ai_response(st.session_state.messages, tools=tools)
    ai_message = ai_response.choices[0].message

st.session_state.messages.append({"role": "assistant", "content": content})

print("AI:", content)
#st.chat_message("assistant").write(ai_message.content)