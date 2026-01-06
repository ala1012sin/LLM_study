import pymupdf
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

def summarize_txt(path: str):
    client = OpenAI(api_key = api_key)
    
    with open(path, 'r', encoding = 'utf-8') as f:
        input_text = f.read()
        
    prompt = f"""
    다음은 논문의 본문입니다. 아래 내용을 바탕으로 핵심 내용을 논문 요약 형식으로 정리하세요.
    - 연구 목적
    - 연구 방법
    - 주요 결과
    - 결론 및 시사점
    
    --- 본문 ---
    {input_text[:15000]}"""
    
    response = client.chat.completions.create(
        model="gpt-4o",              
        temperature=0.9,            
        messages = [
            {"role": "system", "content": "너는 전문 논문 요약가이다. 내용을 간결하게 정리하라."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content
    
def mk_txt():
    path = "과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원 시스템 설계 및 구축.pdf"

    doc = pymupdf.open(path) 


    full = " "

    header_height = 80
    footer_height = 80

    for page in doc:
        rect = page.rect
        header = page.get_text(clip = (0,0, rect.width, header_height))
        footer = page.get_text(clip = (0, rect.height - footer_height, rect.width, rect.height))
        text = page.get_text(clip = (0, header_height, rect.width, rect.height - footer_height))
        full += text
        
    pdf_file_name = os.path.basename(path)
    pdf_file_name = os.path.splitext(pdf_file_name)[0]


    txt_file_path = f"{pdf_file_name}.txt"
    with open(txt_file_path, 'w', encoding = 'utf-8') as f:
        f.write(full)
            
            
            
mk_txt()
path = "과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원 시스템 설계 및 구축.txt"
summary = summarize_txt(path)
with open("요약본.txt", 'w', encoding = 'utf-8') as f:
        f.write(summary)