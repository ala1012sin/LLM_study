from glob import glob
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
import base64

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") 
client = OpenAI(api_key=api_key)      

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
def image_quiz(image_paths):
    base64_image = encode_image(image_paths)
    
    quiz_prompt = """
    제공된 이미지를 바탕으로, 다음과 같은 형식으로 퀴즈를 만들어 주세요.
    정답은 (1)~(4) 중 하나만 해당하도록 출제하세요.
    아래는 예시입니다.
    ------ 예시 ------
    Q: 다음 이미지에 대한 설명 중 옳지 않은 것은 무엇인가요?
    (1) 베이커리에서 사람들이 빵을 사는 모습이 담겨 있습니다.
    (2) 앞에 서 있는 사람은 빨간색 셔츠를 입었습니다.
    (3) 기사를 타기 위해 줄을 서 있는 사람들이 있습니다.
    (4) 점원은 노란색 티셔츠를 입었습니다.
    
    정답: (4) 점원은 노란색 티셔츠가 아닌 파란색 티셔츠를 입었습니다.
    (주의: 정답은 (1)~(4) 중 하나만 선택하도록 출제하세요.)
    ------------------
    문제를 다 만든 후 해당 내용을 영어로도 똑같이 만들어줘. 근데 영어문제의 Question은 "Q:" 대신 "Question:" 으로 시작해줘.
    """
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text":quiz_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ],
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",     # 응답 생성에 사용할 모델 지정
        messages=messages   # 대화 기록을 입력으로 전달
    )

    return response.choices[0].message.content

txt = ''
eng_dic = []
no = 1
for g in glob("image/*.jpg"):
    try:
        q = image_quiz(g)
    except Exception as e:
        print(e)
        continue
    
    divider = f'##문제 {no}\n\n'
    print(divider)
    
    txt += divider
    filename = os.path.basename(g)
    txt += f'![image]({filename})\n\n'
    
    print(q)
    
    txt += q + '\n\n--------------------\n\n'
    
    with open('image_quiz.md', 'w', encoding='utf-8') as f:
        f.write(txt)
        
    eng = q.split('Question:')[1].strip().split('Answer:')[0].strip()
    
    eng_dic.append({
        'no': no,
        'eng': eng,
        'img': filename
    })
    
    with open('quiz_eng.json', 'w', encoding='utf-8') as f:
        json.dump(eng_dic, f, ensure_ascii=False, indent=4)
        
    no += 1
    
