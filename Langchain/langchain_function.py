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


class StockHistoryInput(BaseModel):
    ticker: str = Field(..., title = "주식코드", description="주식 코드(예: 'AAPL')")
    period: str = Field(..., title = "기간", description="주식 데이터 조회 기간(예: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd')")

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



load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

tools = [get_current_time, get_yf_stock_info, get_yf_stock_history, get_yf_stock_recommendations]
tool_dict = {"get_current_time": get_current_time, "get_yf_stock_info": get_yf_stock_info, 
             "get_yf_stock_history": get_yf_stock_history, "get_yf_stock_recommendations": get_yf_stock_recommendations}

llm_with_tools = llm.bind_tools(tools)


messages = [
    SystemMessage(content = "너는 사용자의 질문에 답변을 하기 위해 tools를 사용할 수 있다."),
    HumanMessage(content= "부산 시간은 몇시야"),
]

messages.append(HumanMessage("테슬라는 하루 전에 비해 주가가 올랐나 내렸나?"))


response = llm_with_tools.stream(messages)

is_first = True

for chunk in response:
    print("chunk type: ", type(chunk))
    
    if is_first:
        is_first = False
        gathered = chunk
    else:
        gathered += chunk
    
    print("content:", gathered.content, "tool_call_chunk",  gathered.tool_calls)
    
    
messages.append(gathered)
print(messages)


for tool_call in gathered.tool_calls:
    selected_tool = tool_dict[tool_call["name"]]
    print(tool_call["args"])
    tool_msg = selected_tool.invoke(tool_call)
    messages.append(tool_msg)
    
for i in llm_with_tools.stream(messages):
    print(i.content)
    