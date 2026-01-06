from glob import glob
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
import IPython.display as ipd
import base64

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

with open("quiz_eng.json", "r", encoding="utf-8") as f:
    eng_dic = json.load(f)
    
    
voices = ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shim-mer"]

for q in eng_dic:
    no = q['no']
    quiz = q['eng']
    quiz = quiz.replace("-(1)", "- One.\t")
    quiz = quiz.replace("-(2)", "- Two.\t")
    quiz = quiz.replace("-(3)", "- Three.\t")
    quiz = quiz.replace("-(4)", "- Four.\t")
    
    print(no, quiz)
    
    voice = voices[no % len(voices)]
    
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=f"#{no}. {quiz}",
    )

    response.write_to_file(f"{no}.mp3")

    ipd.Audio("1.mp3")