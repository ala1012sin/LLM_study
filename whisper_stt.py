import pandas as pd
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


def whisper_stt(audi_file_path: str, output_file_path: str = './output.csv'):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
        return_timestamps=True,   # ②
        chunk_length_s=10,        # ③
        stride_length_s=2
    )
    result = pipe(audi_file_path)
    df = whisper_to_dataframe(result, output_file_path)
    return result, df

def whisper_to_dataframe(result, output_file_path):

    segments = result.get("segments") or result.get("chunks")
    data = []

    if segments:
        for seg in segments:
            start = seg.get('start') or (seg.get('timestamp', [None, None])[0] if 'timestamp' in seg else None)
            end = seg.get('end') or (seg.get('timestamp', [None, None])[1] if 'timestamp' in seg else None)
            text = seg.get('text', '')
            data.append({'start': start, 'end': end, 'text': text})
    else:
        # segments가 없을 때 text만 기록
        data.append({'start': None, 'end': None, 'text': result.get('text', '')})

    df = pd.DataFrame(data)
    df.to_csv(output_file_path, index=False)
    return df

if __name__ == "__main__":
    result, df = whisper_stt(
     "C:\LLM\싼기타_비싼기타.mp3",
     "C:\LLM\싼기타_비싼기타.csv"   
    )
    print(df)
    