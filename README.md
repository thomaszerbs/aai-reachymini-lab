# Reachy Mini Ollama Chat App

This app integrates Reachy Mini with Ollama LLM to create an interactive chat experience. While Ollama generates responses, Reachy Mini performs random expressive movements in the Mujoco simulation.

## 🚀 Quick Start

1. **Install Ollama** and pull a model
2. **Install Reachy Mini SDK**
3. **Install Python dependencies**
4. **Run the app**

## 📋 Features

### Original Version (app.py)
1. **Python-based app** with clean object-oriented design
2. **Local Ollama integration** using the qwen3:0.6b model (configurable)
3. **Reachy Mini SDK control** during Ollama responses
4. **Predefined action functions** for easy control of robot movements
5. **Interactive chat interface** with commands and help system
6. **Streaming responses** with real-time robot movements

### Enhanced Versions

#### emo_v1.py - Basic Emotion Controller
- 4 basic emotion types (positive, negative, question, activity)
- Custom coded movements
- Simple API design

#### emo_v2.py - Enhanced with Recorded Moves
- **Recorded moves library** (19 pre-recorded movements)
- **Enhanced emotion detection** with intensity (high/medium/low)
- **Emoji support** 😊😢🤔💃
- **Debug mode** for troubleshooting
- **Fallback system** for reliability

#### emo_v3.py - Parallel Action Execution
- **All emo_v2 features**
- **Parallel actions** during text streaming
- **Early emotion analysis** (10+ characters)
- **Non-blocking execution**
- **More responsive** user experience

#### emo_v4.py - Text-to-Speech Integration
- **All emo_v3 features**
- **Cross-platform TTS** (macOS, Windows, Linux)
- **Multi-backend support** (Piper, System.Speech, eSpeak, gTTS)
- **Emotional voice modulation** (pitch, speed, volume per emotion)
- **Lip-sync simulation** with antenna movements
- **Complete sentence speaking** (not truncated)
- **Automatic platform detection**

### Version Comparison
See `VERSION_COMPARISON.md` for detailed feature comparison.

## 🔧 Installation & Setup

### 1. Install Ollama

Refer to https://github.com/ollama/ollama

#### macOS/Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Start Ollama and pull a model:
```bash
# Start Ollama server (in a separate terminal)
ollama serve

# In another terminal, pull a model
ollama pull qwen3:0.6b  # Lightweight model (recommended)
```

### 2. Create the workspace
```bash
# Create the workspace
mkdir reachy_mini_chat
cd reachy_mini_chat

# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
```

Do the following steps in this venv.

### 3. Install Reachy Mini SDK with Simulation
The app requires the Reachy Mini SDK. Choose the installation method that fits your setup:
Refering to https://github.com/pollen-robotics/reachy_mini

```bash
pip install "reachy-mini[mujoco]"
```

### 3. Install Python Dependencies
```bash
cd /path/to/reachy_mini_ollama_chat
pip install -r requirements.txt

# For emo_v4.py TTS features, additional packages may be needed:
# macOS: Built-in 'say' command works out of the box
# Windows: pip install pyttsx3 (optional)
# Linux: sudo apt-get install espeak ffmpeg (or equivalent)
```

## 🎮 Usage

### Start the Reachy Mini by simulation
Open the simulation environment with Reachy Mini:
```bash
reachy-mini-daemon --sim --scene minimal
```

### Basic Interactive Chat
Run the original interactive chat session:
```bash
python app.py
```

### Enhanced Versions (Recommended)
We have 4 enhanced versions with increasing capabilities:

#### emo_v2.py - Enhanced with Recorded Moves
```bash
python emo_v2.py --chat
python emo_v2.py --test-moves
python emo_v2.py --chat --debug
```

#### emo_v3.py - Parallel Actions During Text
```bash
python emo_v3.py --chat
python emo_v3.py --test-moves
python emo_v3.py --chat --debug
```

#### emo_v4.py - Text-to-Speech Integration (Cross-Platform)
```bash
python emo_v4.py --chat
python emo_v4.py --test-tts
python emo_v4.py --test-moves
python emo_v4.py --chat --no-tts
python emo_v4.py --chat --debug
```

### Test All Versions
```bash
python test_all_versions.py
```

### Run Script (Optional)
Make the run script executable and adjust the VENV_PATH if needed:
```bash
chmod +x run_app.sh
# Edit run_app.sh to point to your virtual environment
./run_app.sh
```

## 📖 Available Commands in Interactive Mode

- `/exit` or `/quit` - Exit the chat
- `/help` - Show help information
- `/actions` - List available Reachy Mini actions
- `/do <action_name>` - Perform a specific action

## 🤖 Available Actions

The app includes 10 predefined actions:
1. `nod` - Nod head up and down
2. `shake` - Shake head left and right
3. `look_left` - Look to the left
4. `look_right` - Look to the right
5. `look_up` - Look up
6. `look_down` - Look down
7. `antennas_wiggle` - Wiggle antennas
8. `circle_head` - Move head in a circular pattern
9. `excited` - Excited movement with quick nods
10. `thoughtful` - Thoughtful movement with slow nods

## ⚙️ How It Works

1. When you send a message to Ollama, the app starts a background thread that performs random Reachy Mini actions.
2. The actions continue while Ollama streams its response.
3. When the response is complete, the actions stop.
4. You can also manually trigger actions using the `/do` command.

## 💻 Example Session

```
$ python app.py
============================================================
🤖 Reachy Mini Ollama Chat
============================================================
Model: qwen3:0.6b
Ollama URL: http://localhost:11434

Commands:
  /exit or /quit - Exit the chat
  /help - Show this help
  /actions - List available actions
  /do <action> - Perform a specific action

Start chatting! (Reachy Mini will move during responses)
============================================================
Connecting to Reachy Mini...
Connected to Reachy Mini!

🧑 You: Hello, how are you?

🤖 Sending to Ollama (qwen3:0.6b): Hello, how are you?...
🤖 Ollama Response (streaming): I'm doing well, thank you for asking! How can I assist you today?
Performing action: nod for 2.4s
Performing action: look_left for 2.1s

🧑 You: /actions

🤖 Available Reachy Mini actions:
  - nod
  - shake
  - look_left
  - look_right
  - look_up
  - look_down
  - antennas_wiggle
  - circle_head
  - excited
  - thoughtful

Use: /do <action_name> to perform an action
```

## 🔍 Testing Your Setup

```bash
# Test Python dependencies
python test_simple.py

# Test without Ollama (just Reachy Mini)
python app.py --test

# Full interactive chat
python app.py

# See usage examples
python example_usage.py
```

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named 'reachy_mini'"
The Reachy Mini SDK is not installed or not in Python path.

**Solution:**
```bash
# Install the SDK
cd /path/to/reachy_mini
pip install -e .

# Or add to Python path
export PYTHONPATH=/path/to/reachy_mini:$PYTHONPATH
```

### "ConnectionError" to Ollama
Ollama is not running.

**Solution:**
```bash
# Start Ollama in a separate terminal
ollama serve

# Check if it's running
curl http://localhost:11434/api/tags
```

### "Could not connect to Reachy Mini"
The Mujoco simulation is not running or SDK can't connect.

**Solution:**
- Start the Reachy Mini simulation
- Check that the SDK is properly configured
- Try test mode: `python app.py --test`

### "AssertionError: Unknown task UUID." (Callback errors)
These are internal SDK errors that usually don't affect functionality.

**Solution:**
- Ignore if the app still works
- Try restarting the simulation
- Check SDK documentation for updates

### General Tips:
- Make sure Ollama is running (`ollama serve`)
- Verify Reachy Mini simulation is active
- Check Python dependencies: `pip install requests numpy scipy`
- Ensure you're in the correct Python environment

## 🏗️ Code Structure

- `ReachyOllamaController` class - Main controller class
- `actions` dictionary - Maps action names to function methods
- `chat_with_ollama()` - Handles Ollama API communication
- `interactive_chat()` - Runs the interactive chat loop
- Predefined action functions - Individual movement patterns

## 📁 Directory Structure

```
reachy_mini_ollama_chat/
├── app.py              # Main application
├── README.md           # Documentation (this file)
├── requirements.txt    # Python dependencies
├── test_simple.py      # Basic tests
├── example_usage.py    # Usage examples
└── run_app.sh         # Convenience script (adjust paths if needed)
```

## 🔧 Development & Extensibility

The app is designed to be easily extended:

### Adding New Actions
1. Define a new method in the `ReachyOllamaController` class
2. Add it to the `actions` dictionary in `__init__`
3. Test with `/do <new_action_name>`

### Modifying Behavior
- Adjust movement parameters in action functions
- Customize the Ollama prompt and parameters in `chat_with_ollama()`
- Change the random action selection logic in `continuous_random_actions()`

### Testing Changes
```bash
# Run basic tests
python test_simple.py

# Test robot integration
python app.py --test
```

## 🌐 Platform Compatibility

### Cross-Platform Support
`emo_v4.py` provides **true cross-platform compatibility** for macOS, Windows, and Linux:

#### macOS
- **TTS**: Built-in `say` command (works out of the box)
- **Audio**: `afplay` (built-in)
- **Best for**: Quick setup, high quality

#### Windows  
- **TTS**: `.NET System.Speech` (built-in) or `pyttsx3` (installable)
- **Audio**: `winsound` (built-in)
- **Best for**: Corporate environments, .NET integration

#### Linux
- **TTS**: `eSpeak` (installable), `gTTS` (Python, internet required)
- **Audio**: `aplay` (ALSA), `paplay` (PulseAudio), `ffplay` (FFmpeg)
- **Best for**: Servers, open source environments

### Automatic Detection
The code automatically detects your platform and chooses the best available options:
```bash
python emo_v4.py --test-tts --debug
# Shows which TTS backend and audio player are being used
```

### Platform-Specific Installation
See `PLATFORM_COMPATIBILITY.md` for detailed installation instructions for each platform.

## 📄 License

This app is built on top of the Reachy Mini SDK. See the respective licenses for Ollama and Reachy Mini components.

## 🤝 Contributing

Feel free to fork and modify the app for your needs. The code is structured to be easily extensible with new actions and features.

## 🆘 Getting Help

- Review the example usage: `python example_usage.py`
- Test components individually:
  - Ollama: `curl http://localhost:11434/api/tags`
  - Reachy Mini: Run test mode `python app.py --test`
  - Python dependencies: `python test_simple.py`

Read the code documentation in each file
