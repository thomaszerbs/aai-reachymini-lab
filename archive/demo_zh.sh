#source .venv/bin/activate

python emo_v8.py --piper-model ./models/zh_CN-huayan-medium.onnx --model qwen3:0.6b --asr --gentle
