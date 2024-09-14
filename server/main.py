from typing import Union
import os
import subprocess

from fastapi import FastAPI
from pydantic import BaseModel
from utils.utils import split_audio

import ffmpeg
from dotenv import load_dotenv
import subprocess

load_dotenv()

app = FastAPI()


class FileItem(BaseModel):
    path: str


@app.get("/")
def read_root():
    return {"Hello": "World"}

# given file id, I need to process
@app.post("/process")
def process(file_item: FileItem):
    print(os.listdir("data/unprocessed"))
    [file_name, file_format] = file_item.path.split('.')

    # Extract audio from video and convert to WAV
    os.makedirs(f'data/processed/{file_name}', exist_ok=True)

    audio_file_path = f'data/processed/{file_name}/{file_name}.wav'
    ffmpeg.input(f'data/unprocessed/{file_item.path}').output(audio_file_path, ar=16000, ac=1, acodec='pcm_s16le').run()

    output_chunk_dir = f"data/processed/{file_name}/{file_name}_chunks"

    split_audio(audio_file_path, output_chunk_dir, 15)

    text_files = []

    for file in os.listdir(output_chunk_dir):
        result = subprocess.run(["./transcribe.sh", output_chunk_dir, file], capture_output=True, text=True)
        text_files.append(f"{output_chunk_dir}/{file}.txt")
        print(result)
    

    return {"Response": "Success"}

# [text1, text3, ...]
# [embed1, embed2, embed, ....]

# [
#     {
#         text: str,
#         timestamp: int,
#         embedding: [...]
#     }
# ]
