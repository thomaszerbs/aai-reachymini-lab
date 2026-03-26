1. How to isntall ROCm on Ubuntu Ryzen Platform?

Refer to [install-rocm.md](./install-rocm.md). 

2. How to install Ollama?

For linux: https://ollama.com/download/linux

```
curl -fsSL https://ollama.com/install.sh | sh
```

Verify it run on the iGPU

```
ollama run qwen3:0.6b "hi" --think=false --verbose ; ollama ps
```

3. 
