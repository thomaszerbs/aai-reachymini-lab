#source .venv/bin/activate

python emo_v9.py --piper-model ./models/zh_CN-huayan-medium.onnx --model qwen3.5:9b --asr --gentle
