from langchain_core.tools import tool
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessageChunk
from langchain_core.output_parsers import StrOutputParser
from datetime import datetime
from pydantic import BaseModel, Field
import yfinance as yf
import pytz
import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults




class StockHistoryInput(BaseModel):
    ticker: str = Field(..., title = "주식코드", description="주식 코드(예: 'AAPL')")
    period: str = Field(..., title = "기간", description="주식 데이터 조회 기간(예: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd')")

class SearchInput(BaseModel):
    query: str = Field(..., title = "검색어", description="DuckDuckGo에 사용할 검색어")
    
@tool
def get_current_time(timezone: str, location: str) -> str:
    """현재 시간을 반환하는 함수

    Args:
        timezone (str): 타임존(예: 'Asia/Seoul', 'America/New_York'). 실제 존재해야 함
        location (str): 지역명. 타임존은 모든 지명에 대응되지 않으므로 이후 llm 답변 생성에 사용됨
    """
    tz = pytz.timezone(timezone)
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    location_and_localtime = f"{timezone} ({location}) 현재 시간은 {now} 입니다."
    print(location_and_localtime)
    return location_and_localtime

@tool
def get_yf_stock_info(stock_hist_input: StockHistoryInput):
    """ 주식 정보를 알려주는 함수 """
    stock = yf.Ticker(stock_hist_input.ticker)
    info = stock.info
    print(info)
    return str(info)

@tool
def get_yf_stock_history(stock_hist_input: StockHistoryInput):
    """ 주식 종목의 가격 데이터를 조회하는 함수"""
    stock = yf.Ticker(stock_hist_input.ticker)
    history = stock.history(period=stock_hist_input.period)
    history_md = history.to_markdown()
    print(history_md)
    return history_md

@tool
def get_yf_stock_recommendations(stock_hist_input: StockHistoryInput):
    """ 주식 종목을 추천해주는 함수 """
    stock = yf.Ticker(stock_hist_input.ticker)
    recommendations = stock.recommendations
    recommendations_md = recommendations.to_markdown()
    print(recommendations_md)
    return recommendations_md


@tool
def get_duckduckgo_searching(search_input: SearchInput):
    """사용자가 제공한 검색어로 덕덕고 뉴스 검색을 수행하고 기사 내용을 반환하는 함수"""
    wrapper = DuckDuckGoSearchAPIWrapper(region="kr-kr", time = "w")
    
    search = DuckDuckGoSearchResults(
        api_wrapper=wrapper,
        source = "text",
        results_separator = ';\n'
    )

    docs = search.invoke(search_input.query) 
    print(docs)
    return docs


    
def write_stream(stream, container=None):
    """
    스트림 제너레이터를 소비하며 출력.
    container(예: st.empty())가 있으면 UI에 표시, 없으면 콘솔에 print.
    반환: (누적 텍스트, 최종 AIMessageChunk)
    """
    text = ""
    gathered = None
    for chunk in stream:
        if chunk.content:
            text += chunk.content
            if container is not None:
                container.markdown(text)
            else:
                print(chunk.content, end="")

        if gathered is None:
            gathered = chunk
        else:
            gathered += chunk

    if gathered is None:
        gathered = AIMessageChunk(content="")

    return text, gathered

def ai_response(messages, llm_with_tools, tool_dict, container=None):
    """
    1) 첫 호출(스트리밍)로 tool_calls 포함 응답 수신
    2) tool_calls 실행 후 ToolMessage 추가
    3) 최종 답변을 다시 스트리밍
    반환: (최종 누적 텍스트, 최종 AIMessageChunk)
    """
    first_stream = llm_with_tools.stream(messages)
    _, gathered = write_stream(first_stream, container=None)  

    messages.append(gathered)

    if getattr(gathered, "tool_calls", None):
        for tc in gathered.tool_calls:
            name = tc["name"]
            args = tc["args"]  
            selected_tool = tool_dict[name]
            try:
                tool_output = selected_tool.invoke(args)
            except Exception as e:
                tool_output = f"[{name}] 실행 오류: {e}"

            messages.append(
                ToolMessage(
                    content=str(tool_output),
                    tool_call_id=tc["id"],
                    name=name,
                )
            )

        final_stream = llm_with_tools.stream(messages)
        final_text, final_msg = write_stream(final_stream, container=container)
        return final_text, final_msg
    else:
        if container is not None:
            container.markdown(gathered.content or "(응답이 없습니다)")
        return gathered.content or "", gathered


load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

tools = [get_current_time, get_yf_stock_info, get_yf_stock_history, get_yf_stock_recommendations, get_duckduckgo_searching]
tool_dict = {"get_current_time": get_current_time, "get_yf_stock_info": get_yf_stock_info, 
             "get_yf_stock_history": get_yf_stock_history, "get_yf_stock_recommendations": get_yf_stock_recommendations,
             "get_duckduckgo_searching": get_duckduckgo_searching}

llm_with_tools = llm.bind_tools(tools)


st.title("Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="너는 사용자의 질문에 답변을 하기 위해 tools를 사용할 수 있다.")
    ]

user_input = st.chat_input()
if user_input:
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        holder = st.empty()
        final_text, final_msg = ai_response(st.session_state.messages, llm_with_tools, tool_dict, container=holder)
        st.session_state.messages.append(final_msg)