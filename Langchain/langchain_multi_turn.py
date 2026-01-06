# from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기

# client = OpenAI(api_key=api_key)
llm = ChatOpenAI(model="gpt-4o-mini")   # ← (모델 지정)

# def get_ai_response(messages):
#     response = client.chat.completions.create(
#         model="gpt-4o",            # 모델 선택
#         messages=messages,         # 대화 히스토리 전달
#         temperature=0.7,           # 창의성 조절
#         max_tokens=200,            # 생성할 최대 토큰 수
#         top_p=1                    # nucleus sampling
#     )
#     return response.choices[0].message.content  # 생성된 내용 반환

messages = [
    #{ "role": "system", "content": "너는 AI 비서로서 대화를 도와줘." }
     SystemMessage("너는 AI 비서로서 대화를 도와줘.")
]

while True:
    user_input = input("사용자: ")   # 사용자 입력 받기
    if user_input == "exit":        # 사용자가 종료를 원하면 확인
        break

    messages.append(
        #{ "role": "user", "content": user_input }
         HumanMessage(content=user_input)
    )

    # ai_response = get_ai_response(messages)
    ai_response = llm.invoke(messages)

    messages.append(
        #{ "role": "assistant", "content": ai_response }
         AIMessage
    )

    print("AI: " + ai_response.content)  # AI 응답 출력
